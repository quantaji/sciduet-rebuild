# from glob import glob
from unidecode import unidecode
import string
import os
from pathlib import Path
import pandas as pd
from tqdm import tqdm
import json
import subprocess


def pdf_to_txt(pdf_pth):
    text_pth = os.path.join(os.getcwd(), 'temp')
    # os.system()
    command = "pdftotext {} {}".format(pdf_pth, text_pth)
    return subprocess.check_output(command, shell=True)  #could be anything here.


def remove_temp_txt():
    text_pth = os.path.join(os.getcwd(), 'temp')
    if os.path.exists(text_pth):
        os.remove(text_pth)


def modified_jaccard_text_similarity(str1, str2):
    a = set(str1.split())
    if len(a) == 0:
        return 1.0
    b = set(str2.split())
    c = a.intersection(b)
    return float(len(c) / len(a))


def txt_to_json(txt_pth=os.path.join(os.getcwd(), 'temp')):
    tmp_slide = []
    with open(txt_pth, 'r', encoding='utf-8') as f:
        deck = f.read().split('\f')
        for page in deck[:-1]:
            to_keep = []
            lines = page.split('\n')
            title = ""
            for idx, line in enumerate(lines):
                if "sha1" in line:
                    continue
                line = unidecode(line)
                if len(line) < 2:
                    continue
                nospace = line.replace(' ', '')
                if len(nospace) == 0:
                    continue
                if sum(c in string.ascii_letters for c in nospace) / len(nospace) < 0.75:
                    continue
                if idx == 0 or title == "":
                    title = line
                    continue
                if len(to_keep) > 0 and line[0] in string.ascii_lowercase:
                    to_keep[-1] += " " + line
                    continue
                to_keep.append(line)
            to_keep = [sent for sent in to_keep if len(sent.split()) > 3]

            tmp_slide.append({
                'title': title,
                'text': to_keep,
            })

    # now we cleanup, their might be several pages for single slides, we use the last page's text and also record the pages correspondence
    slide = []

    page_stack = []
    for i in range(len(tmp_slide)):
        page_stack.append(i)
        # similar = True

        if i + 1 < len(tmp_slide) and modified_jaccard_text_similarity(
                str1=' '.join(tmp_slide[i]['text']),
                str2=' '.join(tmp_slide[i + 1]['text']),
        ) > 0.8:
            continue  # current page is redundant, to next slide
        else:
            # next page is different
            cleaned = []
            for line in tmp_slide[i]['text']:
                line = line.strip()
                if len(line) < 3:
                    continue
                if line[1] == ' ':
                    line = line[2:]
                line = line.strip()
                cleaned.append(line)
            slide.append({
                'id': len(slide),
                'page_nums': page_stack,
                'title': tmp_slide[i]['title'],
                'text': cleaned,
            })
            page_stack = []

    return slide


def slide2json(slide_pth):
    stdout = pdf_to_txt(slide_pth)

    # print('****----', stdout)

    return txt_to_json()


if __name__ == '__main__':

    repo_dir = './'
    data_dir = os.path.abspath(repo_dir + 'data')
    collection_names = [Path(file).stem for file in os.listdir(data_dir)]

    for name in collection_names:
        print(name)
        collection_dir = os.path.join(data_dir, name)

        slide_dir = os.path.join(collection_dir, 'slide')
        slide_json_dir = os.path.join(collection_dir, 'slide_json')
        if not os.path.exists(slide_json_dir):
            os.makedirs(slide_json_dir)

        data = pd.read_csv(os.path.join(collection_dir, 'list.csv'), index_col='uuid')

        # for uuid, item in data[:10].iterrows():
        for uuid, item in tqdm(data.iterrows()):
            slide_pdf_pth = os.path.join(slide_dir, uuid + '.pdf')
            slide_json_pth = os.path.join(slide_json_dir, uuid + '.json')
            json_data = {
                'slide': slide2json(slide_pdf_pth),
            }

            with open(slide_json_pth, 'w') as f:
                json.dump(json_data, f, indent=4)
