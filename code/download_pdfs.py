import requests
from pathlib import Path
import pandas as pd
from waybackpy import WaybackMachineAvailabilityAPI
from bs4 import BeautifulSoup
import PyPDF2
import os
import pandas as pd

from initial_stage.collect_files import get_pdfs_from_csv

if __name__ == '__main__':

    data_dir = os.path.abspath('../data')
    collection_names = [Path(file).stem for file in os.listdir(data_dir)]

    for name in collection_names:
        collection_dir = os.path.join(data_dir, name)

        paper_dir = os.path.join(collection_dir, 'paper')
        slide_dir = os.path.join(collection_dir, 'slide')

        if not os.path.exists(paper_dir):
            os.makedirs(paper_dir)
        if not os.path.exists(slide_dir):
            os.makedirs(slide_dir)

        for idx, item in pd.read_csv(os.path.join(collection_dir, 'list.csv')).iterrows():
            print(item)
            if idx > 10:
                break
