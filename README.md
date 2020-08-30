# Deep SEM

Our project aims to apply frontier techniques in DL to Structural Equation Modeling (SEM, a popular analysis method in social science). It is supposed to automate the model refining process in SEM, which requires experts deveting hours and hours for now.
<br>

<p align="center">
  <img alt="demo" src="https://user-images.githubusercontent.com/29430011/91650118-0c500000-eaae-11ea-9af5-bc66779c5f22.gif">
</p>

Features
========
* Powerful RL algorithm.
* User-friendly UI.
* Runs on both Linux, MacOS.

Get started
===========
To use this project you need to have a basic understanding of SEM which is a famous analysis technique in social science. Go to [wiki](https://en.wikipedia.org/wiki/Structural_equation_modeling) for a brief introduction if you are not familiar with SEM.

Then you nees some data collected by [scales](https://en.wikipedia.org/wiki/Likert_scale). If you don't have any, there's some data in `/data` for you to play around.

Then launch the program to enjoy our project.

Usage
=====
To launch the program, run the following command in bash:

```bash
chmod +x run.sh
./run.sh
```

This program is fairly easy to use and follows almost the same pattern as [SPSS AMOS](https://www.ibm.com/hk-en/marketplace/structural-equation-modeling-sem). Or you can refer to the gif at the beginning of this README.

Requirements
============
This project is essentially written in Python and requires following packages:

* autogluon >= 0.0.13
* graphviz >= 0.14
* numpy >= 1.17.4
* PyQt5 >= 5.14.2
* rpy2 >= 3.3.5

Run the following code in the project folder to install all the requirements:

```bash
pip install -r requirements.txt
```

Due to one key package we used, autogluon, doesn't support Windwos, this project requires MacOS or Linux.

File Structure
===

Key project files are organized in the following structure:

![File Structure](https://user-images.githubusercontent.com/29430011/91650226-7c12ba80-eaaf-11ea-8e01-6b9063ebc37b.png)

FAQ
===

### Why our project?
Our project intends to replace the Model Modification section in the current SEM pipeline which requires experts devoting hours and hours for now with RL. It saves you time and is very likely to provide a better results than expert proposed.

### Run into problems?
This project is still in early development stage. If you run into problems please kindly open an issue in this github project.

