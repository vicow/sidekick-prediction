from __future__ import print_function
import os
import sys
sys.path.insert(0, os.path.abspath('../utils/'))  # Add sibling to Python path
sys.path.insert(0, os.path.abspath('../src/'))  # Add sibling to Python path
import numpy as np
import pickle as cp
from src.dataset import Sidekick
import GPy
from math import floor
from utils import ProgressBar


data_dir = "../../data/sidekick"


def evaluate(X_test, y_test, model):
    se_successful = []
    se_failed = []
    se_total = []
    accuracy = 0
    for i, x_test in enumerate(X_test):
        x_test = np.expand_dims(x_test, axis=0)
        y_pred, y_var = model.predict(x_test)
        y_pred = y_pred[0, 0]
        y_var = y_var[0, 0]
        y_actual = y_test[i]
        se = (y_pred - y_actual)**2
        se_total.append(se)
        if y_test[i] >= 1.0:  # Project is successful
            se_successful.append(se)
        else:  # project is failed
            se_failed.append(se)
        if (y_pred >= 1 and y_actual >= 1) or (y_pred < 1 and y_actual < 1):
            accuracy += 1

    rmse_successful = np.sqrt(np.mean(se_successful))
    rmse_failed = np.sqrt(np.mean(se_failed))
    rmse_total = np.sqrt(np.mean(se_total))
    accuracy /= len(y_test)

    return rmse_successful, rmse_failed, rmse_total, accuracy


def one_run(projects_train, projects_test, outlier_threshold):
    rmse_failed_run = []
    rmse_success_run = []
    rmse_run = []
    accuracy_run = []
    relative_time = np.linspace(0.025, 1, 40)
    bar = ProgressBar(end_value=len(relative_time), text="Time steps", count=True)
    bar.start()
    for i, rel_t in enumerate(relative_time):
        #n_samples = 1
        #t0 = 1
        #t1 = 500
        #samples = subsample(t0, t1, n_samples)
        samples = rel_t * 1000 - 1
        t = 1
        T = 999
        ARD = False

        projects_train = [p for p in projects_train if p.money[T] < outlier_threshold and p.money[samples] < outlier_threshold]
        projects_test = [p for p in projects_test if p.money[T] < outlier_threshold and p.money[samples] < outlier_threshold]

        X_train = np.ndarray(shape=(len(projects_train), t), buffer=np.array([p.money[samples] for p in projects_train]), dtype=float)
        y_train = np.expand_dims(np.array([p.money[T] for p in projects_train]), axis=1)
        X_test = np.ndarray(shape=(len(projects_test), t), buffer=np.array([p.money[samples] for p in projects_test]), dtype=float)
        y_test = np.expand_dims(np.array([p.money[T] for p in projects_test]), axis=1)

        kernel = GPy.kern.RBF(input_dim=t, ARD=ARD)
        m = GPy.models.GPRegression(X_train, y_train, kernel)
        m.optimize()

        rmse_failed, rmse_success, rmse, accuracy = evaluate(X_test, y_test, m)
        rmse_failed_run.append(rmse_failed)
        rmse_success_run.append(rmse_success)
        rmse_run.append(rmse)
        accuracy_run.append(accuracy)

        bar.update(i)

    return rmse_failed_run, rmse_success_run, rmse_run, accuracy_run


def learning_curve(seed=2, runs=10, light=False, outlier_threshold=10):
    sk = Sidekick(data_dir=data_dir, seed=seed)
    sk.load(light=light)

    rmse_failed_all = []
    rmse_success_all = []
    rmse_all = []
    accuracy_all = []
    for r in range(runs):
        projects_train, projects_test = sk.split(threshold=0.7, shuffle=True)
        n_test = len(projects_test)
        projects_validation = projects_test[:floor(n_test*3/5)]
        projects_test = projects_test[floor(n_test*3/5):]

        rmse_failed_run, rmse_success_run, rmse_run, accuracy_run = one_run(projects_train, projects_test, outlier_threshold)
        rmse_failed_all.append(rmse_failed_run)
        rmse_success_all.append(rmse_success_run)
        rmse_all.append(rmse_run)
        accuracy_all.append(accuracy_run)
        with open('gp_rmse_failed_outlier_%s.pkl' % outlier_threshold, 'wb') as f:
            cp.dump(rmse_failed_all, f)
        with open('gp_rmse_success_outlier_%s.pkl' % outlier_threshold, 'wb') as f:
            cp.dump(rmse_success_all, f)
        with open('gp_rmse_outlier_%s.pkl' % outlier_threshold, 'wb') as f:
            cp.dump(rmse_all, f)
        with open('gp_accuracy_outlier_%s.pkl' % outlier_threshold, 'wb') as f:
            cp.dump(accuracy_all, f)

    return rmse_failed_all, rmse_success_all, rmse_all, accuracy_all


rmse_failed_all, rmse_success_all, rmse_all, accuracy_all = learning_curve(seed=2,
                                                                           runs=10,
                                                                           light=True,
                                                                           outlier_threshold=20)