from grobid_client.grobid_client import GrobidClient
from pathlib import Path
import os
# import shutil

client = GrobidClient(config_path=str(Path.home()) + '/Library/grobid_client_python/config.json')

if __name__ == "__main__":
    urls_dir = os.path.abspath('./initial_data/stage_2/extracted_url/')
    pdfs_dir = os.path.abspath('./initial_data/stage_2/pdf/')
    csv_list = os.listdir(urls_dir)

    for csv_name in csv_list:

        dataset_name = Path(csv_name).stem
        csv_pth = os.path.join(urls_dir, csv_name)

        xml_dir = os.path.join(os.path.abspath('./initial_data/stage_2/paper_xml/'), dataset_name)
        pdf_dir = os.path.join(pdfs_dir, dataset_name + '/papers')

        if not os.path.exists(xml_dir):
            os.makedirs(xml_dir)

        client.process(
            'processFulltextDocument',
            pdf_dir,
            tei_coordinates=True,
            force=True,
            verbose=True,
            output=xml_dir,
        )
