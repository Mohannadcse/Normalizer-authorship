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
 1- Specifying the location of the `datasetpath` and `normalizedresultspath` inside the python file `src/PyProject/Configuration.py`

 2- Specify the attack configuration as defined [here](https://github.com/EricYizhenWang/RobustAuthorshipAttribution/blob/normalizer/src/PyProject/Configuration.py#L90)

 3- Provide the corresponding pickle files (classification models) to the specified attack in the previous step. The default location is defined [here](https://github.com/EricYizhenWang/RobustAuthorshipAttribution/blob/normalizer/src/PyProject/Configuration.py#L30)
 
 4- The verification of the output before and after the applying the transformer can be enable/disabled from [here](https://github.com/EricYizhenWang/RobustAuthorshipAttribution/blob/normalizer/src/PyProject/Configuration.py#L96). It's by default enabled. 

 5- To run the normalizer and generate the normalized dataset `python3 src/PyProject/normalizer/normalizer.py <TransformationCategory>`, where the current implementation supports the following categories: `API, Control, Misc, Declaration, all`

## Ouput of the Normalizer
Besides generating the normalized files for the provided dataset in the specified location `normalizedresultspath`, the normalizer also generates two CSV files `tranfromation_results.csv` and `count_results.csv` to report about the performed transformations for each `cpp` file.

# Debugging the Normalizer
We added debugging feature to the normalizer to normalize just a signle `.cpp` file. The variable `single` inside the python file `src/PyProject/Configuration.py` enables this debugging. Otherwise, it should be zero.