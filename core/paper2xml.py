from pathlib import Path
import pandas as pd
from grobid_client.grobid_client import GrobidClient
import os

client = GrobidClient(config_path=str(Path.home()) + '/Library/grobid_client_python/config.json')

if __name__ == '__main__':

    data_dir = os.path.abspath('./data')
    collection_names = [Path(file).stem for file in os.listdir(data_dir)]

    for name in collection_names:
        collection_dir = os.path.join(data_dir, name)

        paper_dir = os.path.join(collection_dir, 'paper')
        xml_dir = os.path.join(collection_dir, 'xml')

        if not os.path.exists(paper_dir):
            os.makedirs(paper_dir)
        if not os.path.exists(xml_dir):
            os.makedirs(xml_dir)

        print(name)
        client.process(
            'processFulltextDocument',
            paper_dir,
            tei_coordinates=True,
            force=True,
            verbose=True,
            output=xml_dir,
        )
