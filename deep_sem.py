import sys
from PyQt5 import QtWidgets
from deep_sem.frontend.main import MainWindow

if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)

    mainWindow = MainWindow()
    mainWindow.setGeometry(0, 0, 1600, 1000)
    mainWindow.show()

    sys.exit(app.exec_())
