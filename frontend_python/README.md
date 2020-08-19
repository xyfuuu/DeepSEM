# Python Frontend

The frontend of DESM implemented with PyQt5. The UI design is largely borrowed from the Qt version of frontend.

## File Introduction

- `main.py` : UI layout for the input canvas.
- `diagram_item.py`: Components of the canvas, including: Arrow, Double Arrow, Rectangle, Text. 
- `output.py`:  Parse the output model and display it as picture.
- ` images/` & `diagramscene.qrc` & `diagramscene_rc.py`: Resources and assets required by UI design. If you have no intention to change UI layout, you can totally ignore those files and folder. 

## Try It Out

Run `python3 main.py` in your terminal to run the input canvas.

Run `python3 output.py` in your terminal to try the visualization of searched results.

## Develop Guide

1. If you wanna add call backend functions from the frontend, you can probably do so by modifying `doCalculation()` in Class `MainWindow` located in `main.py`.
2. If you wanna show a searched result call create an instance of `PaintPicture` in `output.py`.
3. SEM Models passed between frontend and backend are suggested to follow the following format:
    * The model should be a map contains 3 submaps to store Measurement Model, Regressions Model, and Covariance Relationships separately. 
    * The map stores information on Measurement Model contains relationship between observed variables and latent variables (each observed variables connect to at most 1 latent variable). The key values are the name of latent variables and the corresponding values is a list contains observed variables connected to thi latent variable. 
    * The map stores information about Regressions Model contains follows similar schema. The very only difference is that variables in the list is those latent variables with a __directed__ connection to the latent variable indicated by the corresponding key.
    * The map stores Covariance Relationships is very much the same. The very only difference is that variables in the list is those variables with a __bi-directed__ connection (double headed arrows in the canvas) to the variable indicated by the corresponding key.
    * An example goes like this: 
    ```python
    sample_model = {'measurement_dict': {
        'factor1': ['y3', 'y4', 'y7', 'y8'],
        'factor2': ['x1', 'x2', 'x3'],
        'factor3': ['y1', 'y2', 'y5', 'y6']
    }, 'regressions_dict': {
        'factor2': ['factor3'],
    }, 'covariance_dict': {
        'factor3': ['factor1']
    }}
    ```