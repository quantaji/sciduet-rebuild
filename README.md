# sciduet-rebuild

This is the rebuild of [SciDuet](https://github.com/IBM/document2slides) dataset. This repo includes paper and slides of NeurIPS {2018, 2019, 2021, 2022}, ICML {2020, 2021, 2022}, ICLR {2021, 2022}. This repo only provide the download urls for paper and slides, and also the preprocessing code similar to original SciDuet dataset. 

## Get the data
```shell
# step 1: download pdfs, need webarchieve python package
python core/download_pdfs.py
# step 2: extract xml from paper pdfs, need java8 and GROBID running in the background
python core/paper2xml.py
# step 3: extract figures and their captions, need sbt installed
python core/paper2fig.py
# step 4: remove failure case
python core/remove_img_failure.py
# step 5: merge xml and figures into json file
python core/merge2json.py
```

<!-- To run `code/extrace_slides.py` you need to  -->
