# kamiCLI : easy CLI to evaluate HTR model

The purpose of this script is to provide an easy way to evaluate an HTR model from your ground truth files. It allows you to serialize the results as independent CSVs according to the desired transformations.

The script is based on the [KaMI-lib](https://github.com/KaMI-tools-project/KaMi-lib/tree/master) library designed by Lucas Terriel and Alix Chagué.

Each CSV contains standard HTR metrics such as CER, WER, Wacc, Levensthein distance, etc... This makes statistical manipulation of all your datasets much easier.

--------------------------------------------
### How to use

Here's a basic example, csv files will be present in `output/` :

```shell
python3 run.py MODEL_PATH -d DATASET_PATH
```
There are a number of options for refining the results to suit your needs.

---------------------------------------------

## Troubleshooting

If you get a similar error: "[ERROR] Prediction with Kraken failed: 'Delaunay' object has no attribute 'vertices'" you simply need to install an earlier version of Scipy `pip install SciPy==1.10.1` (issue [#525](https://github.com/mittagessen/kraken/issues/525)).
