# code modified from https://github.com/IBM/document2slides/blob/main/sciduet-build/extract_papers.py
import os
from os import path
import json
from dataclasses import dataclass
from multiprocessing.pool import Pool
import pandas as pd
from pathlib import Path
from bs4 import BeautifulSoup
import nltk
from dataclasses import dataclass


@dataclass
class Person:
    firstname: str
    middlename: str
    surname: str


def read_tei(tei_file):
    with open(tei_file, 'r', encoding='utf-8') as tei:
        soup = BeautifulSoup(tei, 'xml')
        return soup


def elem_to_text(elem, default=''):
    if elem:
        return elem.getText()
    else:
        return default


class TEIFile(object):

    def __init__(self, xml_pth: str = None, fig_json_pth: str = ''):
        # self.filename = filename
        # self.dir = os.path.abspath(paper_dir)
        self.xml_pth = os.path.abspath(xml_pth)
        self.fig_json_pth = os.path.abspath(fig_json_pth)
        # self.soup = read_tei(os.path.join(self.dir, 'paper.tei.xml'))
        self.soup = read_tei(self.xml_pth)
        self._text = None
        self._title = ''
        self._abstract = ''
        self._headers = None
        self._figures = None

    @property
    def doi(self):
        idno_elem = self.soup.find('idno', type='DOI')
        if not idno_elem:
            return ''
        else:
            return idno_elem.getText()

    @property
    def title(self):
        if not self._title:
            self._title = self.soup.title.getText()
        return self._title

    @property
    def abstract(self):
        if not self._abstract:
            abstract = self.soup.abstract.getText(separator=' ', strip=True)
            self._abstract = abstract
        return self._abstract

    @property
    def authors(self):
        authors_in_header = self.soup.analytic.find_all('author')

        # print(authors_in_header)

        result = []
        for author in authors_in_header:
            persname = author.persName
            if not persname:
                persname = author.persname
            if not persname:
                continue
            firstname = elem_to_text(persname.find("forename", type="first"))
            middlename = elem_to_text(persname.find("forename", type="middle"))
            surname = elem_to_text(persname.surname)
            person = Person(firstname, middlename, surname)
            result.append(person)

        return result

    @property
    def text(self):
        if not self._text:
            self._headers = []
            headerlist = self.soup.body.find_all("head")
            sections = []
            for head in headerlist:
                if head.parent.name == 'div':
                    txt = head.parent.get_text(separator=' ', strip=True)
                    if head.get("n"):
                        sections.append([head.text, head.get('n'), txt])
                    else:
                        if len(sections) == 0:
                            print("Grobid processing error.")
                        sections[-1][2] += txt
            start = 0
            for i in sections:
                sent = nltk.tokenize.sent_tokenize(i[2])
                sec_dic = {'section': i[0], 'n': i[1], 'start': start, 'end': start + len(sent) - 1}
                self._headers.append(sec_dic)
                start += len(sent)
            plain_text = " ".join([i[2] for i in sections])
            self._text = [{'id': i, 'string': s} for i, s in enumerate(nltk.tokenize.sent_tokenize(plain_text))]
        return self._text

    @property
    def headers(self):
        if not self._headers:
            self.text()
        return self._headers

    @property
    def figures(self):
        if not self._figures:
            # base_name = basename_without_ext(self.filename)
            self._figures = []
            # fn = 'figures/{}.json'.format(base_name)  # link to figures dir
            # fn = os.path.join(self.dir, 'paper_figure/paper.json')
            fn = self.fig_json_pth
            if not path.isfile(fn):
                return []
            with open(fn) as f:
                data = json.load(f)
            for i in data:
                elem = {'filename': i['renderURL'], 'caption': i['caption'], 'page': i['page'], 'bbox': i['regionBoundary']}
                self._figures.append(elem)
        return self._figures


def single_entry(uuid: str, xml_pth: str, fig_json_pth: str):
    tei = TEIFile(xml_pth=xml_pth, fig_json_pth=fig_json_pth)
    return uuid, tei.title, tei.abstract, tei.text, tei.headers, tei.figures


if __name__ == '__main__':

    repo_dir = './'
    data_dir = os.path.abspath(repo_dir + 'data')
    collection_names = [Path(file).stem for file in os.listdir(data_dir)]

    for name in collection_names:
        print(name)
        collection_dir = os.path.join(data_dir, name)

        figure_dir = os.path.join(collection_dir, 'figure')
        xml_dir = os.path.join(collection_dir, 'xml')
        json_dir = os.path.join(collection_dir, 'json')
        if not os.path.exists(json_dir):
            os.makedirs(json_dir)

        data = pd.read_csv(os.path.join(collection_dir, 'list.csv'), index_col='uuid')

        args = []
        for uuid, item in data.iterrows():
            xml_pth = os.path.join(xml_dir, uuid + '.tei.xml')
            fig_json_pth = os.path.join(figure_dir, 'json', uuid + '.json')
            args.append((uuid, xml_pth, fig_json_pth))

        pool = Pool()
        entries = pool.starmap(single_entry, args)
        result_df = pd.DataFrame(entries, columns=['UUID', 'Title', 'Abstract', 'Text', 'Headers', 'Figs'])
        print(result_df.head())

        # pkl and json are the same information
        result_df.to_pickle(os.path.join(collection_dir, 'papers_data.pkl'))

        # json
        for _, row in result_df.iterrows():
            json_data = {
                'title': row['Title'],
                'abstract': row['Abstract'],
                'text': row['Text'],
                'headers': row['Headers'],
                'figures': row['Figs'],
            }

            with open(os.path.join(json_dir, row['UUID'] + '.json'), 'w') as f:
                json.dump(json_data, f, indent=4)
