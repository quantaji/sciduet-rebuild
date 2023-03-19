import requests
from pathlib import Path
import pandas as pd
from waybackpy import WaybackMachineAvailabilityAPI
from bs4 import BeautifulSoup
import PyPDF2
import os


def get_pdf(url: str, tgt_pth: str) -> bool:
    """
    logic: If original url not successful or downloaded content too small (less than 64KB, 65532 Byte, but save it) then try waybackpy if we can download any
    if not return false
    if the returned pdf has less than 1 page return false
    """
    ori_usable = True
    axv_usable = True
    timeout1 = 5.0  # 5 seconds for testing timeout
    timeout2 = 20.0

    req = None

    # first try original link
    url = 'https://' + url.replace("https://", "").replace("http://", "")

    # print(url)

    try:
        req = requests.get(url, timeout=timeout1)

        # try read the file
        pdf_file = Path(tgt_pth)
        pdf_file.write_bytes(req.content)

        test_open1 = open(tgt_pth, 'rb')
        try:
            test_pdf1 = PyPDF2.PdfReader(test_open1)
            if len(test_pdf1.pages) == 0:
                print('Ori page zero.')
                ori_usable = False
        except:
            print('Ori pdf broken.')
            ori_usable = False

    except:
        print('Ori request timeout')
        ori_usable = False

    if ori_usable is False:
        axv_url = None

        axv_api = WaybackMachineAvailabilityAPI(url, 'Any-user-agent-you-want')
        try:
            axv_api.timestamp()
            axv_page_url = str(axv_api.oldest())
            axv_req = requests.get(axv_page_url, timeout=timeout2)

            # sometimes webarxiv directly return content, sometimes it return a smaller html
            if len(axv_req.content) > 65536:
                axv_url = axv_page_url
            else:
                soup = BeautifulSoup(axv_req.content, 'lxml')

                axv_pdf_item = soup.find('iframe', src=True, id='playback')

                if axv_pdf_item:
                    axv_url = axv_pdf_item['src']
                else:
                    print('Axv no url')
                    axv_usable = False

        except:
            print('Axv timeout')
            axv_usable = False

        if axv_usable:
            req = requests.get(axv_url, timeout=timeout2)

            # try read the file
            pdf_file = Path(tgt_pth)
            pdf_file.write_bytes(req.content)

            test_open2 = open(tgt_pth, 'rb')
            try:
                test_pdf2 = PyPDF2.PdfReader(test_open2)
                if len(test_pdf2.pages) == 0:
                    print('Axv pdf zero page')
                    axv_usable = False
            except:
                print('Axv pdf broken')
                axv_usable = False

    if ori_usable or axv_usable:
        return True
    else:
        # delete potential pdf
        if os.path.exists(tgt_pth):
            os.remove(tgt_pth)

        return False


if __name__ == '__main__':

    data_dir = os.path.abspath('./data')
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

            print(idx)
            paper_pth = os.path.join(paper_dir, item['uuid'] + '.pdf')
            slide_pth = os.path.join(slide_dir, item['uuid'] + '.pdf')
            get_pdf(url=item['slide_url'], tgt_pth=slide_pth)
            get_pdf(url=item['paper_url'], tgt_pth=paper_pth)
