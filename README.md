# Cafe Accessibility

## Description

This project measures how walkable cafes in Seattle are from King County Metro bus stops and determines which bus stops have the most cafes near them. 
 
## Set up

Before doing anything please fork and clone this repository. 

### Environment creation

Before running an analysis, you must install the necessary packages. It is recommended that you install them into a [conda environment](https://docs.conda.io/en/latest/) but please to use the environment/container of your choice. Below are instructions for creating a `conda` environment and installing the required packages into it.

1. Download and install [conda](https://docs.conda.io/projects/conda/en/latest/user-guide/install/index.html)
2. Create an environment using the following command:

```
conda env create -f environment.yml
```

This will install all of the packages required to run the analysis. 

## Running this project

1. Activate the `conda` environment using the following command:

```
conda activate transportation_data_analysis
```

2. TBD

```
python main.py
```

3. Run the updated command.
4. Check the output directory you specified and rerun the script as needed.

## Contributing to this project

### Reporting a bug

To report a bug, please create an issue, tag it as a `bug` and write a short description of the problem and attach a screenshot of any error message.

### Suggesting a new feature

To suggest a new feature, please create an issue, tag it as a `enhancement` and write a short description of what you would like to see added.

### Setting up an development environment

Since this project is not currently a package, you can use the `cafe_accessability` environment to make modifications and run tests.

### Making modifications

When making modifications, please create a new branch and submit a pull request when you are ready to merge with the `main` branch. Please refrain from making changes on `main`.

### Running tests

For any function you add, please add unit tests for any outputs and any exceptions that are raised. This project currently has a test framework that uses [pytest](https://docs.pytest.org/en/8.0.x/) as a test runner. [Github actions](https://docs.github.com/en/actions) is currently setup to run all tests when someone tries to merge a pull request and push commits. You can also run tests from the `tests` directory using the following command:

```
pytest
```
