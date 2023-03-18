import requests
from pathlib import Path
import pandas as pd
from waybackpy import WaybackMachineAvailabilityAPI
from bs4 import BeautifulSoup
import PyPDF2
import os
import pandas as pd
from tqdm import tqdm


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


def get_pdfs_from_csv(csv_pth: str, pdf_dir: str, url_dir: str) -> None:
    collection_name = csv_pth.split('/')[-1][:-4]

    collection_pdf_dir = os.path.join(pdf_dir, collection_name)
    if not os.path.exists(collection_pdf_dir):
        os.makedirs(collection_pdf_dir)
    if not os.path.exists(os.path.join(collection_pdf_dir, 'papers')):
        os.makedirs(os.path.join(collection_pdf_dir, 'papers'))
    if not os.path.exists(os.path.join(collection_pdf_dir, 'slides')):
        os.makedirs(os.path.join(collection_pdf_dir, 'slides'))

    pair_all = {
        'index': [],
        'title': [],
        'slide_url': [],
        'paper_url': [],
        'filename': [],
    }

    index = 0

    df = pd.read_csv(csv_pth)
    for i, row in df.iterrows():

        filename = '{index}.pdf'.format(index=index)
        paper_pth = os.path.abspath(os.path.join(collection_pdf_dir, 'papers', filename))
        slide_pth = os.path.abspath(os.path.join(collection_pdf_dir, 'slides', filename))

        slide_avail = get_pdf(url=row['slides'], tgt_pth=slide_pth)
        paper_avail = get_pdf(url=row['papers'], tgt_pth=paper_pth)

        print(i, row['titles'], slide_avail, paper_avail)

        if slide_avail and paper_avail:
            pair_all['index'].append(index)
            pair_all['title'].append(row['titles'])
            pair_all['slide_url'].append(row['slides'])
            pair_all['paper_url'].append(row['papers'])
            pair_all['filename'].append(filename)

            index += 1

    pd.DataFrame(pair_all).to_csv(os.path.abspath(os.path.join(url_dir, collection_name + '.csv')))
    print('Total available pairs: ', index)


if __name__ == "__main__":
    urls_dir = os.path.abspath('./initial_data/stage_1/extracted_urls/')
    csv_list = os.listdir(urls_dir)

    for csv_name in csv_list:
        csv_pth = os.path.join(urls_dir, csv_name)
        get_pdfs_from_csv(
            csv_pth=csv_pth,
            pdf_dir='./initial_data/stage_2/pdf',
            url_dir='./initial_data/stage_2/extracted_url',
        )
