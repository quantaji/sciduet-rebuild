from pathlib import Path
import pandas as pd
import os
from grobid_client.grobid_client import GrobidClient
import shutil
from subprocess import call
import subprocess
import json

pdffigures2_home = os.path.abspath(str(Path.home()) + '/Library/pdffigures2')

if __name__ == '__main__':

    repo_dir = './'
    data_dir = os.path.abspath(repo_dir + 'data')
    # data_dir = os.path.abspath(repo_dir + 'data_backup')
    collection_names = [Path(file).stem for file in os.listdir(data_dir)]

    for name in collection_names:
        collection_dir = os.path.join(data_dir, name)
        paper_dir = os.path.join(collection_dir, 'paper')
        figure_dir = os.path.join(collection_dir, 'figure')

        fig_dir_profix = 'figure'
        img_dir_profix = 'figure/image'
        json_dir_profix = 'figure/json'

        tgt_fig_dir = os.path.join(collection_dir, fig_dir_profix)
        # remove original figure first
        try:
            shutil.rmtree(tgt_fig_dir)
        except:
            pass
        if not os.path.exists(tgt_fig_dir):
            os.makedirs(tgt_fig_dir)

        tmp_fig_dir = os.path.join(pdffigures2_home, fig_dir_profix)
        if not os.path.exists(tmp_fig_dir):
            os.makedirs(tmp_fig_dir)
        tmp_img_dir = os.path.join(pdffigures2_home, img_dir_profix)
        if not os.path.exists(tmp_img_dir):
            os.makedirs(tmp_img_dir)
        tmp_json_dir = os.path.join(pdffigures2_home, json_dir_profix)
        if not os.path.exists(tmp_json_dir):
            os.makedirs(tmp_json_dir)

        args = ['sbt', 'runMain org.allenai.pdffigures2.FigureExtractorBatchCli -q ' + os.path.abspath(paper_dir) + '/' + ' -m ' + './' + img_dir_profix + '/' + ' -d ' + './' + json_dir_profix + '/' + ' -s ' + './' + fig_dir_profix + '/stat.json']

        # exit_code = call(args, cwd=pdffigures2_home, stdout=subprocess.DEVNULL)
        exit_code = call(args, cwd=pdffigures2_home)

        shutil.move(tmp_fig_dir, tgt_fig_dir)
