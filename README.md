# pitchplots

library plotting charts for different tonal representations

## Getting Started

The program consist in the following files: musical_function.py, musical_read_file.py and static.py 

### Prerequisites

What things you need to install the software and how to install them

```
You will need python on your computer and the following libaries: matplotlib, pandas, numpy and magenta
```

note that if you are using anaconda, these libraries are already installed except magenta

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

you can first try to parse xml files to csv or DataFrame using our test files [data_example.mxl](data_example.mxl) with:

```
import pitchplots.parser as ppp

ppp.xml_to_csv('data_example.mxl')
df_data_example = ppp.xml_to_csv('data_example.mxl', save_csv=False)
```

then you can try the static module by passing csv files or Dataframe:

```
import pitchplots.static as pps

pps.hexagonal_chart('data_example.csv')
```
or
```
import pitchplots.static as pps

pps.hexagonal_chart(df_data_example)
```

then to see all the possibilities you can look at the [documentation_hexagonal_chart.ipynb](documentation_hexagonal_chart.ipynb) for hexagonal_chart information and the [documentation_pie_chart.ipynb](documentation_pie_chart.ipynb) for pie_chart information.

## Authors

* **Timothy Loayza**, **Fabian Moss** - *Initial work* - [pitchplots](https://github.com/DCMLab/pitchplots)

## License

This project is licensed under the MIT License - see the [LICENSE.md](LICENSE.md) file for details
