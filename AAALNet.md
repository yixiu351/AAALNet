# AAALNet
<h1 id="OMrDr">Environment:</h1>
+ pytorch=1.8.1
+ python=3.8

<h1 id="TagXF">Getting Started:</h1>
<h2 id="VTUMk"><font style="color:rgb(31, 35, 40);">Install dependencies:</font></h2>
`pip install -r requirements.txt`

<h2 id="OCJ0v">Test:</h2>
+ <font style="color:rgb(31, 35, 40);">Download pre-trained models from this </font>[google drive](https://drive.google.com/file/d/1NnwZsSGdSuoSOZ5PrsDAdN-AMlVxXdyw/view?usp=drive_link)<font style="color:rgb(31, 35, 40);">. </font>
+ Test a single image:

`<font style="color:rgb(31, 35, 40);">python test.py --content content/1.jpg --style style/1.jpg</font>`

+ <font style="color:rgb(31, 35, 40);">Test multiple images:</font>

`<font style="color:rgb(31, 35, 40);">python test.py --content_dir content/ --style_dir style/</font>`

+ Style control when testing:

`<font style="color:rgb(31, 35, 40);">python test.py --content content/1.jpg --style style/1.jpg --alpha 0.7</font>`

+ <font style="color:rgb(31, 35, 40);">Keep the content color when testing:</font>
+ `<font style="color:rgb(31, 35, 40);">python test.py --content content/1.jpg --style style/1.jpg --preserve_color</font>`

<h2 id="ei35B">Train:</h2>
+ <font style="color:rgb(31, 35, 40);">Download content dataset </font>[MS-COCO](https://cocodataset.org/#download) <font style="color:rgb(31, 35, 40);">and style dataset </font>[WikiArt](https://www.wikiart.org/)<font style="color:rgb(31, 35, 40);">.</font>
+ <font style="color:rgb(31, 35, 40);">Download the pre-trained </font>[vgg_normalised.pth](https://drive.google.com/file/d/1NWkTiPIo9ABKF-qreDh2VW2yOwi0XPa5/view?usp=drive_link)<font style="color:rgb(31, 35, 40);">.</font>
+ <font style="color:rgb(31, 35, 40);">Run train script:</font>

`<font style="color:rgb(31, 35, 40);">python train.py --content_dir ./datasets/coco2014/train2014 --style_dir ./datasets/wikiart/train</font>`

<h1 id="pvfzA"><font style="color:rgb(31, 35, 40);">Acknowledgement:</font></h1>
We refer to some codes from [AesUST](https://github.com/EndyWon/AesUST) and [TSSAT](https://github.com/HalbertCH/TSSAT). Great thanks to them!

