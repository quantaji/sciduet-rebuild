from pathlib import Path
import os
import shutil
from subprocess import call
import subprocess
import json
import pandas as pd

# need to change this on your computer
pdffigures2_home = os.path.abspath(str(Path.home()) + '/Library/pdffigures2')


def test_figure_extraction(pdf_dir: str):

    pair_all = {
        'filename': [],
        'img_ext_success': [],
    }

    # dry run for extraction
    tmp_dir = './tmp_fig_ext'
    if not os.path.exists(tmp_dir):
        os.makedirs(tmp_dir)
    stat_json_pth = os.path.join(tmp_dir, 'stat_file.json')

    args = ['sbt', 'runMain org.allenai.pdffigures2.FigureExtractorBatchCli -q ' + os.path.abspath(pdf_dir) + '/' + ' -e -s ' + os.path.abspath(stat_json_pth)]

    exit_code = call(args, cwd=pdffigures2_home, stdout=subprocess.DEVNULL)
    # exit_code = call(args, cwd=pdffigures2_home)

    with open(stat_json_pth) as data_file:
        data = json.load(data_file)
        for i in data:
            # print(i['filename'])
            img_ext_success = ('numPages' in i.keys())
            filename = i['filename'].split('/')[-1]

            pair_all['filename'].append(filename)
            pair_all['img_ext_success'].append(img_ext_success)

    try:
        shutil.rmtree(tmp_dir)
    except:
        pass

    return pair_all


if __name__ == '__main__':

    urls_dir = os.path.abspath('./initial_data/stage_2/extracted_url/')
    pdfs_dir = os.path.abspath('./initial_data/stage_2/pdf/')
    csv_list = os.listdir(urls_dir)

    img_ext_csv_dir = os.path.abspath('./initial_data/stage_2/paper_img_ext/')
    if not os.path.exists(img_ext_csv_dir):
        os.makedirs(img_ext_csv_dir)

    for csv_name in csv_list:
        print(csv_name)

        dataset_name = Path(csv_name).stem
        pdf_dir = os.path.join(pdfs_dir, dataset_name + '/papers')

        data = test_figure_extraction(pdf_dir=pdf_dir)
        df = pd.DataFrame(data)
        df.sort_values(by='filename')
        df.to_csv(os.path.abspath(os.path.join(img_ext_csv_dir, dataset_name + '.csv')))
