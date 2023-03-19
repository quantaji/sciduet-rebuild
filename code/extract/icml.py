import requests
import pandas as pd
from bs4 import BeautifulSoup
import os
import re

if __name__ == '__main__':

    years = [2019, 2020, 2021, 2022]  # only these years are possible
    volume = {
        '2019': 'v97',
        '2020': 'v119',
        '2021': 'v139',
        '2022': 'v162',
    }

    url_store_dir = './initial_data/stage_1/extracted_urls'
    if not os.path.exists(url_store_dir):
        os.makedirs(url_store_dir)

    for year in years:
        schedule_url = 'https://icml.cc/Conferences/{year}/Schedule'.format(year=year)

        r = requests.get(schedule_url)
        soup = BeautifulSoup(r.content, "lxml")
        filtered = soup.find_all('div', string=['Oral', 'Poster', 'Spotlight'])  # leave only papers remain

        paper_list_url = 'http://proceedings.mlr.press/{volume}/'.format(volume=volume[str(year)])
        r_tmp = requests.get(paper_list_url)
        paper_list = BeautifulSoup(r_tmp.content, "lxml")

        pair_all = {'titles': [], 'slides': [], 'papers': []}
        index = 0

        for item in filtered:

            main_item = item.parent
            # print(main_item)

            # find slides url now
            slide_url = None
            slide_item = main_item.find('a', title='Slides')
            if not slide_item:
                continue
            else:
                temp = slide_item['href']
                if temp[-4:] != '.pdf':
                    continue
                else:
                    slide_url = temp
                    if slide_url[:6] == '/media':
                        slide_url = 'icml.cc' + slide_url

            # print(slide_url)

            # title
            title = main_item.find('div', class_="maincardBody").string
            if '$' in title:
                continue
            # print(title)

            # find paper url now
            paper_url = None
            paper_item = None
            try:
                paper_item = paper_list.find('p', string=re.compile(title))
            except:
                continue
            if not paper_item:
                continue
            paper_item = paper_item.parent
            if not paper_item:
                continue
            download_item = paper_item.find('a', href=True, text='Download PDF')
            if not download_item:
                continue
            paper_url = download_item['href']
            print(paper_url)

            slide_url = slide_url.replace("https://", "").replace("http://", "")
            paper_url = paper_url.replace("https://", "").replace("http://", "")

            pair_all['titles'].append(title)
            pair_all['slides'].append(slide_url)
            pair_all['papers'].append(paper_url)

            print(index, title, paper_url, slide_url, sep=' ')
            index += 1

        pd.DataFrame(pair_all).to_csv(os.path.join(url_store_dir, 'icml_{year}.csv'.format(year=year)))
        print('Total count: ', index)
