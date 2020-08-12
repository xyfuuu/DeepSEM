# DSEM
Our project aims to apply frontier techniques in DL to Structural Equation Modeling (SEM, a popular analysis method in social science). It is supposed to automate the model refining process in SEM, which requires experts deveting hours and hours for now.

## File Structure

In this section, we would like to present you with how files in this project distributed. We will go through files in the top level.

Firstly, our project is essentially some sort of a NAS task. As NAS can be generally devided into 3 parts, there're 3 python files here accordingly:

- Search Space -> `search_space.py`
- Search Strategy -> `search_strategy.py`
- Model Evaluation/Reward Function -> `model_evaluation.py`

Secondly, in our project, we utilize conventional SEM widely used in social science. `SEM.py` contains code of this part.

Thirdly, there's a python file named `main.py` which combined data loading, ML model initializing and everything else together. You can train this project by running `python3 main.py`.

As you can see, there're 2 folders here. The folder named `data` contains data for developemnt and demos to use. The folder named `notebooks` contains several jupyter notebooks which are primaryly for development use. Typically, you can ignore those 2 folders.

