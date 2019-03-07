# pitchplots

![header](images/big_blue_hex_8_top.png)

library plotting charts for different tonal representations

## Getting Started

The library contains the following files
* `functions.py`, 
* `reader.py`, 
* `modified_music_xml.py`, 
* `parser.py`, and 
* `static.py`

### Prerequisites

In order to use **pitchplots** you need a running Python environment and the following libraries:
* matplotlib
* pandas
* numpy

Note that if you are using the Anaconda distribution, these libraries are already installed.

### Installation

You can install the pitchplots package on pypi with pip using the following command in the prompt:

```
python3 -m pip install pitchplots
```

or if you're using the anaconda prompt

```
pip install pitchplots
```

## Working with files

### Parsing

**Pitchplots** plots note distributions from MusicXML files (`.xml` of `.mxl`). You can either specify your own file or use the [test file](data_example.mxl) `data_example.mxl`. contained in the package.

The first step is to parse the file into a note list representation that corresponds to a pandas DataFrame where each line is a note or a rest.

```python
import os

import pitchplots
import pitchplots.parser as ppp

path = os.path.join(pitchplots.__path__[0], 'data_example.mxl')
df_data_example = ppp.xml_to_csv(path, save_csv=True)
```

To use your own file, replace `path` with the path to your file.

## Plotting

In order to plot the notes of a piece, import the `pitchplots.static` module and use one of its plotting functions. They take as input the output of the parser, i.e. either a DataFrame object:

```python
import pitchplots.static as pps

pps.hexagonal_chart(df_data_example)
```
 or a CSV file:
```python
import pitchplots.static as pps

pps.hexagonal_chart('csv/data_example.csv')
```
A more detailed overview about the functionality of the plotting functions is given in the notebooks [documentation_hexagonal_chart.ipynb](documentation_hexagonal_chart.ipynb) for information on `hexagonal_chart` and [documentation_pie_chart.ipynb](documentation_pie_chart.ipynb) for information on `pie_chart information`.

## Functions

<img   src="images/Tp1_def_hex.png"><img   src="images/Tp2_hex_orange_pc_5.png"><img   src="images/Tp3_hex_noduplicate.png"><img   src="images/Tp4_def_pie.png"><img   src="images/Tp5_red_pie_nofifith.png"><img   src="images/Tp6_log_pie.png">

Pitchplots has 2 functions related to tonal representation and 1 for the parsing of `.mxl` and `.xml` files into `.csv`.

-   `hexagonal_chart` uses a `.csv` file or a pandas DataFrame of a piece of music to do a hexagonal 2D representation.
-   `pie_chart` uses a csv file or a pandas DataFrame of a piece of music to represent the notes by fifth or chromatic.
-   `xml_to_csv` uses a `.mxl` or `.xml` file and parses it into a `.csv` file using the magenta musicxml_parser.py.

## Authors

* **Timothy Loayza**, **Fabian Moss** - *Initial work* - [pitchplots](https://github.com/DCMLab/pitchplots)

## Usage of Magenta's code

The [modified_musicxml_parser.py](modified_musicxml_parser.py) file is taken from the [magenta](https://github.com/tensorflow/magenta) project and has been modified. Therefore the modifications are listed in the [magenta_musicxml_code_modifications.md](magenta_musicxml_code_modifications.md) file and there is the [magenta_LICENSE.md](magenta_LICENSE.md).

## License

This project is licensed under the MIT License - see the [LICENSE.md](LICENSE.md) file for details
