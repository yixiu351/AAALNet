# AAALNet
## Environment
- Python 3.8
- PyTorch 1.8.1

## Getting Started

### Installation
```bash
pip install -r requirements.txt
```
### Test
- Download pre-trained models from this [google drive](https://drive.google.com/file/d/1NnwZsSGdSuoSOZ5PrsDAdN-AMlVxXdyw/view?usp=drive_link).
- Test a single image
```bash
python test.py --content content/1.jpg --style style/1.jpg
```
- Test multiple images
```bash
python test.py --content_dir content/ --style_dir style/
```
- Style control when testing
```bash
python test.py --content content/1.jpg --style style/1.jpg --alpha 0.7
```
- Keep the content color when testing
```bash
python test.py --content content/1.jpg --style style/1.jpg --preserve_color
```
### Train
- Download content dataset [MS-COCO](https://cocodataset.org/#download) and style dataset [WikiArt](https://www.wikiart.org/).
- Download the pre-trained [vgg_normalised.pth](https://drive.google.com/file/d/1NWkTiPIo9ABKF-qreDh2VW2yOwi0XPa5/view?usp=drive_link).
- Run train script
```bash
python train.py --content_dir ./datasets/coco2014/train2014 --style_dir ./datasets/wikiart/train
```
## Acknowledgement
We refer to some codes from [AesUST](https://github.com/EndyWon/AesUST), [MAST](https://github.com/diyiiyiii/Arbitrary-Style-Transfer-via-Multi-Adaptation-Network) and [TSSAT](https://github.com/HalbertCH/TSSAT). Great thanks to them!
