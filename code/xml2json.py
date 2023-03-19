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


def test_xml_valid(filename: str, xml_pth: str, fig_json_pth: str = '') -> bool:
    try:
        test = TEIFile(xml_pth=xml_pth, fig_json_pth=fig_json_pth)
        test_property = {
            'doi': test.doi,
            'title': test.title,
            'abstract': test.abstract,
            'authors': test.authors,
            'text': test.text,
            'headers': test.headers,
            'figures': test.figures,
        }
        return filename, True
    except:
        return filename, False


if __name__ == '__main__':

    urls_dir = os.path.abspath('./initial_data/stage_2/extracted_url/')
    csv_list = os.listdir(urls_dir)
    xml2json_test_dir = os.path.abspath('./initial_data/stage_2/xml2json_test/')
    if not os.path.exists(xml2json_test_dir):
        os.makedirs(xml2json_test_dir)

    for csv_name in csv_list:

        dataset_name = Path(csv_name).stem
        csv_pth = os.path.join(urls_dir, dataset_name + '.csv')
        xml_dir = os.path.join(os.path.abspath('./initial_data/stage_2/paper_xml/'), dataset_name)

        filenames = pd.read_csv(csv_pth)['filename']
        input = [(filename, os.path.join(xml_dir, Path(filename).stem + '.tei.xml', '')) for filename in filenames]

        pool = Pool()
        entries = pool.starmap(test_xml_valid, input)

        df = pd.DataFrame(entries, columns=['filename', 'xml_to_json_success'])
        df.sort_values(by='filename')
        df.to_csv(os.path.abspath(os.path.join(xml2json_test_dir, dataset_name + '.csv')))
