# DAVIDpy
Python3 extension for [DAVID Bioinformatics Tool](https://david-d.ncifcrf.gov/)

**! Current version supports only Chart Reports !**

DAVIDpy is based on [DAVID Web Service](https://david-d.ncifcrf.gov/content.jsp?file=WS.html) so it has the same restrictions (max. 200 jobs in a day).


## Installation
You can install DAVIDpy from [PyPI](https://pypi.org/project/DAVIDpy/) using `pip`:

    pip3 install DAVIDpy

Also you should register [HERE](https://david-d.ncifcrf.gov/webservice/register.htm) before using this tool.

## Usage
**<details><summary>Command-line tool</summary>**
Easy and fast way to run DAVID analysis.

You should use it if:
* You want just to save a result (.tsv or .csv).
* You need a fast way to have a look on result right in the command line.

To perform analysis, run:

    davidpy -i <genes>

where `<genes>` is a genes list or a text file with genes.

Some optional arguments:
`--tsv` and `--csv` - save result at working directory.
`--full` - show more columns.
 </details>

**<details><summary>Python package</summary>**
More flexible way to run DAVID analysis.  
It allows to work with results as a Pandas DataFrame object.

Common way to perform analysis:
``` python
import davidpy
client = davidpy.DAVID_start(input_list)
df = davidpy.get_chart(client)
```

If you need, you can use `client` object to do more complex requests, using *WSDL* operations listed [here](https://david-d.ncifcrf.gov/content.jsp?file=WS.html). For example:
``` python
import davidpy
client = davidpy.DAVID_start(input_list)
client.service.getListReport()
```
</details>
