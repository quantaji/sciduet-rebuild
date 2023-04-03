import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score
import os
from os import path
import json
from pathlib import Path
from tqdm import tqdm
import nlp
import re
import numpy as np

if __name__ == '__main__':

    repo_dir = './'
    data_dir = os.path.abspath(repo_dir + 'data')
    collection_names = [Path(file).stem for file in os.listdir(data_dir)]

    datas = []

    for name in collection_names:
        print(name)
        collection_dir = os.path.join(data_dir, name)
        collection_data_pth = os.path.join(collection_dir, 'data.pkl')

        datas.append(pd.read_pickle(collection_data_pth))

    data = pd.concat(datas)
    print(data.head(), data.size, data['uuid'].size)

    data.to_pickle(os.path.join(data_dir, 'data.pkl'))
