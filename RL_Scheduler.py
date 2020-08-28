import numpy as np
import pickle as pkl
import logging
import sys
import autogluon as ag
import matplotlib.pyplot as plt
import mxnet as mx

from collections import OrderedDict
from autogluon.utils import (save, load, mkdir, try_import_mxboard, tqdm)
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *

import logging
logger = logging.getLogger(__name__)

class RLScheduler(ag.scheduler.RLScheduler, QThread):
    sinOut = pyqtSignal(int)

    def __init__(self, train_fn, **kwargs):
        ag.scheduler.RLScheduler.__init__(self, train_fn, **kwargs)
        QThread.__init__(self)
        self.working = True
        self.num = 0

    def get_topk_config(self, k):
        """Returns top k configurations found so far.
        """
        with self.LOCK:
            if self.searcher.results:
                topk_configs = list()
                for config_pkl, reward in sorted(self.searcher.results.items(), key=lambda item: -item[1]):
                    topk_configs.append(pkl.loads(config_pkl))
                    if len(topk_configs) >= k:
                        break
                return topk_configs
            else:
                return list()

    def run(self, **kwargs):
        ag.scheduler.RLScheduler.run(self, **kwargs)

    def _run_sync(self):
        decay = self.ema_baseline_decay
        for i in tqdm(range(self.num_trials // self.controller_batch_size + 1)):
            with mx.autograd.record():
                # sample controller_batch_size number of configurations
                print(i * 100 // (self.num_trials // self.controller_batch_size + 1))
                self.sinOut.emit(i * 100 // (self.num_trials // self.controller_batch_size + 1))
                batch_size = self.num_trials % self.num_trials \
                    if i == self.num_trials // self.controller_batch_size \
                    else self.controller_batch_size
                if batch_size == 0: continue
                configs, log_probs, entropies = self.controller.sample(
                    batch_size, with_details=True)
                # schedule the training tasks and gather the reward
                rewards = self.sync_schedule_tasks(configs)
                print(rewards)
                print("rewards?")
                print(rewards)
                # substract baseline
                if self.baseline is None:
                    self.baseline = rewards[0]
                avg_rewards = mx.nd.array([reward - self.baseline for reward in rewards],
                                          ctx=self.controller.context)
                # EMA baseline
                for reward in rewards:
                    self.baseline = decay * self.baseline + (1 - decay) * reward
                # negative policy gradient
                log_probs = log_probs.sum(axis=1)
                loss = - log_probs * avg_rewards#.reshape(-1, 1)
                loss = loss.sum()  # or loss.mean()

            # update
            loss.backward()
            self.controller_optimizer.step(batch_size)
            logger.debug('controller loss: {}'.format(loss.asscalar()))
    
    def _run_async(self):
        ag.scheduler.RLScheduler._run_async(self)
    
    def sync_schedule_tasks(self, configs):
        return ag.scheduler.RLScheduler.sync_schedule_tasks(self, configs)