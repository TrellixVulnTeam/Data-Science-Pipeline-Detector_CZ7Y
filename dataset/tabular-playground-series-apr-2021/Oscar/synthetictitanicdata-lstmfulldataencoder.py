# Prediction of survival in the Titanic wreck using all data in a textual form
# LSTM encoder of character sequences in data for Titanic survival prediction
import sys
import os
import copy
import math
import subprocess
from collections import OrderedDict
import pandas as pd
import numpy as np
from tqdm import tqdm
import random
import torch
import torch.nn as nn

#Initialise the random seeds
def random_init(**kwargs):
    random.seed(kwargs['seed'])
    np.random.seed(kwargs['seed'])
    torch.manual_seed(kwargs['seed'])
    torch.cuda.manual_seed(kwargs['seed'])
    torch.backends.cudnn.deterministic = True

#Normalise the text and reorder names and surnames
def normalise(text):
    text = text.upper()
    text = ' '.join(text.split(';')[0].split(',')[::-1])+";"+';'.join(text.split(';')[1:])
    text = text.strip()
    text = text.replace("  "," ")
    return text

#Read the existing characters
def read_vocabulary(train_text, **kwargs):
    vocab = dict()
    counts = dict()
    num_words = 0
    for line in train_text:
        line = (list(line.strip()) if kwargs['characters'] else line.strip().split())
        for char in line:
            if char not in vocab:
                vocab[char] = num_words
                counts[char] = 0
                num_words+=1
            counts[char] += 1
    num_words = 0
    vocab2 = dict()
    if not kwargs['characters']:
        for w in vocab:
            if counts[w] >= args['min_count']:
                vocab2[w] = num_words
                num_words += 1
        vocab = vocab2
    for word in [kwargs['start_token'],kwargs['end_token'],kwargs['unk_token']]:
        if word not in vocab:
            vocab[word] = num_words
            num_words += 1
    return vocab

#Load the data into torch tensors
def load_data(text, targets=None, randomize=False, **kwargs):
    num_seq = len(text)
    max_words = max([len((list(line.strip()) if kwargs['characters'] else line.strip().split())) for line in text])+2
    dataset = len(kwargs['vocab'])*torch.ones((max_words,num_seq),dtype=torch.long)
    labels = torch.zeros((num_seq),dtype=torch.uint8)
    idx = 0
    utoken_value = kwargs['vocab'][kwargs['unk_token']]
    for i,line in tqdm(enumerate(text),desc='Allocating data memory',disable=(kwargs['verbose']<2)):
        words = (list(line.strip()) if kwargs['characters'] else line.strip().split())
        if len(words)==0 or words[0] != kwargs['start_token']:
            words.insert(0,kwargs['start_token'])
        if words[-1] != kwargs['end_token']:
            words.append(kwargs['end_token'])
        for jdx,word in enumerate(words):
            dataset[jdx,idx] = kwargs['vocab'].get(word,utoken_value)
        if targets is not None:
            labels[idx] = targets[i]
        idx += 1
        
    if randomize:
        idx = [i for i in range(dataset.shape[1])]
        random.shuffle(idx)
        dataset = dataset[:,idx]
        labels = labels[idx]
    
    return dataset, labels

#Class for a LSTM encoder
class LSTMEncoder(nn.Module):
    def __init__(self, **kwargs):
        
        super(LSTMEncoder, self).__init__()
        #Base variables
        self.vocab = kwargs['vocab']
        self.in_dim = len(self.vocab)
        self.start_token = kwargs['start_token']
        self.end_token = kwargs['end_token']
        self.unk_token = kwargs['unk_token']
        self.characters = kwargs['characters']
        self.embed_dim = kwargs['embedding_size']
        self.hid_dim = kwargs['hidden_size']
        self.n_layers = kwargs['num_layers']
        
        #Define the embedding layer
        self.embed = nn.Embedding(self.in_dim+1,self.embed_dim,padding_idx=self.in_dim)
        #Define the lstm layer
        self.lstm = nn.LSTM(input_size=self.embed_dim,hidden_size=self.hid_dim,num_layers=self.n_layers)
    
    def forward(self, inputs, lengths):
        #Inputs are size (LxBx1)
        #Forward embedding layer
        emb = self.embed(inputs)
        #Embeddings are size (LxBxself.embed_dim)

        #Pack the sequences for GRU
        packed = torch.nn.utils.rnn.pack_padded_sequence(emb, lengths)
        #Forward the GRU
        packed_rec, self.hidden = self.lstm(packed,self.hidden)
        #Unpack the sequences
        rec, _ = torch.nn.utils.rnn.pad_packed_sequence(packed_rec)
        #Hidden outputs are size (LxBxself.hidden_size)
        
        #Get last embeddings
        out = rec[lengths-1,list(range(rec.shape[1])),:]
        #Outputs are size (Bxself.hid_dim)
        
        return out
    
    def init_hidden(self, bsz):
        #Initialise the hidden state
        weight = next(self.parameters())
        self.hidden = (weight.new_zeros(self.n_layers, bsz, self.hid_dim),weight.new_zeros(self.n_layers, bsz, self.hid_dim))

    def detach_hidden(self):
        #Detach the hidden state
        self.hidden=(self.hidden[0].detach(),self.hidden[1].detach())

    def cpu_hidden(self):
        #Set the hidden state to CPU
        self.hidden=(self.hidden[0].detach().cpu(),self.hidden[1].detach().cpu())

#Class for an MLP predictor
class Predictor(nn.Module):
    def __init__(self, **kwargs):
        
        super(Predictor, self).__init__()
        self.hid_dim = kwargs['hidden_size']
        self.out_dim = 2
        #Define the output layer and softmax
        self.linear = nn.Linear(self.hid_dim,self.out_dim)
        self.softmax = nn.LogSoftmax(dim=1)
        
    def forward(self,inputs):
        #Outputs are size (Bxself.hid_dim)
        out = self.softmax(self.linear(inputs))
        return out

#Train one epoch of the model
def train_model(trainset,trainlabels,encoder,predictor,optimizer,criterion,**kwargs):
    trainlen = trainset.shape[1]
    nbatches = math.ceil(trainlen/kwargs['batch_size'])
    total_loss = 0
    total_backs = 0
    with tqdm(total=nbatches,disable=(kwargs['verbose']<2)) as pbar:
        encoder = encoder.train()
        for b in range(nbatches):
            #Data batch
            X = trainset[:,b*kwargs['batch_size']:min(trainlen,(b+1)*kwargs['batch_size'])].clone().long().to(kwargs['device'])
            Y = trainlabels[b*kwargs['batch_size']:min(trainlen,(b+1)*kwargs['batch_size'])].clone().long().to(kwargs['device'])
            mask = torch.clamp(len(kwargs['vocab'])-X,max=1)
            seq_length = torch.sum(mask,dim=0)
            ordered_seq_length, dec_index = seq_length.sort(descending=True)
            max_seq_length = torch.max(seq_length)
            X = X[:,dec_index]
            Y = Y[dec_index]
            X = X[0:max_seq_length]
            #Forward pass
            encoder.init_hidden(X.size(1))
            embeddings = encoder(X,ordered_seq_length.cpu())
            posteriors = predictor(embeddings)
            loss = criterion(posteriors,Y)
            #Backpropagate
            optimizer.zero_grad()
            loss.backward()
            optimizer.step()
            #Estimate the latest loss
            if total_backs == 100:
                total_loss = total_loss*0.99+loss.detach().cpu().numpy()
            else:
                total_loss += loss.detach().cpu().numpy()
                total_backs += 1
            encoder.detach_hidden()
            pbar.set_description(f'Training epoch. Loss {total_loss/(total_backs+1):.2f}')
            pbar.update()
    return total_loss/(total_backs+1)

#Get predictions from a model
def evaluate_model(testset,encoder,predictor,**kwargs):
    testlen = testset.shape[1]
    nbatches = math.ceil(testlen/kwargs['batch_size'])
    predictions = np.zeros((testlen,))
    with torch.no_grad():
        encoder = encoder.eval()
        for b in range(nbatches):
            #Data batch
            X = testset[:,b*kwargs['batch_size']:min(testlen,(b+1)*kwargs['batch_size'])].clone().long().to(kwargs['device'])
            mask = torch.clamp(len(kwargs['vocab'])-X,max=1)
            seq_length = torch.sum(mask,dim=0)
            ordered_seq_length, dec_index = seq_length.sort(descending=True)
            max_seq_length = torch.max(seq_length)
            X = X[:,dec_index]
            X = X[0:max_seq_length]
            #Forward pass
            encoder.init_hidden(X.size(1))
            embeddings = encoder(X,ordered_seq_length.cpu())
            posteriors = predictor(embeddings)
            estimated = posteriors[:,1]#torch.argmax(posteriors,dim=1)
            rev_dec_index = list(range(estimated.shape[0]))
            for i,j in enumerate(dec_index):
                rev_dec_index[j] = i
            predictions[b*kwargs['batch_size']:min(testlen,(b+1)*kwargs['batch_size'])] = np.exp(estimated[rev_dec_index].detach().cpu().numpy())
    return predictions

def compute_results(predictions,labels):
    thresholds = np.arange(1.0,-0.000001,-0.001)
    fpr = []
    tpr = []
    acc = []
    for th in thresholds:
        tp = np.sum((predictions >= th) * labels)
        tn = np.sum((predictions < th) * (1-labels))
        fp = np.sum((predictions >= th) * (1-labels))
        fn = np.sum((predictions < th) * labels)
        tpr.append(tp/(tp+fn))
        fpr.append(fp/(tn+fp))
        acc.append((tp+tn)/(tp+tn+fp+fn))
    results = pd.DataFrame({'thresholds':thresholds,'tpr':tpr,'fpr':fpr,'acc':acc})
    return results
        
#Arguments
args = {
    'input_file': None,
    'vocabulary': None,
    'cv_percentage': 0.1,
    'epochs': 10,
    'batch_size': 32,
    'embedding_size': 16,
    'hidden_size': 64,
    'num_layers': 1,
    'learning_rate': 0.001,
    'seed': 0,
    'start_token': '*s*',
    'end_token': '*\s*',
    'unk_token': '*UNK*',
    'verbose': 1,
    'characters': True,
    'min_count': 1,
    'device': torch.device(('cuda:0' if torch.cuda.is_available() else 'cpu'))
    }

#Read data, split
random_init(**args)
train_data = pd.read_csv('../input/tabular-playground-series-apr-2021/train.csv')
train_data = train_data.sample(frac=1).reset_index(drop=True)
valid_data = train_data.iloc[-int(len(train_data)*args['cv_percentage']):].reset_index(drop=True)
train_data = train_data.iloc[:-int(len(train_data)*args['cv_percentage'])].reset_index(drop=True)
test_data = pd.read_csv('../input/tabular-playground-series-apr-2021/test.csv')
train_targets = np.array(train_data.Survived.values)
valid_targets = np.array(valid_data.Survived.values)

print('Training: {0:d} names. Validation: {1:d}. Evaluation: {2:d} names'.format(len(train_data),len(valid_data),len(test_data)))
print('{0:.2f}% of the training set are survival examples'.format(100*sum(train_targets)/len(train_data)))

columns = ['Name','Pclass','Sex','Age','SibSp','Parch','Ticket','Fare','Cabin','Embarked']
train_text = [normalise(';'.join([str(train_data[c][i]) for c in columns])) for i in range(len(train_data))]
valid_text = [normalise(';'.join([str(valid_data[c][i]) for c in columns])) for i in range(len(valid_data))]
test_text = [normalise(';'.join([str(test_data[c][i]) for c in columns])) for i in range(len(test_data))]
print('Using columns [{0:s}]. Example training sample: {1:s}'.format(', '.join(columns),train_text[0]))

#Make vocabulary and load data
args['vocab'] = read_vocabulary(train_text, **args)
trainset, trainlabels = load_data(train_text, train_targets, randomize=True, **args)
validset, validlabels = load_data(valid_text, valid_targets, randomize=False, **args)
testset, _ = load_data(test_text, None, randomize=False, **args)

#Create model, optimiser and criterion
encoder = LSTMEncoder(**args).to(args['device'])
predictor = Predictor(**args).to(args['device'])
optimizer = torch.optim.Adam(list(encoder.parameters())+list(predictor.parameters()),lr=args['learning_rate'])
criterion = nn.NLLLoss(reduction='mean').to(args['device'])

#Train epochs
best_acc = 0.0
for ep in range(1,args['epochs']+1):
    loss = train_model(trainset,trainlabels,encoder,predictor,optimizer,criterion,**args)
    val_pred = evaluate_model(validset,encoder,predictor,**args)
    test_pred = evaluate_model(testset,encoder,predictor,**args)
    results = compute_results(val_pred,validlabels.numpy())
    th = results.loc[results['acc']==np.max(results['acc'])]['thresholds'].values[0]
    acc = 100*results.loc[results['acc']==np.max(results['acc'])]['acc'].values[0]
    auc = np.trapz(results['tpr'],x=results['fpr'])
    pos = 100*sum(test_pred >= th)/len(test_text)
    if acc >= best_acc:
        best_results = copy.copy(results)
        best_acc = acc
        best_th = th
        test_predictions = copy.copy(test_pred)
    print('Epoch: {0:d} of {1:d}. Training loss: {2:.2f}, validation AUC: {3:.3f}, validation accuracy: {4:.2f}%@{5:.3f}, test survival rate: {6:.2f}%'.format(ep,args['epochs'],loss,auc,acc,th,pos))

#Write results
df_out = pd.DataFrame({'PassengerId': test_data['PassengerId'], 'Survived': (test_predictions >= best_th).astype(int)})       
df_out.to_csv('submission.csv',index=False)