from pathlib import Path
import os
import shutil
import pandas as pd
import uuid

if __name__ == '__main__':

    repo_path = os.path.abspath('./')
    urls_dir = os.path.join(repo_path, 'initial_data/stage_2/extracted_url/')
    collection_names = [Path(file).stem for file in os.listdir(urls_dir)]
    final_data_dir = os.path.join(repo_path, 'data')

    img_ext_dir = os.path.abspath(os.path.join(repo_path, 'initial_data/stage_2/paper_img_ext'))
    xml2json_test_dir = os.path.abspath(os.path.join(repo_path, 'initial_data/stage_2/xml2json_test'))

    for name in collection_names:
        original_data = pd.read_csv(os.path.join(urls_dir, name + '.csv'))
        original_img_test = pd.read_csv(os.path.join(img_ext_dir, name + '.csv'))
        original_xml_test = pd.read_csv(os.path.join(xml2json_test_dir, name + '.csv'))

        original_data = original_data.merge(original_img_test, on='filename').merge(original_xml_test, on='filename')[['title', 'slide_url', 'paper_url', 'filename', 'img_ext_success', 'xml_to_json_success']]

        collection_dir = os.path.join(final_data_dir, name)
        xml_dir = os.path.join(collection_dir, 'xml')
        paper_dir = os.path.join(collection_dir, 'paper')
        slide_dir = os.path.join(collection_dir, 'slide')
        figure_dir = os.path.join(collection_dir, 'figure')
        # fig_dir = os.path.join(collection_dir, 'paper_fig')
        if not os.path.exists(xml_dir):
            os.makedirs(xml_dir)
        if not os.path.exists(paper_dir):
            os.makedirs(paper_dir)
        if not os.path.exists(slide_dir):
            os.makedirs(slide_dir)
        if not os.path.exists(figure_dir):
            os.makedirs(figure_dir)

        # index = 0
        pair = {
            'uuid': [],
            'title': [],
            'slide_url': [],
            'paper_url': [],
        }

        for idx, item in original_data.iterrows():

            # validate
            if item['img_ext_success'] and item['xml_to_json_success']:

                id = str(uuid.uuid4())

                file = Path(item['filename']).stem

                old_paper_pth = os.path.join(repo_path, 'initial_data/stage_2/pdf', name, 'papers', item['filename'])
                old_slide_pth = os.path.join(repo_path, 'initial_data/stage_2/pdf', name, 'slides', item['filename'])
                old_xml_pth = os.path.join(repo_path, 'initial_data/stage_2/paper_xml', name, file + '.tei.xml')

                new_paper_pth = os.path.join(paper_dir, id + '.pdf')
                new_slide_pth = os.path.join(slide_dir, id + '.pdf')
                new_xml_pth = os.path.join(paper_dir, id + '.tei.xml')

                pair['uuid'].append(id)
                pair['title'].append(item['title'])
                pair['slide_url'].append(item['slide_url'])
                pair['paper_url'].append(item['paper_url'])

                shutil.copy(old_paper_pth, new_paper_pth)
                shutil.copy(old_slide_pth, new_slide_pth)
                shutil.copy(old_xml_pth, new_xml_pth)

        df = pd.DataFrame(pair)
        df.to_csv(os.path.join(collection_dir, 'list.csv'), index=False)
