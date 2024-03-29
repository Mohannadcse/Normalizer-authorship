## The normalizer implementation consists of 2 components: 
1- [normalized transformations](src/LibToolingAST_Normalizer)

2- [generating normalized Dataset](src/PyProject/normalizer)

## Preparing Projects
### Clang Transformations

Follow the instructions [here](https://github.com/EQuiw/code-imitator/blob/master/src/LibToolingAST/README.md)

### Python Project
 
- Export the python project path `i.e., export PYTHONPATH="/nobackup/code-imitator-normalizer/src/PyProject:$PYTHONPATH"`

- Follow the instructions [here](https://github.com/EQuiw/code-imitator/blob/master/src/PyProject/README.md)

## Dataset
The dataset shold follow the same structure of the original dataset https://github.com/EQuiw/code-imitator/tree/master/data/dataset_2017/dataset_2017_8

## Running the Normalizer

 1- Download the [dataset](https://github.com/EQuiw/code-imitator/tree/master/data/dataset_2017/dataset_2017_8)

 2- Specifying the location of the `datasetpath` and `normalizedresultspath` inside the python file `src/PyProject/Configuration.py`

 3- Specify the attack configuration as defined [here](src/PyProject/Configuration.py#L90)

 4- Provide the corresponding pickle files (classification models) to the specified attack in the previous step. The default location is defined [here](src/PyProject/Configuration.py#L30)
 
 5- The verification of the output before and after the applying the transformer can be enable/disabled from [here](src/PyProject/Configuration.py#L96). It's by default enabled. 

 6- To run the normalizer and generate the normalized dataset `python3 src/PyProject/normalizer/normalizer.py <TransformationCategory>`, where the current implementation supports the following categories: `API, Control, Misc, Declaration, all`

## Ouput of the Normalizer
Besides generating the normalized files for the provided dataset in the specified location `normalizedresultspath`, the normalizer also generates two CSV files `tranfromation_results.csv` and `count_results.csv` to report about the performed transformations for each `cpp` file.

# Debugging the Normalizer
We added debugging feature to the normalizer to normalize just a signle `.cpp` file. The variable `single` inside the python file `src/PyProject/Configuration.py` enables this debugging. Otherwise, it should be zero.

# Disclaimer
The normalizer has been developed to normalize code transformations defined [here](https://github.com/EQuiw/code-imitator/tree/master/src/LibToolingAST). Therefore, many of its libraries have been used as is or adapted.


# Citation 
If you are using our implementation, please cite our NeurIPS '22 paper. You may use the following BibTex entry:
```
@inproceedings{
wang2022robust,
title={Robust Learning against Relational Adversaries},
author={Yizhen Wang and Mohannad Alhanahnah and Xiaozhu Meng and Ke Wang and Mihai Christodorescu and Somesh Jha},
booktitle={Advances in Neural Information Processing Systems},
editor={Alice H. Oh and Alekh Agarwal and Danielle Belgrave and Kyunghyun Cho},
year={2022},
url={https://openreview.net/forum?id=WBp4dli3No6}
}
```

