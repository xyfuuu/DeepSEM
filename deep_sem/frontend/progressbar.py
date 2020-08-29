#!/usr/bin/python3
# -*- coding: utf-8 -*-

from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
import PyQt5.QtCore as QtCore

from ..backend.rl_scheduler import RLScheduler


class ProgressBar(QDialog):
    def __init__(self, train_fn, data, search_space, verified_proportion, **kwargs):
        super().__init__()
        self.setWindowTitle('Data Processing')
        self.pbar = QProgressBar(self)
        self.pbar.setGeometry(30, 40, 200, 25)
        self.timer = QBasicTimer()
        self.timer.start(100, self)
        self.step = 0
        self.setGeometry(300, 300, 280, 170)

        self.thread = RLScheduler(train_fn, data, search_space, verified_proportion, **kwargs)
        self.thread.sinOut.connect(self.set_process)
        self.thread.finished.connect(self.on_finished)

    def run(self):
        self.thread.start()

    @QtCore.pyqtSlot()
    def on_finished(self):
        self.close()

    def get_best_config(self):
        return self.thread.get_best_config()

    def get_best_reward(self):
        return self.thread.get_best_reward()

    def get_topk_config(self, k):
        return self.thread.get_topk_config(k)

    def training_history(self):
        return self.thread.training_history()

    def set_process(self, target):
        if self.step >= 100:
            self.timer.stop()
            return
        self.step = target
        self.pbar.setValue(self.step)
