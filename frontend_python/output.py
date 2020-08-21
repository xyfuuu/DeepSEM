import sys
import tempfile
from graphviz import Digraph
from PyQt5 import QtGui, QtWidgets


class PaintPicture(QtWidgets.QDialog):
    def __init__(self, model):
        super(PaintPicture, self).__init__()

        self.model = model

        layout = QtWidgets.QVBoxLayout()
        self.img_btn = QtWidgets.QPushButton('Render')
        self.img_btn.clicked.connect(self.graphvizRender)
        layout.addWidget(self.img_btn)

        self.setLayout(layout)
        self.show()

    def graphvizRender(self):
        # Potential Engine Options = ['dot', 'neato', 'fdp']
        dot = Digraph(comment='Result from DSEM', engine='dot')

        measurement_dict = self.model['measurement_dict']
        regressions_dict = self.model['regressions_dict']
        covariance_dict = self.model['covariance_dict']

        for latent in measurement_dict.keys():
            for observed in measurement_dict[latent]:
                dot.edge(observed, latent)

        for latent1 in regressions_dict.keys():
            for latent2 in regressions_dict[latent1]:
                dot.edge(latent1, latent2)

        for variable1 in covariance_dict.keys():
            for variable2 in covariance_dict[variable1]:
                dot.edge(variable1, variable2, dir='both')

        file_name = tempfile.mktemp()
        file_format = 'png'
        dot.render(file_name, format=file_format)
        full_path = file_name + '.' + file_format

        image = QtGui.QImage(full_path)

        self.imageLabel = QtWidgets.QLabel()
        self.imageLabel.setPixmap(QtGui.QPixmap.fromImage(image))

        layout = self.layout()
        layout.addWidget(self.imageLabel)


if __name__ == "__main__":
    sample_model = {'measurement_dict': {
        'factor1': ['y3', 'y4', 'y7', 'y8'],
        'factor2': ['x1', 'x2', 'x3'],
        'factor3': ['y1', 'y2', 'y5', 'y6']
    }, 'regressions_dict': {
        'factor2': ['factor3'],
    }, 'covariance_dict': {
        'factor3': ['factor1']
    }}

    app = QtWidgets.QApplication(sys.argv)
    widget = PaintPicture(sample_model)
    sys.exit(app.exec_())
