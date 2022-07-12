#! /usr/bin/python3 -OOu
'''
Be careful with the above shebang, which may not work with arguments.
'''

import time

perf_counter_start = time.perf_counter()

import gc
import os
import sys

import pandas as pd
import psutil
from sklearn.base import BaseEstimator, TransformerMixin
from sklearn.cross_validation import train_test_split
from sklearn.feature_extraction import FeatureHasher
from sklearn.feature_selection import GenericUnivariateSelect
from sklearn.metrics import brier_score_loss
from sklearn.metrics import hinge_loss
from sklearn.metrics import log_loss
from sklearn.metrics import matthews_corrcoef
from sklearn.metrics import roc_auc_score
from sklearn.pipeline import FeatureUnion
from sklearn.pipeline import Pipeline
import xgboost as xgb

FEATURE_DTYPES = {
    'VAR_0002': 'uint16', 'VAR_0003': 'uint16', 'VAR_0008': object, 'VAR_0009': object,
    'VAR_0010': object, 'VAR_0011': object, 'VAR_0012': object, 'VAR_0043': object,
    'VAR_0196': object, 'VAR_0214': object, 'VAR_0226': object, 'VAR_0229': object,
    'VAR_0230': object, 'VAR_0232': object, 'VAR_0236': object, 'VAR_0239': object,
    'VAR_0532': 'uint8', 'VAR_0533': 'uint8', 'VAR_0534': 'uint8', 'VAR_0535': 'uint8',
    'VAR_0536': 'uint8', 'VAR_0537': 'uint8', 'VAR_0538': 'uint8', 'VAR_0539': 'uint8',
    'VAR_0540': 'uint8', 'VAR_0545': 'uint16', 'VAR_0546': 'uint16', 'VAR_0547': 'uint16',
    'VAR_0548': 'uint16', 'VAR_0549': 'uint16', 'VAR_0550': 'uint16', 'VAR_0551': 'uint16',
    'VAR_0552': 'uint8', 'VAR_0553': 'uint8', 'VAR_0554': 'uint16', 'VAR_0555': 'uint16',
    'VAR_0556': 'uint16', 'VAR_0557': 'uint16', 'VAR_0558': 'uint16', 'VAR_0559': 'uint8',
    'VAR_0560': 'uint8', 'VAR_0561': 'uint16', 'VAR_0562': 'uint8', 'VAR_0563': 'uint8',
    'VAR_0564': 'uint8', 'VAR_0565': 'uint8', 'VAR_0566': 'uint8', 'VAR_0567': 'uint8',
    'VAR_0568': 'uint8', 'VAR_0569': 'uint8', 'VAR_0570': 'uint16', 'VAR_0572': 'uint8',
    'VAR_0580': 'uint8', 'VAR_0581': 'uint8', 'VAR_0582': 'uint8', 'VAR_0604': 'uint8',
    'VAR_0605': 'uint8', 'VAR_0606': 'uint8', 'VAR_0617': 'uint8', 'VAR_0618': 'uint8',
    'VAR_0619': 'uint8', 'VAR_0620': 'uint8', 'VAR_0621': 'uint8', 'VAR_0622': 'uint8',
    'VAR_0623': 'uint8', 'VAR_0624': 'uint8', 'VAR_0625': 'uint8', 'VAR_0626': 'uint8',
    'VAR_0627': 'uint8', 'VAR_0637': 'uint8', 'VAR_0638': 'uint8', 'VAR_0639': 'uint8',
    'VAR_0640': 'uint8', 'VAR_0646': 'uint8', 'VAR_0647': 'uint8', 'VAR_0657': 'uint8',
    'VAR_0658': 'uint8', 'VAR_0662': 'uint8', 'VAR_0663': 'uint8', 'VAR_0664': 'uint8',
    'VAR_0665': 'uint8', 'VAR_0666': 'uint8', 'VAR_0667': 'uint8', 'VAR_0668': 'uint8',
    'VAR_0685': 'uint8', 'VAR_0686': 'uint8', 'VAR_0689': 'uint8', 'VAR_0690': 'uint8',
    'VAR_0696': 'uint8', 'VAR_0697': 'uint8', 'VAR_0703': 'uint8', 'VAR_0708': 'uint8',
    'VAR_0709': 'uint8', 'VAR_0710': 'uint8', 'VAR_0711': 'uint8', 'VAR_0712': 'uint8',
    'VAR_0713': 'uint8', 'VAR_0714': 'uint8', 'VAR_0715': 'uint8', 'VAR_0716': 'uint8',
    'VAR_0717': 'uint8', 'VAR_0718': 'uint8', 'VAR_0719': 'uint8', 'VAR_0720': 'uint8',
    'VAR_0721': 'uint8', 'VAR_0722': 'uint8', 'VAR_0723': 'uint8', 'VAR_0724': 'uint8',
    'VAR_0725': 'uint8', 'VAR_0726': 'uint8', 'VAR_0727': 'uint8', 'VAR_0728': 'uint8',
    'VAR_0729': 'uint8', 'VAR_0730': 'uint8', 'VAR_0731': 'uint8', 'VAR_0732': 'uint8',
    'VAR_0733': 'uint8', 'VAR_0734': 'uint8', 'VAR_0735': 'uint8', 'VAR_0736': 'uint8',
    'VAR_0737': 'uint8', 'VAR_0738': 'uint8', 'VAR_0739': 'uint8', 'VAR_0740': 'uint8',
    'VAR_0741': 'uint8', 'VAR_0742': 'uint8', 'VAR_0743': 'uint8', 'VAR_0744': 'uint8',
    'VAR_0745': 'uint8', 'VAR_0746': 'uint8', 'VAR_0747': 'uint8', 'VAR_0748': 'uint8',
    'VAR_0749': 'uint8', 'VAR_0750': 'uint8', 'VAR_0751': 'uint8', 'VAR_0752': 'uint8',
    'VAR_0753': 'uint8', 'VAR_0754': 'uint8', 'VAR_0755': 'uint8', 'VAR_0756': 'uint8',
    'VAR_0758': 'uint8', 'VAR_0759': 'uint8', 'VAR_0760': 'uint8', 'VAR_0761': 'uint8',
    'VAR_0762': 'uint8', 'VAR_0763': 'uint8', 'VAR_0764': 'uint8', 'VAR_0765': 'uint8',
    'VAR_0766': 'uint8', 'VAR_0767': 'uint8', 'VAR_0768': 'uint8', 'VAR_0769': 'uint8',
    'VAR_0770': 'uint8', 'VAR_0771': 'uint8', 'VAR_0772': 'uint8', 'VAR_0773': 'uint8',
    'VAR_0774': 'uint8', 'VAR_0775': 'uint8', 'VAR_0776': 'uint8', 'VAR_0777': 'uint8',
    'VAR_0778': 'uint8', 'VAR_0779': 'uint8', 'VAR_0780': 'uint8', 'VAR_0781': 'uint8',
    'VAR_0782': 'uint8', 'VAR_0783': 'uint8', 'VAR_0784': 'uint8', 'VAR_0785': 'uint8',
    'VAR_0786': 'uint8', 'VAR_0787': 'uint8', 'VAR_0788': 'uint8', 'VAR_0789': 'uint8',
    'VAR_0790': 'uint8', 'VAR_0791': 'uint8', 'VAR_0792': 'uint8', 'VAR_0793': 'uint8',
    'VAR_0794': 'uint8', 'VAR_0795': 'uint8', 'VAR_0796': 'uint8', 'VAR_0797': 'uint8',
    'VAR_0798': 'uint8', 'VAR_0799': 'uint8', 'VAR_0800': 'uint8', 'VAR_0801': 'uint8',
    'VAR_0802': 'uint8', 'VAR_0803': 'uint8', 'VAR_0804': 'uint8', 'VAR_0805': 'uint8',
    'VAR_0806': 'uint8', 'VAR_0807': 'uint8', 'VAR_0808': 'uint8', 'VAR_0809': 'uint8',
    'VAR_0810': 'uint8', 'VAR_0812': 'uint8', 'VAR_0813': 'uint8', 'VAR_0814': 'uint8',
    'VAR_0815': 'uint8', 'VAR_0816': 'uint8', 'VAR_0817': 'uint8', 'VAR_0818': 'uint8',
    'VAR_0819': 'uint8', 'VAR_0820': 'uint8', 'VAR_0821': 'uint8', 'VAR_0822': 'uint8',
    'VAR_0823': 'uint8', 'VAR_0824': 'uint8', 'VAR_0825': 'uint8', 'VAR_0826': 'uint8',
    'VAR_0827': 'uint8', 'VAR_0828': 'uint8', 'VAR_0829': 'uint8', 'VAR_0830': 'uint8',
    'VAR_0831': 'uint8', 'VAR_0832': 'uint8', 'VAR_0833': 'uint8', 'VAR_0834': 'uint8',
    'VAR_0835': 'uint8', 'VAR_0836': 'uint8', 'VAR_0837': 'uint8', 'VAR_0838': 'uint8',
    'VAR_0839': 'uint8', 'VAR_0841': 'uint8', 'VAR_0842': 'uint8', 'VAR_0843': 'uint8',
    'VAR_0844': 'uint8', 'VAR_0845': 'uint8', 'VAR_0846': 'uint8', 'VAR_0848': 'uint8',
    'VAR_0849': 'uint8', 'VAR_0850': 'uint8', 'VAR_0851': 'uint8', 'VAR_0852': 'uint8',
    'VAR_0853': 'uint8', 'VAR_0854': 'uint8', 'VAR_0855': 'uint8', 'VAR_0856': 'uint8',
    'VAR_0857': 'uint8', 'VAR_0859': 'uint8', 'VAR_0877': 'uint8', 'VAR_0878': 'uint8',
    'VAR_0879': 'uint8', 'VAR_0885': 'uint8', 'VAR_0886': 'uint8', 'VAR_0911': 'uint8',
    'VAR_0914': 'uint8', 'VAR_0915': 'uint8', 'VAR_0916': 'uint8', 'VAR_0923': 'uint8',
    'VAR_0924': 'uint8', 'VAR_0925': 'uint8', 'VAR_0926': 'uint8', 'VAR_0927': 'uint8',
    'VAR_0940': 'uint8', 'VAR_0945': 'uint8', 'VAR_0947': 'uint8', 'VAR_0952': 'uint8',
    'VAR_0954': 'uint8', 'VAR_0959': 'uint8', 'VAR_0962': 'uint8', 'VAR_0963': 'uint8',
    'VAR_0969': 'uint8', 'VAR_0973': 'uint8', 'VAR_0974': 'uint8', 'VAR_0975': 'uint8',
    'VAR_0983': 'uint8', 'VAR_0984': 'uint8', 'VAR_0985': 'uint8', 'VAR_0986': 'uint8',
    'VAR_0987': 'uint8', 'VAR_0988': 'uint8', 'VAR_0989': 'uint8', 'VAR_0990': 'uint8',
    'VAR_0991': 'uint8', 'VAR_0992': 'uint8', 'VAR_0993': 'uint8', 'VAR_0994': 'uint8',
    'VAR_0995': 'uint8', 'VAR_0996': 'uint8', 'VAR_0997': 'uint8', 'VAR_0998': 'uint8',
    'VAR_0999': 'uint8', 'VAR_1000': 'uint8', 'VAR_1001': 'uint8', 'VAR_1002': 'uint8',
    'VAR_1003': 'uint8', 'VAR_1004': 'uint8', 'VAR_1005': 'uint8', 'VAR_1006': 'uint8',
    'VAR_1007': 'uint8', 'VAR_1008': 'uint8', 'VAR_1009': 'uint8', 'VAR_1010': 'uint8',
    'VAR_1011': 'uint8', 'VAR_1012': 'uint8', 'VAR_1013': 'uint8', 'VAR_1014': 'uint8',
    'VAR_1015': 'uint8', 'VAR_1016': 'uint8', 'VAR_1017': 'uint8', 'VAR_1018': 'uint8',
    'VAR_1019': 'uint8', 'VAR_1020': 'uint8', 'VAR_1021': 'uint8', 'VAR_1022': 'uint8',
    'VAR_1023': 'uint8', 'VAR_1024': 'uint8', 'VAR_1025': 'uint8', 'VAR_1026': 'uint8',
    'VAR_1027': 'uint8', 'VAR_1028': 'uint8', 'VAR_1029': 'uint8', 'VAR_1030': 'uint8',
    'VAR_1031': 'uint8', 'VAR_1032': 'uint8', 'VAR_1033': 'uint8', 'VAR_1034': 'uint8',
    'VAR_1035': 'uint8', 'VAR_1036': 'uint8', 'VAR_1037': 'uint8', 'VAR_1038': 'uint8',
    'VAR_1039': 'uint8', 'VAR_1040': 'uint8', 'VAR_1041': 'uint8', 'VAR_1042': 'uint8',
    'VAR_1043': 'uint8', 'VAR_1044': 'uint8', 'VAR_1045': 'uint8', 'VAR_1046': 'uint8',
    'VAR_1047': 'uint8', 'VAR_1048': 'uint8', 'VAR_1049': 'uint8', 'VAR_1050': 'uint8',
    'VAR_1051': 'uint8', 'VAR_1052': 'uint8', 'VAR_1053': 'uint8', 'VAR_1054': 'uint8',
    'VAR_1055': 'uint8', 'VAR_1056': 'uint8', 'VAR_1057': 'uint8', 'VAR_1058': 'uint8',
    'VAR_1059': 'uint8', 'VAR_1060': 'uint8', 'VAR_1061': 'uint8', 'VAR_1062': 'uint8',
    'VAR_1063': 'uint8', 'VAR_1064': 'uint8', 'VAR_1065': 'uint8', 'VAR_1066': 'uint8',
    'VAR_1067': 'uint8', 'VAR_1068': 'uint8', 'VAR_1069': 'uint8', 'VAR_1070': 'uint8',
    'VAR_1071': 'uint8', 'VAR_1072': 'uint8', 'VAR_1073': 'uint8', 'VAR_1080': 'uint8',
    'VAR_1108': 'uint8', 'VAR_1109': 'uint8', 'VAR_1161': 'uint8', 'VAR_1162': 'uint8',
    'VAR_1163': 'uint8', 'VAR_1164': 'uint8', 'VAR_1165': 'uint8', 'VAR_1166': 'uint8',
    'VAR_1167': 'uint8', 'VAR_1168': 'uint8', 'VAR_1175': 'uint8', 'VAR_1176': 'uint8',
    'VAR_1177': 'uint8', 'VAR_1178': 'uint8', 'VAR_1185': 'uint8', 'VAR_1186': 'uint8',
    'VAR_1187': 'uint8', 'VAR_1188': 'uint8', 'VAR_1189': 'uint8', 'VAR_1190': 'uint8',
    'VAR_1191': 'uint8', 'VAR_1192': 'uint8', 'VAR_1193': 'uint8', 'VAR_1194': 'uint8',
    'VAR_1195': 'uint8', 'VAR_1196': 'uint8', 'VAR_1197': 'uint8', 'VAR_1198': 'uint8',
    'VAR_1212': 'uint8', 'VAR_1213': 'uint8', 'VAR_1217': 'uint8', 'VAR_1218': 'uint8',
    'VAR_1224': 'uint8', 'VAR_1225': 'uint8', 'VAR_1226': 'uint8', 'VAR_1229': 'uint8',
    'VAR_1230': 'uint8', 'VAR_1231': 'uint8', 'VAR_1232': 'uint8', 'VAR_1233': 'uint8',
    'VAR_1234': 'uint8', 'VAR_1235': 'uint8', 'VAR_1236': 'uint8', 'VAR_1237': 'uint8',
    'VAR_1238': 'uint8', 'VAR_1239': 'uint8', 'VAR_1267': 'uint8', 'VAR_1268': 'uint8',
    'VAR_1269': 'uint8', 'VAR_1270': 'uint8', 'VAR_1271': 'uint8', 'VAR_1272': 'uint8',
    'VAR_1273': 'uint8', 'VAR_1274': 'uint8', 'VAR_1275': 'uint8', 'VAR_1276': 'uint8',
    'VAR_1277': 'uint8', 'VAR_1278': 'uint8', 'VAR_1279': 'uint8', 'VAR_1280': 'uint8',
    'VAR_1281': 'uint8', 'VAR_1282': 'uint8', 'VAR_1283': 'uint8', 'VAR_1284': 'uint8',
    'VAR_1285': 'uint8', 'VAR_1286': 'uint8', 'VAR_1287': 'uint8', 'VAR_1288': 'uint8',
    'VAR_1289': 'uint8', 'VAR_1290': 'uint8', 'VAR_1291': 'uint8', 'VAR_1292': 'uint8',
    'VAR_1293': 'uint8', 'VAR_1294': 'uint8', 'VAR_1295': 'uint8', 'VAR_1296': 'uint8',
    'VAR_1297': 'uint8', 'VAR_1298': 'uint8', 'VAR_1299': 'uint8', 'VAR_1300': 'uint8',
    'VAR_1301': 'uint8', 'VAR_1302': 'uint8', 'VAR_1303': 'uint8', 'VAR_1304': 'uint8',
    'VAR_1305': 'uint8', 'VAR_1306': 'uint8', 'VAR_1307': 'uint8', 'VAR_1338': 'uint8',
    'VAR_1339': 'uint8', 'VAR_1340': 'uint8', 'VAR_1345': 'uint8', 'VAR_1346': 'uint8',
    'VAR_1347': 'uint8', 'VAR_1348': 'uint8', 'VAR_1349': 'uint8', 'VAR_1350': 'uint8',
    'VAR_1351': 'uint8', 'VAR_1352': 'uint8', 'VAR_1359': 'uint8', 'VAR_1360': 'uint8',
    'VAR_1361': 'uint8', 'VAR_1362': 'uint8', 'VAR_1363': 'uint8', 'VAR_1364': 'uint8',
    'VAR_1365': 'uint8', 'VAR_1366': 'uint8', 'VAR_1367': 'uint8', 'VAR_1368': 'uint8',
    'VAR_1369': 'uint8', 'VAR_1386': 'uint8', 'VAR_1387': 'uint8', 'VAR_1388': 'uint8',
    'VAR_1389': 'uint8', 'VAR_1392': 'uint8', 'VAR_1393': 'uint8', 'VAR_1394': 'uint8',
    'VAR_1395': 'uint8', 'VAR_1396': 'uint8', 'VAR_1404': 'uint8', 'VAR_1405': 'uint8',
    'VAR_1406': 'uint8', 'VAR_1407': 'uint8', 'VAR_1408': 'uint8', 'VAR_1409': 'uint8',
    'VAR_1410': 'uint8', 'VAR_1411': 'uint8', 'VAR_1412': 'uint8', 'VAR_1413': 'uint8',
    'VAR_1414': 'uint8', 'VAR_1415': 'uint8', 'VAR_1416': 'uint8', 'VAR_1417': 'uint8',
    'VAR_1427': 'uint8', 'VAR_1429': 'uint8', 'VAR_1430': 'uint8', 'VAR_1431': 'uint8',
    'VAR_1432': 'uint8', 'VAR_1433': 'uint8', 'VAR_1434': 'uint8', 'VAR_1435': 'uint8',
    'VAR_1449': 'uint8', 'VAR_1450': 'uint8', 'VAR_1456': 'uint8', 'VAR_1457': 'uint8',
    'VAR_1458': 'uint8', 'VAR_1459': 'uint8', 'VAR_1460': 'uint8', 'VAR_1461': 'uint8',
    'VAR_1462': 'uint8', 'VAR_1463': 'uint8', 'VAR_1464': 'uint8', 'VAR_1465': 'uint8',
    'VAR_1466': 'uint8', 'VAR_1467': 'uint8', 'VAR_1468': 'uint8', 'VAR_1469': 'uint8',
    'VAR_1470': 'uint8', 'VAR_1471': 'uint8', 'VAR_1472': 'uint8', 'VAR_1473': 'uint8',
    'VAR_1474': 'uint8', 'VAR_1475': 'uint8', 'VAR_1476': 'uint8', 'VAR_1477': 'uint8',
    'VAR_1478': 'uint8', 'VAR_1479': 'uint8', 'VAR_1480': 'uint8', 'VAR_1481': 'uint8',
    'VAR_1482': 'uint8', 'VAR_1532': 'uint8', 'VAR_1533': 'uint8', 'VAR_1534': 'uint8',
    'VAR_1535': 'uint8', 'VAR_1537': 'uint8', 'VAR_1538': 'uint8', 'VAR_1539': 'uint8',
    'VAR_1540': 'uint8', 'VAR_1542': 'uint8', 'VAR_1543': 'uint8', 'VAR_1544': 'uint8',
    'VAR_1545': 'uint8', 'VAR_1546': 'uint8', 'VAR_1547': 'uint8', 'VAR_1548': 'uint8',
    'VAR_1549': 'uint8', 'VAR_1551': 'uint8', 'VAR_1552': 'uint8', 'VAR_1553': 'uint8',
    'VAR_1554': 'uint8', 'VAR_1556': 'uint8', 'VAR_1557': 'uint8', 'VAR_1558': 'uint8',
    'VAR_1559': 'uint8', 'VAR_1561': 'uint8', 'VAR_1562': 'uint8', 'VAR_1563': 'uint8',
    'VAR_1564': 'uint8', 'VAR_1565': 'uint8', 'VAR_1566': 'uint8', 'VAR_1567': 'uint8',
    'VAR_1568': 'uint8', 'VAR_1569': 'uint8', 'VAR_1570': 'uint8', 'VAR_1571': 'uint8',
    'VAR_1572': 'uint8', 'VAR_1574': 'uint8', 'VAR_1575': 'uint8', 'VAR_1576': 'uint8',
    'VAR_1577': 'uint8', 'VAR_1578': 'uint8', 'VAR_1579': 'uint8', 'VAR_1583': 'uint8',
    'VAR_1584': 'uint8', 'VAR_1585': 'uint8', 'VAR_1586': 'uint8', 'VAR_1587': 'uint8',
    'VAR_1588': 'uint8', 'VAR_1589': 'uint8', 'VAR_1590': 'uint8', 'VAR_1591': 'uint8',
    'VAR_1592': 'uint8', 'VAR_1593': 'uint8', 'VAR_1594': 'uint8', 'VAR_1595': 'uint8',
    'VAR_1596': 'uint8', 'VAR_1597': 'uint8', 'VAR_1598': 'uint8', 'VAR_1599': 'uint8',
    'VAR_1600': 'uint8', 'VAR_1601': 'uint8', 'VAR_1602': 'uint8', 'VAR_1603': 'uint8',
    'VAR_1604': 'uint8', 'VAR_1605': 'uint8', 'VAR_1606': 'uint8', 'VAR_1607': 'uint8',
    'VAR_1608': 'uint8', 'VAR_1609': 'uint8', 'VAR_1610': 'uint8', 'VAR_1656': 'uint8',
    'VAR_1657': 'uint8', 'VAR_1658': 'uint8', 'VAR_1659': 'uint8', 'VAR_1660': 'uint8',
    'VAR_1661': 'uint8', 'VAR_1662': 'uint8', 'VAR_1663': 'uint8', 'VAR_1664': 'uint8',
    'VAR_1665': 'uint8', 'VAR_1666': 'uint8', 'VAR_1667': 'uint8', 'VAR_1668': 'uint8',
    'VAR_1669': 'uint8', 'VAR_1670': 'uint8', 'VAR_1671': 'uint8', 'VAR_1672': 'uint8',
    'VAR_1673': 'uint8', 'VAR_1674': 'uint8', 'VAR_1675': 'uint8', 'VAR_1676': 'uint8',
    'VAR_1677': 'uint8', 'VAR_1678': 'uint8', 'VAR_1679': 'uint8', 'VAR_1680': 'uint8',
    'VAR_1681': 'uint8', 'VAR_1682': 'uint8', 'VAR_1683': 'uint8', 'VAR_1713': 'uint8',
    'VAR_1714': 'uint8', 'VAR_1721': 'uint8', 'VAR_1722': 'uint8', 'VAR_1723': 'uint8',
    'VAR_1724': 'uint8', 'VAR_1725': 'uint8', 'VAR_1726': 'uint8', 'VAR_1727': 'uint8',
    'VAR_1728': 'uint8', 'VAR_1740': 'uint8', 'VAR_1741': 'uint8', 'VAR_1742': 'uint8',
    'VAR_1743': 'uint8', 'VAR_1744': 'uint8', 'VAR_1745': 'uint8', 'VAR_1746': 'uint8',
    'VAR_1752': 'uint8', 'VAR_1753': 'uint8', 'VAR_1760': 'uint8', 'VAR_1761': 'uint8',
    'VAR_1762': 'uint8', 'VAR_1763': 'uint8', 'VAR_1764': 'uint8', 'VAR_1765': 'uint8',
    'VAR_1766': 'uint8', 'VAR_1767': 'uint8', 'VAR_1768': 'uint8', 'VAR_1769': 'uint8',
    'VAR_1770': 'uint8', 'VAR_1771': 'uint8', 'VAR_1772': 'uint8', 'VAR_1773': 'uint8',
    'VAR_1774': 'uint8', 'VAR_1775': 'uint8', 'VAR_1776': 'uint8', 'VAR_1777': 'uint8',
    'VAR_1778': 'uint8', 'VAR_1779': 'uint8', 'VAR_1780': 'uint8', 'VAR_1781': 'uint8',
    'VAR_1782': 'uint8', 'VAR_1783': 'uint8', 'VAR_1784': 'uint8', 'VAR_1785': 'uint8',
    'VAR_1786': 'uint8', 'VAR_1787': 'uint8', 'VAR_1788': 'uint8', 'VAR_1789': 'uint8',
    'VAR_1790': 'uint8', 'VAR_1791': 'uint8', 'VAR_1792': 'uint8', 'VAR_1793': 'uint8',
    'VAR_1794': 'uint8', 'VAR_1843': 'uint8', 'VAR_1844': 'uint8', 'VAR_1853': 'uint8',
    'VAR_1854': 'uint8', 'VAR_1855': 'uint8', 'VAR_1856': 'uint8', 'VAR_1857': 'uint8',
    'VAR_1866': 'uint8', 'VAR_1867': 'uint8', 'VAR_1872': 'uint8', 'VAR_1873': 'uint8',
    'VAR_1874': 'uint8', 'VAR_1875': 'uint8', 'VAR_1876': 'uint8', 'VAR_1877': 'uint8',
    'VAR_1878': 'uint8', 'VAR_1879': 'uint8', 'VAR_1880': 'uint8', 'VAR_1881': 'uint8',
    'VAR_1882': 'uint8', 'VAR_1883': 'uint8', 'VAR_1884': 'uint8', 'VAR_1885': 'uint8',
    'VAR_1886': 'uint8', 'VAR_1887': 'uint8', 'VAR_1888': 'uint8', 'VAR_1903': 'uint8',
    'VAR_1904': 'uint8', 'VAR_1905': 'uint8', 'VAR_1906': 'uint8', 'VAR_1907': 'uint8',
    'VAR_1908': 'uint8', 'VAR_1909': 'uint8', 'VAR_1910': 'uint8', 'VAR_1920': 'uint8',
    'VAR_1921': 'uint8', 'VAR_1925': 'uint8', 'VAR_1926': 'uint8', 'VAR_1927': 'uint8',
    'VAR_1928': 'uint16', 'VAR_1930': 'uint16'}
FEATURE_COLUMN_NAMES = [
    'VAR_0001', 'VAR_0002', 'VAR_0003', 'VAR_0004', 'VAR_0005', 'VAR_0006', 'VAR_0007',
    'VAR_0008', 'VAR_0009', 'VAR_0010', 'VAR_0011', 'VAR_0012', 'VAR_0013', 'VAR_0014',
    'VAR_0015', 'VAR_0016', 'VAR_0017', 'VAR_0018', 'VAR_0019', 'VAR_0020', 'VAR_0021',
    'VAR_0022', 'VAR_0023', 'VAR_0024', 'VAR_0025', 'VAR_0026', 'VAR_0027', 'VAR_0028',
    'VAR_0029', 'VAR_0030', 'VAR_0031', 'VAR_0032', 'VAR_0033', 'VAR_0034', 'VAR_0035',
    'VAR_0036', 'VAR_0037', 'VAR_0038', 'VAR_0039', 'VAR_0040', 'VAR_0041', 'VAR_0042',
    'VAR_0043', 'VAR_0044', 'VAR_0045', 'VAR_0046', 'VAR_0047', 'VAR_0048', 'VAR_0049',
    'VAR_0050', 'VAR_0051', 'VAR_0052', 'VAR_0053', 'VAR_0054', 'VAR_0055', 'VAR_0056',
    'VAR_0057', 'VAR_0058', 'VAR_0059', 'VAR_0060', 'VAR_0061', 'VAR_0062', 'VAR_0063',
    'VAR_0064', 'VAR_0065', 'VAR_0066', 'VAR_0067', 'VAR_0068', 'VAR_0069', 'VAR_0070',
    'VAR_0071', 'VAR_0072', 'VAR_0073', 'VAR_0074', 'VAR_0075', 'VAR_0076', 'VAR_0077',
    'VAR_0078', 'VAR_0079', 'VAR_0080', 'VAR_0081', 'VAR_0082', 'VAR_0083', 'VAR_0084',
    'VAR_0085', 'VAR_0086', 'VAR_0087', 'VAR_0088', 'VAR_0089', 'VAR_0090', 'VAR_0091',
    'VAR_0092', 'VAR_0093', 'VAR_0094', 'VAR_0095', 'VAR_0096', 'VAR_0097', 'VAR_0098',
    'VAR_0099', 'VAR_0100', 'VAR_0101', 'VAR_0102', 'VAR_0103', 'VAR_0104', 'VAR_0105',
    'VAR_0106', 'VAR_0107', 'VAR_0108', 'VAR_0109', 'VAR_0110', 'VAR_0111', 'VAR_0112',
    'VAR_0113', 'VAR_0114', 'VAR_0115', 'VAR_0116', 'VAR_0117', 'VAR_0118', 'VAR_0119',
    'VAR_0120', 'VAR_0121', 'VAR_0122', 'VAR_0123', 'VAR_0124', 'VAR_0125', 'VAR_0126',
    'VAR_0127', 'VAR_0128', 'VAR_0129', 'VAR_0130', 'VAR_0131', 'VAR_0132', 'VAR_0133',
    'VAR_0134', 'VAR_0135', 'VAR_0136', 'VAR_0137', 'VAR_0138', 'VAR_0139', 'VAR_0140',
    'VAR_0141', 'VAR_0142', 'VAR_0143', 'VAR_0144', 'VAR_0145', 'VAR_0146', 'VAR_0147',
    'VAR_0148', 'VAR_0149', 'VAR_0150', 'VAR_0151', 'VAR_0152', 'VAR_0153', 'VAR_0154',
    'VAR_0155', 'VAR_0156', 'VAR_0157', 'VAR_0158', 'VAR_0159', 'VAR_0160', 'VAR_0161',
    'VAR_0162', 'VAR_0163', 'VAR_0164', 'VAR_0165', 'VAR_0166', 'VAR_0167', 'VAR_0168',
    'VAR_0169', 'VAR_0170', 'VAR_0171', 'VAR_0172', 'VAR_0173', 'VAR_0174', 'VAR_0175',
    'VAR_0176', 'VAR_0177', 'VAR_0178', 'VAR_0179', 'VAR_0180', 'VAR_0181', 'VAR_0182',
    'VAR_0183', 'VAR_0184', 'VAR_0185', 'VAR_0186', 'VAR_0187', 'VAR_0188', 'VAR_0189',
    'VAR_0190', 'VAR_0191', 'VAR_0192', 'VAR_0193', 'VAR_0194', 'VAR_0195', 'VAR_0196',
    'VAR_0197', 'VAR_0198', 'VAR_0199', 'VAR_0200', 'VAR_0201', 'VAR_0202', 'VAR_0203',
    'VAR_0204', 'VAR_0205', 'VAR_0206', 'VAR_0208', 'VAR_0209', 'VAR_0210', 'VAR_0211',
    'VAR_0212', 'VAR_0214', 'VAR_0215', 'VAR_0216', 'VAR_0217', 'VAR_0219', 'VAR_0220',
    'VAR_0221', 'VAR_0222', 'VAR_0223', 'VAR_0224', 'VAR_0225', 'VAR_0226', 'VAR_0227',
    'VAR_0228', 'VAR_0229', 'VAR_0230', 'VAR_0231', 'VAR_0232', 'VAR_0233', 'VAR_0234',
    'VAR_0235', 'VAR_0236', 'VAR_0237', 'VAR_0238', 'VAR_0239', 'VAR_0241', 'VAR_0242',
    'VAR_0243', 'VAR_0244', 'VAR_0245', 'VAR_0246', 'VAR_0247', 'VAR_0248', 'VAR_0249',
    'VAR_0250', 'VAR_0251', 'VAR_0252', 'VAR_0253', 'VAR_0254', 'VAR_0255', 'VAR_0256',
    'VAR_0257', 'VAR_0258', 'VAR_0259', 'VAR_0260', 'VAR_0261', 'VAR_0262', 'VAR_0263',
    'VAR_0264', 'VAR_0265', 'VAR_0266', 'VAR_0267', 'VAR_0268', 'VAR_0269', 'VAR_0270',
    'VAR_0271', 'VAR_0272', 'VAR_0273', 'VAR_0274', 'VAR_0275', 'VAR_0276', 'VAR_0277',
    'VAR_0278', 'VAR_0279', 'VAR_0280', 'VAR_0281', 'VAR_0282', 'VAR_0283', 'VAR_0284',
    'VAR_0285', 'VAR_0286', 'VAR_0287', 'VAR_0288', 'VAR_0289', 'VAR_0290', 'VAR_0291',
    'VAR_0292', 'VAR_0293', 'VAR_0294', 'VAR_0295', 'VAR_0296', 'VAR_0297', 'VAR_0298',
    'VAR_0299', 'VAR_0300', 'VAR_0301', 'VAR_0302', 'VAR_0303', 'VAR_0304', 'VAR_0305',
    'VAR_0306', 'VAR_0307', 'VAR_0308', 'VAR_0309', 'VAR_0310', 'VAR_0311', 'VAR_0312',
    'VAR_0313', 'VAR_0314', 'VAR_0315', 'VAR_0316', 'VAR_0317', 'VAR_0318', 'VAR_0319',
    'VAR_0320', 'VAR_0321', 'VAR_0322', 'VAR_0323', 'VAR_0324', 'VAR_0325', 'VAR_0326',
    'VAR_0327', 'VAR_0328', 'VAR_0329', 'VAR_0330', 'VAR_0331', 'VAR_0332', 'VAR_0333',
    'VAR_0334', 'VAR_0335', 'VAR_0336', 'VAR_0337', 'VAR_0338', 'VAR_0339', 'VAR_0340',
    'VAR_0341', 'VAR_0342', 'VAR_0343', 'VAR_0344', 'VAR_0345', 'VAR_0346', 'VAR_0347',
    'VAR_0348', 'VAR_0349', 'VAR_0350', 'VAR_0351', 'VAR_0352', 'VAR_0353', 'VAR_0354',
    'VAR_0355', 'VAR_0356', 'VAR_0357', 'VAR_0358', 'VAR_0359', 'VAR_0360', 'VAR_0361',
    'VAR_0362', 'VAR_0363', 'VAR_0364', 'VAR_0365', 'VAR_0366', 'VAR_0367', 'VAR_0368',
    'VAR_0369', 'VAR_0370', 'VAR_0371', 'VAR_0372', 'VAR_0373', 'VAR_0374', 'VAR_0375',
    'VAR_0376', 'VAR_0377', 'VAR_0378', 'VAR_0379', 'VAR_0380', 'VAR_0381', 'VAR_0382',
    'VAR_0383', 'VAR_0384', 'VAR_0385', 'VAR_0386', 'VAR_0387', 'VAR_0388', 'VAR_0389',
    'VAR_0390', 'VAR_0391', 'VAR_0392', 'VAR_0393', 'VAR_0394', 'VAR_0395', 'VAR_0396',
    'VAR_0397', 'VAR_0398', 'VAR_0399', 'VAR_0400', 'VAR_0401', 'VAR_0402', 'VAR_0403',
    'VAR_0404', 'VAR_0405', 'VAR_0406', 'VAR_0407', 'VAR_0408', 'VAR_0409', 'VAR_0410',
    'VAR_0411', 'VAR_0412', 'VAR_0413', 'VAR_0414', 'VAR_0415', 'VAR_0416', 'VAR_0417',
    'VAR_0418', 'VAR_0419', 'VAR_0420', 'VAR_0421', 'VAR_0422', 'VAR_0423', 'VAR_0424',
    'VAR_0425', 'VAR_0426', 'VAR_0427', 'VAR_0428', 'VAR_0429', 'VAR_0430', 'VAR_0431',
    'VAR_0432', 'VAR_0433', 'VAR_0434', 'VAR_0435', 'VAR_0436', 'VAR_0437', 'VAR_0438',
    'VAR_0439', 'VAR_0440', 'VAR_0441', 'VAR_0442', 'VAR_0443', 'VAR_0444', 'VAR_0445',
    'VAR_0446', 'VAR_0447', 'VAR_0448', 'VAR_0449', 'VAR_0450', 'VAR_0451', 'VAR_0452',
    'VAR_0453', 'VAR_0454', 'VAR_0455', 'VAR_0456', 'VAR_0457', 'VAR_0458', 'VAR_0459',
    'VAR_0460', 'VAR_0461', 'VAR_0462', 'VAR_0463', 'VAR_0464', 'VAR_0465', 'VAR_0466',
    'VAR_0467', 'VAR_0468', 'VAR_0469', 'VAR_0470', 'VAR_0471', 'VAR_0472', 'VAR_0473',
    'VAR_0474', 'VAR_0475', 'VAR_0476', 'VAR_0477', 'VAR_0478', 'VAR_0479', 'VAR_0480',
    'VAR_0481', 'VAR_0482', 'VAR_0483', 'VAR_0484', 'VAR_0485', 'VAR_0486', 'VAR_0487',
    'VAR_0488', 'VAR_0489', 'VAR_0490', 'VAR_0491', 'VAR_0492', 'VAR_0493', 'VAR_0494',
    'VAR_0495', 'VAR_0496', 'VAR_0497', 'VAR_0498', 'VAR_0499', 'VAR_0500', 'VAR_0501',
    'VAR_0502', 'VAR_0503', 'VAR_0504', 'VAR_0505', 'VAR_0506', 'VAR_0507', 'VAR_0508',
    'VAR_0509', 'VAR_0510', 'VAR_0511', 'VAR_0512', 'VAR_0513', 'VAR_0514', 'VAR_0515',
    'VAR_0516', 'VAR_0517', 'VAR_0518', 'VAR_0519', 'VAR_0520', 'VAR_0521', 'VAR_0522',
    'VAR_0523', 'VAR_0524', 'VAR_0525', 'VAR_0526', 'VAR_0527', 'VAR_0528', 'VAR_0529',
    'VAR_0530', 'VAR_0531', 'VAR_0532', 'VAR_0533', 'VAR_0534', 'VAR_0535', 'VAR_0536',
    'VAR_0537', 'VAR_0538', 'VAR_0539', 'VAR_0540', 'VAR_0541', 'VAR_0542', 'VAR_0543',
    'VAR_0544', 'VAR_0545', 'VAR_0546', 'VAR_0547', 'VAR_0548', 'VAR_0549', 'VAR_0550',
    'VAR_0551', 'VAR_0552', 'VAR_0553', 'VAR_0554', 'VAR_0555', 'VAR_0556', 'VAR_0557',
    'VAR_0558', 'VAR_0559', 'VAR_0560', 'VAR_0561', 'VAR_0562', 'VAR_0563', 'VAR_0564',
    'VAR_0565', 'VAR_0566', 'VAR_0567', 'VAR_0568', 'VAR_0569', 'VAR_0570', 'VAR_0571',
    'VAR_0572', 'VAR_0573', 'VAR_0574', 'VAR_0575', 'VAR_0576', 'VAR_0577', 'VAR_0578',
    'VAR_0579', 'VAR_0580', 'VAR_0581', 'VAR_0582', 'VAR_0583', 'VAR_0584', 'VAR_0585',
    'VAR_0586', 'VAR_0587', 'VAR_0588', 'VAR_0589', 'VAR_0590', 'VAR_0591', 'VAR_0592',
    'VAR_0593', 'VAR_0594', 'VAR_0595', 'VAR_0596', 'VAR_0597', 'VAR_0598', 'VAR_0599',
    'VAR_0600', 'VAR_0601', 'VAR_0602', 'VAR_0603', 'VAR_0604', 'VAR_0605', 'VAR_0606',
    'VAR_0607', 'VAR_0608', 'VAR_0609', 'VAR_0610', 'VAR_0611', 'VAR_0612', 'VAR_0613',
    'VAR_0614', 'VAR_0615', 'VAR_0616', 'VAR_0617', 'VAR_0618', 'VAR_0619', 'VAR_0620',
    'VAR_0621', 'VAR_0622', 'VAR_0623', 'VAR_0624', 'VAR_0625', 'VAR_0626', 'VAR_0627',
    'VAR_0628', 'VAR_0629', 'VAR_0630', 'VAR_0631', 'VAR_0632', 'VAR_0633', 'VAR_0634',
    'VAR_0635', 'VAR_0636', 'VAR_0637', 'VAR_0638', 'VAR_0639', 'VAR_0640', 'VAR_0641',
    'VAR_0642', 'VAR_0643', 'VAR_0644', 'VAR_0645', 'VAR_0646', 'VAR_0647', 'VAR_0648',
    'VAR_0649', 'VAR_0650', 'VAR_0651', 'VAR_0652', 'VAR_0653', 'VAR_0654', 'VAR_0655',
    'VAR_0656', 'VAR_0657', 'VAR_0658', 'VAR_0659', 'VAR_0660', 'VAR_0661', 'VAR_0662',
    'VAR_0663', 'VAR_0664', 'VAR_0665', 'VAR_0666', 'VAR_0667', 'VAR_0668', 'VAR_0669',
    'VAR_0670', 'VAR_0671', 'VAR_0672', 'VAR_0673', 'VAR_0674', 'VAR_0675', 'VAR_0676',
    'VAR_0677', 'VAR_0678', 'VAR_0679', 'VAR_0680', 'VAR_0681', 'VAR_0682', 'VAR_0683',
    'VAR_0684', 'VAR_0685', 'VAR_0686', 'VAR_0687', 'VAR_0688', 'VAR_0689', 'VAR_0690',
    'VAR_0691', 'VAR_0692', 'VAR_0693', 'VAR_0694', 'VAR_0695', 'VAR_0696', 'VAR_0697',
    'VAR_0698', 'VAR_0699', 'VAR_0700', 'VAR_0701', 'VAR_0702', 'VAR_0703', 'VAR_0704',
    'VAR_0705', 'VAR_0706', 'VAR_0707', 'VAR_0708', 'VAR_0709', 'VAR_0710', 'VAR_0711',
    'VAR_0712', 'VAR_0713', 'VAR_0714', 'VAR_0715', 'VAR_0716', 'VAR_0717', 'VAR_0718',
    'VAR_0719', 'VAR_0720', 'VAR_0721', 'VAR_0722', 'VAR_0723', 'VAR_0724', 'VAR_0725',
    'VAR_0726', 'VAR_0727', 'VAR_0728', 'VAR_0729', 'VAR_0730', 'VAR_0731', 'VAR_0732',
    'VAR_0733', 'VAR_0734', 'VAR_0735', 'VAR_0736', 'VAR_0737', 'VAR_0738', 'VAR_0739',
    'VAR_0740', 'VAR_0741', 'VAR_0742', 'VAR_0743', 'VAR_0744', 'VAR_0745', 'VAR_0746',
    'VAR_0747', 'VAR_0748', 'VAR_0749', 'VAR_0750', 'VAR_0751', 'VAR_0752', 'VAR_0753',
    'VAR_0754', 'VAR_0755', 'VAR_0756', 'VAR_0757', 'VAR_0758', 'VAR_0759', 'VAR_0760',
    'VAR_0761', 'VAR_0762', 'VAR_0763', 'VAR_0764', 'VAR_0765', 'VAR_0766', 'VAR_0767',
    'VAR_0768', 'VAR_0769', 'VAR_0770', 'VAR_0771', 'VAR_0772', 'VAR_0773', 'VAR_0774',
    'VAR_0775', 'VAR_0776', 'VAR_0777', 'VAR_0778', 'VAR_0779', 'VAR_0780', 'VAR_0781',
    'VAR_0782', 'VAR_0783', 'VAR_0784', 'VAR_0785', 'VAR_0786', 'VAR_0787', 'VAR_0788',
    'VAR_0789', 'VAR_0790', 'VAR_0791', 'VAR_0792', 'VAR_0793', 'VAR_0794', 'VAR_0795',
    'VAR_0796', 'VAR_0797', 'VAR_0798', 'VAR_0799', 'VAR_0800', 'VAR_0801', 'VAR_0802',
    'VAR_0803', 'VAR_0804', 'VAR_0805', 'VAR_0806', 'VAR_0807', 'VAR_0808', 'VAR_0809',
    'VAR_0810', 'VAR_0811', 'VAR_0812', 'VAR_0813', 'VAR_0814', 'VAR_0815', 'VAR_0816',
    'VAR_0817', 'VAR_0818', 'VAR_0819', 'VAR_0820', 'VAR_0821', 'VAR_0822', 'VAR_0823',
    'VAR_0824', 'VAR_0825', 'VAR_0826', 'VAR_0827', 'VAR_0828', 'VAR_0829', 'VAR_0830',
    'VAR_0831', 'VAR_0832', 'VAR_0833', 'VAR_0834', 'VAR_0835', 'VAR_0836', 'VAR_0837',
    'VAR_0838', 'VAR_0839', 'VAR_0841', 'VAR_0842', 'VAR_0843', 'VAR_0844', 'VAR_0845',
    'VAR_0846', 'VAR_0848', 'VAR_0849', 'VAR_0850', 'VAR_0851', 'VAR_0852', 'VAR_0853',
    'VAR_0854', 'VAR_0855', 'VAR_0856', 'VAR_0857', 'VAR_0858', 'VAR_0859', 'VAR_0860',
    'VAR_0861', 'VAR_0862', 'VAR_0863', 'VAR_0864', 'VAR_0865', 'VAR_0866', 'VAR_0867',
    'VAR_0868', 'VAR_0869', 'VAR_0870', 'VAR_0871', 'VAR_0872', 'VAR_0873', 'VAR_0874',
    'VAR_0875', 'VAR_0876', 'VAR_0877', 'VAR_0878', 'VAR_0879', 'VAR_0880', 'VAR_0881',
    'VAR_0882', 'VAR_0883', 'VAR_0884', 'VAR_0885', 'VAR_0886', 'VAR_0887', 'VAR_0888',
    'VAR_0889', 'VAR_0890', 'VAR_0891', 'VAR_0892', 'VAR_0893', 'VAR_0894', 'VAR_0895',
    'VAR_0896', 'VAR_0897', 'VAR_0898', 'VAR_0899', 'VAR_0900', 'VAR_0901', 'VAR_0902',
    'VAR_0903', 'VAR_0904', 'VAR_0905', 'VAR_0906', 'VAR_0907', 'VAR_0908', 'VAR_0909',
    'VAR_0910', 'VAR_0911', 'VAR_0912', 'VAR_0913', 'VAR_0914', 'VAR_0915', 'VAR_0916',
    'VAR_0917', 'VAR_0918', 'VAR_0919', 'VAR_0920', 'VAR_0921', 'VAR_0922', 'VAR_0923',
    'VAR_0924', 'VAR_0925', 'VAR_0926', 'VAR_0927', 'VAR_0928', 'VAR_0929', 'VAR_0930',
    'VAR_0931', 'VAR_0932', 'VAR_0933', 'VAR_0934', 'VAR_0935', 'VAR_0936', 'VAR_0937',
    'VAR_0938', 'VAR_0939', 'VAR_0940', 'VAR_0941', 'VAR_0942', 'VAR_0943', 'VAR_0944',
    'VAR_0945', 'VAR_0946', 'VAR_0947', 'VAR_0948', 'VAR_0949', 'VAR_0950', 'VAR_0951',
    'VAR_0952', 'VAR_0953', 'VAR_0954', 'VAR_0955', 'VAR_0956', 'VAR_0957', 'VAR_0958',
    'VAR_0959', 'VAR_0960', 'VAR_0961', 'VAR_0962', 'VAR_0963', 'VAR_0964', 'VAR_0965',
    'VAR_0966', 'VAR_0967', 'VAR_0968', 'VAR_0969', 'VAR_0970', 'VAR_0971', 'VAR_0972',
    'VAR_0973', 'VAR_0974', 'VAR_0975', 'VAR_0976', 'VAR_0977', 'VAR_0978', 'VAR_0979',
    'VAR_0980', 'VAR_0981', 'VAR_0982', 'VAR_0983', 'VAR_0984', 'VAR_0985', 'VAR_0986',
    'VAR_0987', 'VAR_0988', 'VAR_0989', 'VAR_0990', 'VAR_0991', 'VAR_0992', 'VAR_0993',
    'VAR_0994', 'VAR_0995', 'VAR_0996', 'VAR_0997', 'VAR_0998', 'VAR_0999', 'VAR_1000',
    'VAR_1001', 'VAR_1002', 'VAR_1003', 'VAR_1004', 'VAR_1005', 'VAR_1006', 'VAR_1007',
    'VAR_1008', 'VAR_1009', 'VAR_1010', 'VAR_1011', 'VAR_1012', 'VAR_1013', 'VAR_1014',
    'VAR_1015', 'VAR_1016', 'VAR_1017', 'VAR_1018', 'VAR_1019', 'VAR_1020', 'VAR_1021',
    'VAR_1022', 'VAR_1023', 'VAR_1024', 'VAR_1025', 'VAR_1026', 'VAR_1027', 'VAR_1028',
    'VAR_1029', 'VAR_1030', 'VAR_1031', 'VAR_1032', 'VAR_1033', 'VAR_1034', 'VAR_1035',
    'VAR_1036', 'VAR_1037', 'VAR_1038', 'VAR_1039', 'VAR_1040', 'VAR_1041', 'VAR_1042',
    'VAR_1043', 'VAR_1044', 'VAR_1045', 'VAR_1046', 'VAR_1047', 'VAR_1048', 'VAR_1049',
    'VAR_1050', 'VAR_1051', 'VAR_1052', 'VAR_1053', 'VAR_1054', 'VAR_1055', 'VAR_1056',
    'VAR_1057', 'VAR_1058', 'VAR_1059', 'VAR_1060', 'VAR_1061', 'VAR_1062', 'VAR_1063',
    'VAR_1064', 'VAR_1065', 'VAR_1066', 'VAR_1067', 'VAR_1068', 'VAR_1069', 'VAR_1070',
    'VAR_1071', 'VAR_1072', 'VAR_1073', 'VAR_1074', 'VAR_1075', 'VAR_1076', 'VAR_1077',
    'VAR_1078', 'VAR_1079', 'VAR_1080', 'VAR_1081', 'VAR_1082', 'VAR_1083', 'VAR_1084',
    'VAR_1085', 'VAR_1086', 'VAR_1087', 'VAR_1088', 'VAR_1089', 'VAR_1090', 'VAR_1091',
    'VAR_1092', 'VAR_1093', 'VAR_1094', 'VAR_1095', 'VAR_1096', 'VAR_1097', 'VAR_1098',
    'VAR_1099', 'VAR_1100', 'VAR_1101', 'VAR_1102', 'VAR_1103', 'VAR_1104', 'VAR_1105',
    'VAR_1106', 'VAR_1107', 'VAR_1108', 'VAR_1109', 'VAR_1110', 'VAR_1111', 'VAR_1112',
    'VAR_1113', 'VAR_1114', 'VAR_1115', 'VAR_1116', 'VAR_1117', 'VAR_1118', 'VAR_1119',
    'VAR_1120', 'VAR_1121', 'VAR_1122', 'VAR_1123', 'VAR_1124', 'VAR_1125', 'VAR_1126',
    'VAR_1127', 'VAR_1128', 'VAR_1129', 'VAR_1130', 'VAR_1131', 'VAR_1132', 'VAR_1133',
    'VAR_1134', 'VAR_1135', 'VAR_1136', 'VAR_1137', 'VAR_1138', 'VAR_1139', 'VAR_1140',
    'VAR_1141', 'VAR_1142', 'VAR_1143', 'VAR_1144', 'VAR_1145', 'VAR_1146', 'VAR_1147',
    'VAR_1148', 'VAR_1149', 'VAR_1150', 'VAR_1151', 'VAR_1152', 'VAR_1153', 'VAR_1154',
    'VAR_1155', 'VAR_1156', 'VAR_1157', 'VAR_1158', 'VAR_1159', 'VAR_1160', 'VAR_1161',
    'VAR_1162', 'VAR_1163', 'VAR_1164', 'VAR_1165', 'VAR_1166', 'VAR_1167', 'VAR_1168',
    'VAR_1169', 'VAR_1170', 'VAR_1171', 'VAR_1172', 'VAR_1173', 'VAR_1174', 'VAR_1175',
    'VAR_1176', 'VAR_1177', 'VAR_1178', 'VAR_1179', 'VAR_1180', 'VAR_1181', 'VAR_1182',
    'VAR_1183', 'VAR_1184', 'VAR_1185', 'VAR_1186', 'VAR_1187', 'VAR_1188', 'VAR_1189',
    'VAR_1190', 'VAR_1191', 'VAR_1192', 'VAR_1193', 'VAR_1194', 'VAR_1195', 'VAR_1196',
    'VAR_1197', 'VAR_1198', 'VAR_1199', 'VAR_1200', 'VAR_1201', 'VAR_1202', 'VAR_1203',
    'VAR_1204', 'VAR_1205', 'VAR_1206', 'VAR_1207', 'VAR_1208', 'VAR_1209', 'VAR_1210',
    'VAR_1211', 'VAR_1212', 'VAR_1213', 'VAR_1214', 'VAR_1215', 'VAR_1216', 'VAR_1217',
    'VAR_1218', 'VAR_1219', 'VAR_1220', 'VAR_1221', 'VAR_1222', 'VAR_1223', 'VAR_1224',
    'VAR_1225', 'VAR_1226', 'VAR_1227', 'VAR_1228', 'VAR_1229', 'VAR_1230', 'VAR_1231',
    'VAR_1232', 'VAR_1233', 'VAR_1234', 'VAR_1235', 'VAR_1236', 'VAR_1237', 'VAR_1238',
    'VAR_1239', 'VAR_1240', 'VAR_1241', 'VAR_1242', 'VAR_1243', 'VAR_1244', 'VAR_1245',
    'VAR_1246', 'VAR_1247', 'VAR_1248', 'VAR_1249', 'VAR_1250', 'VAR_1251', 'VAR_1252',
    'VAR_1253', 'VAR_1254', 'VAR_1255', 'VAR_1256', 'VAR_1257', 'VAR_1258', 'VAR_1259',
    'VAR_1260', 'VAR_1261', 'VAR_1262', 'VAR_1263', 'VAR_1264', 'VAR_1265', 'VAR_1266',
    'VAR_1267', 'VAR_1268', 'VAR_1269', 'VAR_1270', 'VAR_1271', 'VAR_1272', 'VAR_1273',
    'VAR_1274', 'VAR_1275', 'VAR_1276', 'VAR_1277', 'VAR_1278', 'VAR_1279', 'VAR_1280',
    'VAR_1281', 'VAR_1282', 'VAR_1283', 'VAR_1284', 'VAR_1285', 'VAR_1286', 'VAR_1287',
    'VAR_1288', 'VAR_1289', 'VAR_1290', 'VAR_1291', 'VAR_1292', 'VAR_1293', 'VAR_1294',
    'VAR_1295', 'VAR_1296', 'VAR_1297', 'VAR_1298', 'VAR_1299', 'VAR_1300', 'VAR_1301',
    'VAR_1302', 'VAR_1303', 'VAR_1304', 'VAR_1305', 'VAR_1306', 'VAR_1307', 'VAR_1308',
    'VAR_1309', 'VAR_1310', 'VAR_1311', 'VAR_1312', 'VAR_1313', 'VAR_1314', 'VAR_1315',
    'VAR_1316', 'VAR_1317', 'VAR_1318', 'VAR_1319', 'VAR_1320', 'VAR_1321', 'VAR_1322',
    'VAR_1323', 'VAR_1324', 'VAR_1325', 'VAR_1326', 'VAR_1327', 'VAR_1328', 'VAR_1329',
    'VAR_1330', 'VAR_1331', 'VAR_1332', 'VAR_1333', 'VAR_1334', 'VAR_1335', 'VAR_1336',
    'VAR_1337', 'VAR_1338', 'VAR_1339', 'VAR_1340', 'VAR_1341', 'VAR_1342', 'VAR_1343',
    'VAR_1344', 'VAR_1345', 'VAR_1346', 'VAR_1347', 'VAR_1348', 'VAR_1349', 'VAR_1350',
    'VAR_1351', 'VAR_1352', 'VAR_1353', 'VAR_1354', 'VAR_1355', 'VAR_1356', 'VAR_1357',
    'VAR_1358', 'VAR_1359', 'VAR_1360', 'VAR_1361', 'VAR_1362', 'VAR_1363', 'VAR_1364',
    'VAR_1365', 'VAR_1366', 'VAR_1367', 'VAR_1368', 'VAR_1369', 'VAR_1370', 'VAR_1371',
    'VAR_1372', 'VAR_1373', 'VAR_1374', 'VAR_1375', 'VAR_1376', 'VAR_1377', 'VAR_1378',
    'VAR_1379', 'VAR_1380', 'VAR_1381', 'VAR_1382', 'VAR_1383', 'VAR_1384', 'VAR_1385',
    'VAR_1386', 'VAR_1387', 'VAR_1388', 'VAR_1389', 'VAR_1390', 'VAR_1391', 'VAR_1392',
    'VAR_1393', 'VAR_1394', 'VAR_1395', 'VAR_1396', 'VAR_1397', 'VAR_1398', 'VAR_1399',
    'VAR_1400', 'VAR_1401', 'VAR_1402', 'VAR_1403', 'VAR_1404', 'VAR_1405', 'VAR_1406',
    'VAR_1407', 'VAR_1408', 'VAR_1409', 'VAR_1410', 'VAR_1411', 'VAR_1412', 'VAR_1413',
    'VAR_1414', 'VAR_1415', 'VAR_1416', 'VAR_1417', 'VAR_1418', 'VAR_1419', 'VAR_1420',
    'VAR_1421', 'VAR_1422', 'VAR_1423', 'VAR_1424', 'VAR_1425', 'VAR_1426', 'VAR_1427',
    'VAR_1429', 'VAR_1430', 'VAR_1431', 'VAR_1432', 'VAR_1433', 'VAR_1434', 'VAR_1435',
    'VAR_1436', 'VAR_1437', 'VAR_1438', 'VAR_1439', 'VAR_1440', 'VAR_1441', 'VAR_1442',
    'VAR_1443', 'VAR_1444', 'VAR_1445', 'VAR_1446', 'VAR_1447', 'VAR_1448', 'VAR_1449',
    'VAR_1450', 'VAR_1451', 'VAR_1452', 'VAR_1453', 'VAR_1454', 'VAR_1455', 'VAR_1456',
    'VAR_1457', 'VAR_1458', 'VAR_1459', 'VAR_1460', 'VAR_1461', 'VAR_1462', 'VAR_1463',
    'VAR_1464', 'VAR_1465', 'VAR_1466', 'VAR_1467', 'VAR_1468', 'VAR_1469', 'VAR_1470',
    'VAR_1471', 'VAR_1472', 'VAR_1473', 'VAR_1474', 'VAR_1475', 'VAR_1476', 'VAR_1477',
    'VAR_1478', 'VAR_1479', 'VAR_1480', 'VAR_1481', 'VAR_1482', 'VAR_1483', 'VAR_1484',
    'VAR_1485', 'VAR_1486', 'VAR_1487', 'VAR_1488', 'VAR_1489', 'VAR_1490', 'VAR_1491',
    'VAR_1492', 'VAR_1493', 'VAR_1494', 'VAR_1495', 'VAR_1496', 'VAR_1497', 'VAR_1498',
    'VAR_1499', 'VAR_1500', 'VAR_1501', 'VAR_1502', 'VAR_1503', 'VAR_1504', 'VAR_1505',
    'VAR_1506', 'VAR_1507', 'VAR_1508', 'VAR_1509', 'VAR_1510', 'VAR_1511', 'VAR_1512',
    'VAR_1513', 'VAR_1514', 'VAR_1515', 'VAR_1516', 'VAR_1517', 'VAR_1518', 'VAR_1519',
    'VAR_1520', 'VAR_1521', 'VAR_1522', 'VAR_1523', 'VAR_1524', 'VAR_1525', 'VAR_1526',
    'VAR_1527', 'VAR_1528', 'VAR_1529', 'VAR_1530', 'VAR_1531', 'VAR_1532', 'VAR_1533',
    'VAR_1534', 'VAR_1535', 'VAR_1536', 'VAR_1537', 'VAR_1538', 'VAR_1539', 'VAR_1540',
    'VAR_1541', 'VAR_1542', 'VAR_1543', 'VAR_1544', 'VAR_1545', 'VAR_1546', 'VAR_1547',
    'VAR_1548', 'VAR_1549', 'VAR_1550', 'VAR_1551', 'VAR_1552', 'VAR_1553', 'VAR_1554',
    'VAR_1555', 'VAR_1556', 'VAR_1557', 'VAR_1558', 'VAR_1559', 'VAR_1560', 'VAR_1561',
    'VAR_1562', 'VAR_1563', 'VAR_1564', 'VAR_1565', 'VAR_1566', 'VAR_1567', 'VAR_1568',
    'VAR_1569', 'VAR_1570', 'VAR_1571', 'VAR_1572', 'VAR_1573', 'VAR_1574', 'VAR_1575',
    'VAR_1576', 'VAR_1577', 'VAR_1578', 'VAR_1579', 'VAR_1580', 'VAR_1581', 'VAR_1582',
    'VAR_1583', 'VAR_1584', 'VAR_1585', 'VAR_1586', 'VAR_1587', 'VAR_1588', 'VAR_1589',
    'VAR_1590', 'VAR_1591', 'VAR_1592', 'VAR_1593', 'VAR_1594', 'VAR_1595', 'VAR_1596',
    'VAR_1597', 'VAR_1598', 'VAR_1599', 'VAR_1600', 'VAR_1601', 'VAR_1602', 'VAR_1603',
    'VAR_1604', 'VAR_1605', 'VAR_1606', 'VAR_1607', 'VAR_1608', 'VAR_1609', 'VAR_1610',
    'VAR_1611', 'VAR_1612', 'VAR_1613', 'VAR_1614', 'VAR_1615', 'VAR_1616', 'VAR_1617',
    'VAR_1618', 'VAR_1619', 'VAR_1620', 'VAR_1621', 'VAR_1622', 'VAR_1623', 'VAR_1624',
    'VAR_1625', 'VAR_1626', 'VAR_1627', 'VAR_1628', 'VAR_1629', 'VAR_1630', 'VAR_1631',
    'VAR_1632', 'VAR_1633', 'VAR_1634', 'VAR_1635', 'VAR_1636', 'VAR_1637', 'VAR_1638',
    'VAR_1639', 'VAR_1640', 'VAR_1641', 'VAR_1642', 'VAR_1643', 'VAR_1644', 'VAR_1645',
    'VAR_1646', 'VAR_1647', 'VAR_1648', 'VAR_1649', 'VAR_1650', 'VAR_1651', 'VAR_1652',
    'VAR_1653', 'VAR_1654', 'VAR_1655', 'VAR_1656', 'VAR_1657', 'VAR_1658', 'VAR_1659',
    'VAR_1660', 'VAR_1661', 'VAR_1662', 'VAR_1663', 'VAR_1664', 'VAR_1665', 'VAR_1666',
    'VAR_1667', 'VAR_1668', 'VAR_1669', 'VAR_1670', 'VAR_1671', 'VAR_1672', 'VAR_1673',
    'VAR_1674', 'VAR_1675', 'VAR_1676', 'VAR_1677', 'VAR_1678', 'VAR_1679', 'VAR_1680',
    'VAR_1681', 'VAR_1682', 'VAR_1683', 'VAR_1684', 'VAR_1685', 'VAR_1686', 'VAR_1687',
    'VAR_1688', 'VAR_1689', 'VAR_1690', 'VAR_1691', 'VAR_1692', 'VAR_1693', 'VAR_1694',
    'VAR_1695', 'VAR_1696', 'VAR_1697', 'VAR_1698', 'VAR_1699', 'VAR_1700', 'VAR_1701',
    'VAR_1702', 'VAR_1703', 'VAR_1704', 'VAR_1705', 'VAR_1706', 'VAR_1707', 'VAR_1708',
    'VAR_1709', 'VAR_1710', 'VAR_1711', 'VAR_1712', 'VAR_1713', 'VAR_1714', 'VAR_1715',
    'VAR_1716', 'VAR_1717', 'VAR_1718', 'VAR_1719', 'VAR_1720', 'VAR_1721', 'VAR_1722',
    'VAR_1723', 'VAR_1724', 'VAR_1725', 'VAR_1726', 'VAR_1727', 'VAR_1728', 'VAR_1729',
    'VAR_1730', 'VAR_1731', 'VAR_1732', 'VAR_1733', 'VAR_1734', 'VAR_1735', 'VAR_1736',
    'VAR_1737', 'VAR_1738', 'VAR_1739', 'VAR_1740', 'VAR_1741', 'VAR_1742', 'VAR_1743',
    'VAR_1744', 'VAR_1745', 'VAR_1746', 'VAR_1747', 'VAR_1748', 'VAR_1749', 'VAR_1750',
    'VAR_1751', 'VAR_1752', 'VAR_1753', 'VAR_1754', 'VAR_1755', 'VAR_1756', 'VAR_1757',
    'VAR_1758', 'VAR_1759', 'VAR_1760', 'VAR_1761', 'VAR_1762', 'VAR_1763', 'VAR_1764',
    'VAR_1765', 'VAR_1766', 'VAR_1767', 'VAR_1768', 'VAR_1769', 'VAR_1770', 'VAR_1771',
    'VAR_1772', 'VAR_1773', 'VAR_1774', 'VAR_1775', 'VAR_1776', 'VAR_1777', 'VAR_1778',
    'VAR_1779', 'VAR_1780', 'VAR_1781', 'VAR_1782', 'VAR_1783', 'VAR_1784', 'VAR_1785',
    'VAR_1786', 'VAR_1787', 'VAR_1788', 'VAR_1789', 'VAR_1790', 'VAR_1791', 'VAR_1792',
    'VAR_1793', 'VAR_1794', 'VAR_1795', 'VAR_1796', 'VAR_1797', 'VAR_1798', 'VAR_1799',
    'VAR_1800', 'VAR_1801', 'VAR_1802', 'VAR_1803', 'VAR_1804', 'VAR_1805', 'VAR_1806',
    'VAR_1807', 'VAR_1808', 'VAR_1809', 'VAR_1810', 'VAR_1811', 'VAR_1812', 'VAR_1813',
    'VAR_1814', 'VAR_1815', 'VAR_1816', 'VAR_1817', 'VAR_1818', 'VAR_1819', 'VAR_1820',
    'VAR_1821', 'VAR_1822', 'VAR_1823', 'VAR_1824', 'VAR_1825', 'VAR_1826', 'VAR_1827',
    'VAR_1828', 'VAR_1829', 'VAR_1830', 'VAR_1831', 'VAR_1832', 'VAR_1833', 'VAR_1834',
    'VAR_1835', 'VAR_1836', 'VAR_1837', 'VAR_1838', 'VAR_1839', 'VAR_1840', 'VAR_1841',
    'VAR_1842', 'VAR_1843', 'VAR_1844', 'VAR_1845', 'VAR_1846', 'VAR_1847', 'VAR_1848',
    'VAR_1849', 'VAR_1850', 'VAR_1851', 'VAR_1852', 'VAR_1853', 'VAR_1854', 'VAR_1855',
    'VAR_1856', 'VAR_1857', 'VAR_1858', 'VAR_1859', 'VAR_1860', 'VAR_1861', 'VAR_1862',
    'VAR_1863', 'VAR_1864', 'VAR_1865', 'VAR_1866', 'VAR_1867', 'VAR_1868', 'VAR_1869',
    'VAR_1870', 'VAR_1871', 'VAR_1872', 'VAR_1873', 'VAR_1874', 'VAR_1875', 'VAR_1876',
    'VAR_1877', 'VAR_1878', 'VAR_1879', 'VAR_1880', 'VAR_1881', 'VAR_1882', 'VAR_1883',
    'VAR_1884', 'VAR_1885', 'VAR_1886', 'VAR_1887', 'VAR_1888', 'VAR_1889', 'VAR_1890',
    'VAR_1891', 'VAR_1892', 'VAR_1893', 'VAR_1894', 'VAR_1895', 'VAR_1896', 'VAR_1897',
    'VAR_1898', 'VAR_1899', 'VAR_1900', 'VAR_1901', 'VAR_1902', 'VAR_1903', 'VAR_1904',
    'VAR_1905', 'VAR_1906', 'VAR_1907', 'VAR_1908', 'VAR_1909', 'VAR_1910', 'VAR_1911',
    'VAR_1912', 'VAR_1913', 'VAR_1914', 'VAR_1915', 'VAR_1916', 'VAR_1917', 'VAR_1918',
    'VAR_1919', 'VAR_1920', 'VAR_1921', 'VAR_1922', 'VAR_1923', 'VAR_1924', 'VAR_1925',
    'VAR_1926', 'VAR_1927', 'VAR_1928', 'VAR_1929', 'VAR_1930', 'VAR_1931', 'VAR_1932',
    'VAR_1933', 'VAR_1934']
DATE_COLUMN_NAMES =[
    'VAR_0073', 'VAR_0075',
    'VAR_0156', 'VAR_0157', 'VAR_0158', 'VAR_0159',
    'VAR_0166', 'VAR_0167', 'VAR_0168', 'VAR_0169',
    'VAR_0176', 'VAR_0177', 'VAR_0178', 'VAR_0179',
    'VAR_0204', 'VAR_0217']


def print_memory_usage():
    print('consuming {:.2f}GB RAM'.format(
           psutil.Process(os.getpid()).get_memory_info().rss / 1073741824),
          flush=True)


"""
'VAR_0207', 'VAR_0213', 'VAR_0840', 'VAR_0847', and 'VAR_1428' are constants

def get_constant_columns(df, constant_columns=None):
    if constant_columns is None:
        card = df.apply(lambda x: x.nunique(dropna=False), axis=0)
        constant_columns = card[card == 1].index.values.tolist()
    return constant_columns
"""


def get_df(csv_path, n_rows=None, column_names=None):
    print('loading {} rows from {}'.format('all' if n_rows is None else n_rows, csv_path),
          flush=True)
    if column_names == ['ID'] or column_names == ['target']:
        date_columns = False
        dtype_map = {'ID': 'uint32'} if column_names == ['ID'] else {'target': 'uint8'}
    else:
        date_columns = DATE_COLUMN_NAMES
        dtype_map = FEATURE_DTYPES
    df = pd.read_csv(csv_path,
                     nrows=n_rows,
                     usecols=column_names,
                     dtype=dtype_map,
                     parse_dates=date_columns,
                     date_parser=lambda t: pd.to_datetime(t, format='%d%b%y:%H:%M:%S'))
    sys.stderr.flush()
    print('{} loaded'.format(df.shape))
    return df


def get_X_df(csv_file_path, n_rows_with_header=None):
    return get_df(csv_path=csv_file_path, n_rows=n_rows_with_header, column_names=FEATURE_COLUMN_NAMES)


def get_train_X_df(train_csv_path='../input/train.csv', n_rows_with_caption=None):
    return get_X_df(csv_file_path=train_csv_path, n_rows_with_header=n_rows_with_caption)


def get_train_y_values(train_csv_path='../input/train.csv', n_rows_with_caption=None):
    return get_df(csv_path=train_csv_path, n_rows=n_rows_with_caption, column_names=['target']).values.ravel()


def get_test_X_df(test_csv_path='../input/test.csv', n_rows_with_caption=None):
    return get_X_df(csv_file_path=test_csv_path, n_rows_with_header=n_rows_with_caption)


def get_test_id_df(test_csv_path='../input/test.csv', n_rows_with_caption=None):
    return get_df(csv_path=test_csv_path, n_rows=n_rows_with_caption, column_names=['ID'])


def evaluate(estimator, dev_X, dev_y):
    print('evaluating on development set', flush=True)
    guess_dev = estimator.predict(dev_X)
    score_roc_auc_dev = roc_auc_score(dev_y, guess_dev)
    print('{:.4f} -- roc auc'.format(score_roc_auc_dev))
    score_brier_loss_dev = brier_score_loss(dev_y, guess_dev)
    print('{:.4f} -- brier loss'.format(score_brier_loss_dev))
    score_log_loss_dev = log_loss(dev_y, estimator.predict_proba(dev_X))
    print('{:.4f} -- log loss'.format(score_log_loss_dev))
    guess_dev_negative_one = guess_dev.copy().astype('int8')
    guess_dev_negative_one[guess_dev_negative_one == 0] = -1
    '''
    decision_fuction not implemented
    # score_hinge_loss_dev = hinge_loss(dev_y, estimator.decision_function(dev_X))
    '''
    score_hinge_loss_dev = hinge_loss(dev_y, guess_dev_negative_one)
    print('{:.4f} -- hinge loss'.format(score_hinge_loss_dev))
    score_matthews_corrcoef_dev = matthews_corrcoef(dev_y, guess_dev_negative_one)
    print('{:.4f} -- matthews_corrcoef'.format(score_matthews_corrcoef_dev))
    print(flush=True)

    return score_roc_auc_dev, score_brier_loss_dev,\
        score_log_loss_dev, score_hinge_loss_dev, score_matthews_corrcoef_dev


def predict(batch_size=30000, temp_test_row_count_limit=None):
    print('initializing submission df')
    submission_df = get_test_id_df(n_rows_with_caption=temp_test_row_count_limit)
    submission_df['target'] = 0.0
    print('{} initialized'.format(submission_df.shape))

    test_X_df = get_test_X_df(n_rows_with_caption=test_row_count_limit)

    total_row_count = submission_df.shape[0]
    slice_row_count = batch_size if batch_size is not None else total_row_count
    final_slice_offset = total_row_count - total_row_count % slice_row_count
    score_list = []
    for offset in range(0, total_row_count, slice_row_count):
        slice_upper_bound = offset + slice_row_count
        if offset == final_slice_offset:
            slice_upper_bound = total_row_count
        print('predicting rows [{}, {}]'.format(offset, slice_upper_bound - 1))

        print('encoding features')
        X_test = feature_encoder.transform(test_X_df.iloc[offset:slice_upper_bound])
        print('{} encoded'.format(X_test.shape), flush=True)

        print('selecting features')
        X_test = feature_selector.transform(X_test)
        print('{} selected'.format(X_test.shape), flush=True)

        score_list.extend(clf.predict_proba(X_test)[:, 1])
        print('predicted')
    submission_df.loc[:, 'target'] = score_list

    return submission_df


class DTypeSelector(BaseEstimator, TransformerMixin):
    def __init__(self, key):
        self.key = key

    def fit(self, X, y=None):
        return self

    def transform(self, data_frame):
        if self.key == 'object':
            print('transforming categorical features')
            return data_frame.select_dtypes(
                include=['object']).fillna('REAL_NA').values.astype(str)
        if self.key == 'datetime':
            print('transforming datetime features')
            return data_frame.select_dtypes(
                include=['datetime64']).values.astype('float32')
        if self.key == 'number':
            print('transforming numerical features')
            return data_frame.select_dtypes(
                include=['number'],
                exclude=['datetime64']).fillna(-2147483648).values.astype('float32')


if __name__ == '__main__':
    """
    No need for this if not using Mac OS X's Accelerate.framework

    try:
        from multiprocessing import set_start_method
    except ImportError:
        raise ImportError('Unable to import multiprocessing.set_start_method.'
                          ' This example only runs on Python 3.4+')
    set_start_method('forkserver')
    import os
    os.environ['OMP_NUM_THREADS'] = '8'
    """

    train_row_count_limit = None #100000
    dev_set_size_rate = 0.25
    test_batch_size = 50000
    test_row_count_limit = None

    datetime_pipe = Pipeline([
        ('separator', DTypeSelector(key='datetime')),
    ])
    object_pipe = Pipeline([
        ('separator', DTypeSelector(key='object')),
        ('encoder', FeatureHasher(input_type='string')),
    ])
    number_pipe = Pipeline([
        ('separator', DTypeSelector(key='number')),
    ])
    feature_encoder = FeatureUnion(transformer_list=[('number', number_pipe),
                                                     ('datetime', datetime_pipe),
                                                     ('object', object_pipe),
                                                     ])
    feature_selector = GenericUnivariateSelect(mode='fwe', param=0.001)

    train_X_df = get_train_X_df(n_rows_with_caption=train_row_count_limit)
    y = get_train_y_values(n_rows_with_caption=train_row_count_limit)

    print('encoding features')
    X = feature_encoder.fit_transform(train_X_df, y)
    print('{} encoded'.format(X.shape), flush=True)

    print('selecting features')
    X = feature_selector.fit_transform(X, y)
    print('{} selected'.format(X.shape), flush=True)

    print_memory_usage()
    print('gc collecting')
    train_X_df_ref = [train_X_df]
    del train_X_df, train_X_df_ref
    gc.collect(generation=0)
    gc.collect(generation=1)
    gc.collect(generation=2)
    print('collected')
    print_memory_usage()

    print('splitting training/development sets')
    X_train, X_dev, y_train, y_dev = train_test_split(X, y, test_size=dev_set_size_rate)
    print('{} / {} split'.format(X_train.shape, X_dev.shape), flush=True)

    print('training')
    print('initializing the classifier', flush=True)
    clf = xgb.XGBClassifier(silent=1,
                            n_estimators=220, learning_rate=0.28, max_depth=8,
                            min_child_weight=0, seed=2015)
    print('fitting', flush=True)
    clf.fit(X, y,
            eval_set=[(X_dev, y_dev)], eval_metric='logloss',
            #early_stopping_rounds=1,
            verbose=True)
    sys.stderr.flush()
    print_memory_usage()
    print('{:.1f} minutes'.format((time.perf_counter() - perf_counter_start) / 60),
          flush=True)

    score_roc_auc, score_brier_loss, score_log_loss, score_hinge_loss,\
        score_matthews_corrcoef = evaluate(clf, X_dev, y_dev)

    print('gc collecting')
    train_ref = [X_dev, y_dev, X_train, y_train, X, y]
    del X_dev, y_dev, X_train, y_train, X, y, train_ref
    gc.collect(generation=0)
    gc.collect(generation=1)
    gc.collect(generation=2)
    print('collected')
    print_memory_usage()

    prediction_df = predict(batch_size=test_batch_size,
                            temp_test_row_count_limit=test_row_count_limit)

    print('dumping to csv')
    prediction_df.to_csv('submission_xgb_a{:.4f}-b{:.4f}-h{:.4f}-l{:.4f}-m{:.4f}.csv'.format(
        score_roc_auc, score_brier_loss, score_hinge_loss,
        score_log_loss, score_matthews_corrcoef),
        index=False)
    print('dumped')

    print('{:.1f} minutes'.format((time.perf_counter() - perf_counter_start) / 60))
