# This Python 3 environment comes with many helpful analytics libraries installed
# It is defined by the kaggle/python docker image: https://github.com/kaggle/docker-python
# For example, here's several helpful packages to load in 

import numpy as np # linear algebra
import pandas as pd # data processing, CSV file I/O (e.g. pd.read_csv)

# Input data files are available in the "../input/" directory.
# For example, running this (by clicking run or pressing Shift+Enter) will list the files in the input directory

from subprocess import check_output
print(check_output(["ls", "../input"]).decode("utf8"))

df = pd.read_csv("../input/train.csv", nrows = 1000)
print(df.shape)
list1 = sorted(df.columns)
df = pd.read_csv("../input/test.csv", nrows = 1000)
print(df.shape)
list2 = sorted(df.columns)
print(set(list1)-set(list2))
print(list1)
print(set(list2)-set(list1))
print(list2)
# Any results you write to the current directory are saved as output.