import sys
import tempfile
from graphviz import Digraph
from PyQt5 import QtGui, QtWidgets


class PaintPicture(QtWidgets.QDialog):
    def __init__(self, models, evaluations, variable_description=None):
        super(PaintPicture, self).__init__()

        if variable_description is None:
            variable_description = dict()
        self.models = models
        self.variableDescription = variable_description
        self.evaluations = evaluations

        self.current_id = 0
        self.current_label = None
        self.current_image = None
        self.current_evaluation = None

        layout = QtWidgets.QVBoxLayout()

        self.nxt_btn = QtWidgets.QPushButton('Next')
        self.nxt_btn.clicked.connect(self._next_model)
        layout.addWidget(self.nxt_btn)

        self.pre_btn = QtWidgets.QPushButton('Previous')
        self.pre_btn.clicked.connect(self._previous_model)
        layout.addWidget(self.pre_btn)

        self.save_btn = QtWidgets.QPushButton('Save')
        self.save_btn.clicked.connect(self._save_image)
        layout.addWidget(self.save_btn)

        self.setLayout(layout)
        self.show()

        # Render the first model.
        self._graphviz_render()
        self._update_button_status()

    def _next_model(self):
        self.current_id += 1
        self._graphviz_render()

        self._update_button_status()

    def _previous_model(self):
        self.current_id -= 1
        self._graphviz_render()

        self._update_button_status()

    def _update_button_status(self):
        if self.current_id <= 0:
            self.pre_btn.setEnabled(False)
        else:
            self.pre_btn.setEnabled(True)

        if self.current_id >= len(self.models) - 1:
            self.nxt_btn.setEnabled(False)
        else:
            self.nxt_btn.setEnabled(True)

        if self.current_label:
            self.save_btn.setEnabled(True)
        else:
            self.save_btn.setEnabled(False)

    def _save_image(self):
        name = QtWidgets.QFileDialog.getSaveFileName(self, 'Save File', directory='dsem_result', filter='*.png')
        if name:
            self.current_image.save(name[0], format='png')

    def _graphviz_render(self):
        # Potential Engine Options = ['dot', 'neato', 'fdp']
        dot = Digraph(comment='Result from DSEM', engine='fdp')

        model = self.models[self.current_id]
        measurement_dict = model['measurement_dict']
        regressions_dict = model['regressions_dict']
        covariance_dict = model['covariance_dict']

        for latent in measurement_dict.keys():
            for observed in measurement_dict[latent]:
                if observed in self.variableDescription.keys():
                    dot.edge(self.variableDescription[observed], latent)
                else:
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

        imageLabel = QtWidgets.QLabel()
        pixmap = QtGui.QPixmap.fromImage(image)
        pixmap = pixmap.scaledToHeight(500)
        imageLabel.setPixmap(pixmap)

        evaluationLabel = QtWidgets.QLabel()
        evaluationLabel.setText(str(self.evaluations[self.current_id]))

        layout = self.layout()
        if self.current_evaluation:
            layout.removeWidget(self.current_evaluation)
            self.current_evaluation.deleteLater()
        if self.current_label:
            layout.removeWidget(self.current_label)
            self.current_label.deleteLater()
        layout.addWidget(evaluationLabel)
        layout.addWidget(imageLabel)

        self.current_label = imageLabel
        self.current_evaluation = evaluationLabel
        self.current_image = image


class GraphvizVisualization:
    def __init__(self, models, evaluation, variable_description=None):
        self.app = QtWidgets.QApplication(sys.argv)
        self.windows = PaintPicture(models, evaluation, variable_description)

    def show(self):
        self.app.exec_()


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

    variableDescription = {
        'y1': 'Expert ratings of the freedom of the press in 1960',
        'y2': 'The freedom of political opposition in 1960',
        'y3': 'The fairness of elections in 1960',
        'y4': 'The effectiveness of the elected legislature in 1960',
        'y5': 'Expert ratings of the freedom of the press in 1965',
        'y6': 'The freedom of political opposition in 1965',
        'y7': 'The fairness of elections in 1965',
        'y8': 'The effectiveness of the elected legislature in 1965',
        'x1': 'The gross national product (GNP) per capita in 1960',
        'x2': 'The inanimate energy consumption per capita in 1960',
        'x3': 'The percentage of the labor force in industry in 1960'
    }

    models = [sample_model, sample_model, sample_model]

    vis = GraphvizVisualization(models, variableDescription)
    vis.show()
