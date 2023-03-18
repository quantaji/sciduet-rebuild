import requests
import pandas as pd
from bs4 import BeautifulSoup
import os
import re

if __name__ == "__main__":
    years = [2021, 2022]
    # ICLR puts all pdf on open reviews

    url_store_dir = './initial_data/stage_1/extracted_urls'
    if not os.path.exists(url_store_dir):
        os.makedirs(url_store_dir)

    for year in years:
        schedule_url = 'https://iclr.cc/Conferences/{year}/Schedule'.format(year=year)

        r = requests.get(schedule_url)
        soup = BeautifulSoup(r.content, "lxml")
        filtered = soup.find_all('div', string=['Oral', 'Poster', 'Spotlight'])  # leave only papers remain

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
                        slide_url = 'iclr.cc' + slide_url

            # print(slide_url)

            # title
            title = main_item.find('div', class_="maincardBody").string
            if '$' in title:
                continue
            # print(title)

            # find paper url now
            paper_url = None

            paper_link = main_item.find('a', class_='paper-pdf-link', href=True)  # 2021
            if paper_link is None:
                paper_link = main_item.find('a', title='OpenReview', href=True)  # 2022
            if paper_link is None:
                continue

            r = requests.get(paper_link['href'])
            tmpsoup = BeautifulSoup(r.content, 'lxml')

            download_item = tmpsoup.find('a', class_='note_content_pdf')
            if download_item is None:
                continue
            else:
                paper_url = 'openreview.net' + download_item['href']

            slide_url = slide_url.replace("https://", "").replace("http://", "")
            paper_url = paper_url.replace("https://", "").replace("http://", "")

            pair_all['titles'].append(title)
            pair_all['slides'].append(slide_url)
            pair_all['papers'].append(paper_url)

            print(index, title, paper_url, slide_url, sep=' ')
            index += 1

        pd.DataFrame(pair_all).to_csv(os.path.join(url_store_dir, 'iclr_{year}.csv'.format(year=year)))
        print('Total count: ', index)
