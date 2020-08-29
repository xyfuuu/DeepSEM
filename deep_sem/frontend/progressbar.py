#!/usr/bin/python3
# -*- coding: utf-8 -*-

import sys
import time
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *

from ..backend.rl_scheduler import RLScheduler


class ProgressBar(QDialog):
    def __init__(self, train_fn, **kwargs):
        super().__init__()
        self.setWindowTitle('Data Processing')
        self.pbar = QProgressBar(self)
        self.pbar.setGeometry(30, 40, 200, 25)
        self.timer = QBasicTimer()
        self.timer.start(100, self)
        self.step = 0
        self.setGeometry(300, 300, 280, 170)

        self.show()

        self.thread = RLScheduler(train_fn, **kwargs)
        # self.thread = Worker()
        # self.thread.start()
        self.thread.sinOut.connect(self.setProcess)

    def run(self):
        self.thread.start()

    def join_jobs(self):
        self.thread.join_jobs()

    def get_best_config(self):
        return self.thread.get_best_config()

    def get_best_reward(self):
        return self.thread.get_best_reward()

    def get_topk_config(self, k):
        return self.thread.get_topk_config(k)

    def training_history(self):
        return self.thread.training_history()

    def setProcess(self, target):
        if self.step >= 100:
            self.timer.stop()
            return
        self.step = target
        self.pbar.setValue(self.step)

    def slotStart(self):
        # 开始按钮不可点击，线程开始
        self.btnStart.setEnabled(False)
        self.thread.start()
        print("Done Start")


class Worker(QThread):
    sinOut = pyqtSignal(int)

    def __init__(self, parent=None):
        super(Worker, self).__init__(parent)
        self.working = True
        self.num = 0

    def __del__(self):
        self.wait()

    def run(self):
        for i in range(101):
            time.sleep(0.1)
            self.sinOut.emit(i)


class ProgressVisualization:
    def __init__(self, train_fn, **kwargs):
        self.app = QApplication(sys.argv)
        # self.progressBar = ProgressBar(train_fn, **kwargs)
        self.windows = ProgressBar(train_fn, **kwargs)
        # self.progressBar

    def run(self):
        self.windows.run()

    def join_jobs(self):
        self.windows.join_jobs()

    def get_best_config(self):
        return self.windows.get_best_config()

    def get_best_reward(self):
        return self.windows.get_best_reward()

    def get_topk_config(self, k):
        return self.windows.get_topk_config(k)

    def training_history(self):
        return self.windows.training_history()

    def show(self):
        self.app.exec_()
