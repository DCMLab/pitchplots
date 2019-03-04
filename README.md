# pitchplots

<img   src="images/big_blue_hex_8_top.png">

library plotting charts for different tonal representations

## Getting Started

The program consist in the following files: functions.py, reader.py, modified_music_xml.py, parser.py and static.py 

### Prerequisites

What things you need to install the software and how to install them

```
You will need python on your computer and the following libaries: matplotlib, pandas and numpy
```

note that if you are using anaconda, these libraries are already installed

### Installing

You can download the pitchplots package on pypi with pip using the following command in the prompt:

```
python3 -m pip install pitchplots
```

or if you're using anaconda prompt

```
pip install pitchplots
```

## Running the tests

you can first try to parse xml/musicScore xml files to csv or DataFrame using our test files [data_example.mxl](data_example.mxl), that is the Gymnopédie from Sati with:

```
import os

import pitchplots
import pitchplots.parser as ppp

example_path = os.path.join(pitchplots.__path__[0], 'data_example.mxl')
df_data_example = ppp.xml_to_csv(example_path, save_csv=True)
```

then you can try the static module by passing csv files or Dataframe:

```
import pitchplots.static as pps

pps.hexagonal_chart(df_data_example)
```
or
```
import pitchplots.static as pps

pps.hexagonal_chart('csv/data_example.csv')
```

then to see all the possibilities you can look at the [documentation_hexagonal_chart.ipynb](documentation_hexagonal_chart.ipynb) for hexagonal_chart information and the [documentation_pie_chart.ipynb](documentation_pie_chart.ipynb) for pie_chart information.

## Functions

<img   src="images/Tp1_def_hex.png"><img   src="images/Tp2_hex_orange_pc_5.png"><img   src="images/Tp3_hex_noduplicate.png"><img   src="images/Tp4_def_pie.png"><img   src="images/Tp5_red_pie_nofifith.png"><img   src="images/Tp6_log_pie.png">

Pitchplots has 2 functions related to tonal representation and 1 for the parsing of `.mxl` and `.xml` files into `.csv`.

-   `hexagonal_chart` uses a `.csv` file or a pandas DataFrame of a piece of music to do a hexagonal 2D representation.
-   `pie_chart` uses a csv file or a pandas DataFrame of a piece of music to represent the notes by fifth or chromatic.
-   `xml_to_csv` uses a `.mxl` or `.xml` file and parses it into a `.csv` file using the magenta musicxml_parser.py.

## Authors

* **Timothy Loayza**, **Fabian Moss** - *Initial work* - [pitchplots](https://github.com/DCMLab/pitchplots)

## Use of magenta's code

The [modified_musicxml_parser.py](modified_musicxml_parser.py) file is taken from the [magenta](https://github.com/tensorflow/magenta) project and has been modified. Therefore the modifications are listed in the [magenta_musicxml_code_modifications.md](magenta_musicxml_code_modifications.md) file and there is the [magenta_LICENSE.md](magenta_LICENSE.md).

## License

This project is licensed under the MIT License - see the [LICENSE.md](LICENSE.md) file for details
