import requests
import pandas as pd
from bs4 import BeautifulSoup
import os
import re

if __name__ == '__main__':
    # no slides for 2020
    years = [2018, 2019, 2021, 2022]  # only these years are possible

    url_store_dir = './initial_data/stage_1/extracted_urls'
    if not os.path.exists(url_store_dir):
        os.makedirs(url_store_dir)

    for year in years:
        schedule_url = 'https://nips.cc/Conferences/{year}/Schedule'.format(year=year)

        r = requests.get(schedule_url)
        soup = BeautifulSoup(r.content, "lxml")
        filtered = soup.find_all('div', string=['Oral', 'Poster', 'Spotlight'])  # leave only papers remain

        pair_all = {'titles': [], 'slides': [], 'papers': []}

        index = 0

        paper_list_url = 'https://papers.nips.cc/paper/{year}'.format(year=year)
        r_tmp = requests.get(paper_list_url)
        paper_list = BeautifulSoup(r_tmp.content, "lxml")

        for item in filtered:

            main_item = item.parent

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
                        slide_url = 'nips.cc' + slide_url

            # title
            title = main_item.find('div', class_="maincardBody").string

            # find paper url now
            paper_url = None
            paper_link = main_item.find_all('a', title=['Paper', 'OpenReview'])
            if paper_link:

                if paper_link[0]['title'] == 'Paper':  # 2018, 2019

                    r = requests.get(paper_link[0]['href'])
                    tmpsoup = BeautifulSoup(r.content, 'lxml')

                    paper_link_tmp = tmpsoup.find("a", string='Paper')['href']
                    paper_url = 'proceedings.neurips.cc' + paper_link_tmp
                else:  # 2021 2022
                    r = requests.get(paper_link[0]['href'])
                    tmpsoup = BeautifulSoup(r.content, 'lxml')

                    download_item = tmpsoup.find('a', class_='note_content_pdf')
                    if download_item is None:
                        continue
                    else:
                        paper_url = 'openreview.net' + download_item['href']
            else:
                # no paper in this page, search from paper list page

                if '$' in title:
                    continue  # no math expression in title

                # pattern = r'(.)*' + re.escape(title) + r'(.)*'
                tmp = paper_list.find('a', string=re.compile(title))

                if not tmp:
                    continue

                r = requests.get('https://papers.nips.cc' + tmp['href'])
                tmpsoup = BeautifulSoup(r.content, 'lxml')

                paper_link_tmp = tmpsoup.find("a", string='Paper')['href']
                paper_url = 'proceedings.neurips.cc' + paper_link_tmp

            slide_url = slide_url.replace("https://", "").replace("http://", "")
            paper_url = paper_url.replace("https://", "").replace("http://", "")

            pair_all['titles'].append(title)
            pair_all['slides'].append(slide_url)
            pair_all['papers'].append(paper_url)

            print(index, title, paper_url, slide_url, sep=' ')
            index += 1

        pd.DataFrame(pair_all).to_csv(os.path.join(url_store_dir, 'neurips_{year}.csv'.format(year=year)))
        print('Total count: ', index)
