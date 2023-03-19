from pathlib import Path
import pandas as pd
import os
import json

if __name__ == '__main__':

    repo_dir = './'
    data_dir = os.path.abspath(repo_dir + 'data')
    collection_names = [Path(file).stem for file in os.listdir(data_dir)]

    for name in collection_names:
        print(name)
        collection_dir = os.path.join(data_dir, name)

        paper_dir = os.path.join(collection_dir, 'paper')
        figure_dir = os.path.join(collection_dir, 'figure')
        img_dir = os.path.join(collection_dir, 'figure/image')
        xml_dir = os.path.join(collection_dir, 'xml')
        slide_dir = os.path.join(collection_dir, 'slide')

        data = pd.read_csv(os.path.join(collection_dir, 'list.csv'), index_col='uuid')
        # # .set_index(keys='uuid')
        # print(data.head())

        img_ext_stat = os.path.join(figure_dir, 'stat.json')
        if not os.path.exists(img_ext_stat):
            print('No json file yet!')
            continue

        def delete_item(tgt_uuid):

            if tgt_uuid not in data.index:
                return data

            paper_pth = os.path.join(paper_dir, tgt_uuid + '.pdf')
            slide_pth = os.path.join(slide_dir, tgt_uuid + '.pdf')
            xml_pth = os.path.join(xml_dir, tgt_uuid + '.tei.xml')
            fig_json_pth = os.path.join(figure_dir, 'json', tgt_uuid + '.json')

            paths = [
                paper_pth,
                slide_pth,
                xml_pth,
                fig_json_pth,
            ]
            for name in os.listdir(img_dir):
                if name[:36] == tgt_uuid:
                    paths.append(os.path.join(img_dir, name))

            for pth in paths:

                # print(pth, os.path.exists(pth))  # dry run
                if os.path.exists(pth):
                    print('Removing file {path}.'.format(path=pth))
                    os.remove(pth)

            return data.drop(index=tgt_uuid)

        with open(img_ext_stat) as data_file:
            stat_data = json.load(data_file)
            idx = 0
            for item in stat_data:
                if 'msg' in item.keys():
                    tgt_uuid = str(Path(item['filename']).stem)
                    if tgt_uuid not in data.index:
                        continue
                    print('Deleting item with uuid:"{uuid}" and error message:"{msg}".'.format(uuid=tgt_uuid, msg=item['msg']))

                    data = delete_item(tgt_uuid=tgt_uuid)
                    # print(tgt_uuid in data.index)

        data.to_csv(os.path.join(collection_dir, 'list.csv'))
