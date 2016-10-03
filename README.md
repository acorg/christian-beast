# Convert CSV to XML for BEAST

This repo contains code to convert a CSV file containing taxa (rows) and
feature (columns) names, and the numeric values for each feature for each
taxon into an XML fragment suitable for pasting into a
[BEAST](http://beast.bio.ed.ac.uk/) config file.

## Usage

The Python script in `bin/csv-to-xml.py` expects CSV on standard input and
writes XML to standard output.  So if you have an input file, called
`input.csv` containing

```
-, Length, Height
A, 3, 4
B, 5, 6
```

you can get XML via

```sh
$ bin/csv-to-xml.py < input.csv
<?xml version='1.0' encoding='UTF-8'?>
<xxx><!--Length--><feature><value>-0.22184874961635642</value></feature><!--Height--><feature><value>-0.17609125905568124</value></feature></xxx>
```

The output XML contains a `<feature>` section for each feature. In each of
these, the values are the upper diagonal of an inter-taxa distance matrix
computed from the values for the feature. Values are logged (base 10)
before their differences are taken for the distance matrix.

The XML format still needs some work to make it completely correct for BEAST.

## Options

Call with `--fragment` to omit the printing of the XML declaration.
