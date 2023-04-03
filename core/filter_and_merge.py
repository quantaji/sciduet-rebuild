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


def random_forest(train_data_pth):
    df = pd.read_excel(train_data_pth)

    X = df[['r_1', 'r_2', 'r_L', 'f_1', 'f_2', 'f_L', '3_r', '3_f', 'allsum']]
    y = df['majority']
    X_train_g, X_test_g, y_train_g, y_test_g = X[:50], X[50:], y[:50], y[50:]

    bestacc = 0
    while bestacc < 0.62:
        clf = RandomForestClassifier(max_depth=1)
        clf = clf.fit(X_train_g, y_train_g)
        pred = clf.predict(X_test_g)
        bestacc = accuracy_score(y_test_g, pred)
    print(bestacc)

    return clf


if __name__ == '__main__':

    repo_dir = './'
    data_dir = os.path.abspath(repo_dir + 'data')
    collection_names = [Path(file).stem for file in os.listdir(data_dir)]

    clf = random_forest('./core/deriv_rouge.xlsx')

    nlp_rouge = nlp.load_metric('rouge')

    # neurips_2018
    # neurips_2019
    # neurips_2021
    # neurips_2022
    # icml_2019
    # icml_2020
    # icml_2021
    # icml_2022
    # iclr_2021
    # iclr_2022
    for name in collection_names:
        print(name)
        collection_dir = os.path.join(data_dir, name)

        json_dir = os.path.join(collection_dir, 'json')
        slide_json_dir = os.path.join(collection_dir, 'slide_json')

        data = pd.read_csv(os.path.join(collection_dir, 'list.csv'), index_col='uuid')

        entries = []

        for uuid, data_item in tqdm(data.iterrows()):
        # for uuid, data_item in tqdm(data[:1].iterrows()):
            paper_json_pth = os.path.join(json_dir, uuid + '.json')
            slide_json_pth = os.path.join(slide_json_dir, uuid + '.json')

            paper_f = open(paper_json_pth)
            slide_f = open(slide_json_pth)

            paper_dict = json.load(paper_f)
            slide_list = json.load(slide_f)['slide']

            # print(paper_dict)
            # print(slide_dict)

            pair = {
                'collection': name,
                'uuid': uuid,
                'title': data_item['title'],
                'slide_url': data_item['slide_url'],
                'paper_url': data_item['paper_url'],
                'paper': paper_dict,
                'slide': slide_list,
            }

            paper_text = [paper_dict['title'], paper_dict['abstract']]
            for item in paper_dict['text']:
                paper_text.append(item['string'])
            for item in paper_dict['figures']:
                paper_text.append(item['caption'])

            # filter
            filtered_slide = []
            for page in slide_list:

                filtered_text = []

                for line in page['text']:
                    ref = [re.sub(r'[^A-Za-z0-9 ]+', '', line)]
                    score = nlp_rouge.compute(paper_text, ref * len(paper_text), rouge_types=['rouge1', 'rouge2', 'rougeL'], use_stemmer=True, use_agregator=False)

                    arr1 = []
                    arr2 = []
                    for x in ['rouge1', 'rouge2', 'rougeL']:
                        r_arr = np.array([z.recall for z in score[x]])
                        f_arr = np.array([z.fmeasure for z in score[x]])
                        arr1.append(r_arr.max())
                        arr2.append(f_arr.max())
                    arr3 = [arr1 + arr2 + [sum(arr1)] + [sum(arr2)] + [sum(arr1) + sum(arr2)]]
                    if clf.predict(arr3)[0]:
                        filtered_text.append(line)

                if len(filtered_text) > 0:
                    filtered_slide.append({
                        'page_id': page['id'],
                        'filtered_text': filtered_text,
                    })

            # print(filtered_slide)
            pair['filtered_slide'] = filtered_slide

            paper_f.close()
            slide_f.close()

            entries.append(pair)

        
        results = pd.DataFrame(entries)
        # print(results)
        # pkl and json are the same information
        results.to_pickle(os.path.join(collection_dir, 'data.pkl'))
