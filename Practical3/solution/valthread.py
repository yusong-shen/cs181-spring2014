'''
validate.py - testing harness
'''
import os
from collections import Counter
try:
    import xml.etree.cElementTree as ET
except ImportError:
    import xml.etree.ElementTree as ET

import numpy as np
from sklearn.cross_validation import train_test_split
from sklearn.preprocessing import normalize
import csv
import datetime
import argparse

import featurefunc as ff
import classifiers as cl
import util

def validate(num_iterations, clf, direc, ds, ds2 = None):
    assert clf != None
    accuracy = []
    X, y, ids = ds.getDataset(direc)
    print "X len=",X.shape, "Y len=", len(y)
    weights = None
    for size in [0.3, 0.2, 0.1]: # try 3 fold, 5 fold and 10 fold
        print "size ",size
        #print "Item\tProbLR\tProbknn\tProbGb\tPredLR\tPredkNN\tPredGb\tChoice\tActual"
        for i in range(num_iterations):
            clf = cl.LogisticRegression()
            # TODO in train_test_split - how to keep track of ids to know which is the best
            # prediction for a given file
            X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=size)
            finalpred = []
            lrProbMean = 0.0
            lrAcc = 0.0

            lrconfidentButWrong = 0.0
            clf.fit(X_train,y_train)

            clf2 = clf.classifier_()

            df = clf2.predict_proba(X_test)

            preds = clf.predict(X_test)

            for i in range(len(df)):

                # choose the best prediction for LR / syscalls:
                # a2 = sorted(dict of rows)
                # i = 0 (next slice of rows) - iterate on each test example
                # beg = a2[i]
                # end = a2[i+1]
                # best prediction = max confidence of (preds[beg:end])

                #syscallMap = sorted(ds.threadMapping)

                lrProbMean += np.max(df[i])
                if preds[i] == y_test[i]: 
                    lrAcc += 1.0
                else:
                    if np.max(df[i]) > 0.50:
                        lrconfidentButWrong += 1

                #if np.max(dfknn[i]) - np.max(df[i]) > 0.4:
                #    choice = preds2[i]
                #else:
                #    choice = preds[i]
                #finalpred.append(choice)
                '''

                    print("%d\t%0.3f\t%d\t%d" % (i,
                                                 np.max(df[i]), 
                                                 choice,
                                                 y_test[i]))

                    print("%d\t%0.3f\t%0.3f\t%0.3f\t%d\t%d\t%d\t%d\t%d" % (i,
                                                 np.max(df[i]), 
                                                 np.max(dfknn[i]),
                                                 np.max(dfgbrt[i]),
                                                 preds[i],
                                                 preds2[i],
                                                 preds3[i],
                                                 choice,
                                                 y_test[i]))

                '''
            s = clf.score(preds,y_test)
            accuracy.append(s)
            l = float(len(preds))
            print "lrConfident (0.5) but wrong:", float(lrconfidentButWrong) / l

            print "LR mean prob:", lrProbMean/l, "accuracy:", lrAcc/l
            if weights is None:
                weights = np.array(clf.weights())
            else:
                weights = np.vstack([weights,clf.weights()])
            clr = None

    return np.array(accuracy), weights

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-i', '--iterations',help='Number of cross validation iterations to run', type=int)
    parser.add_argument('-f', '--full',help='full or minimal training run (default minimal)',action='store_true')
    parser.add_argument('-t', '--thread',help='use thread metrics (default process)', action='store_true')
    parser.add_argument('classifier',nargs='?', help='Which classifer to use (default all)')
    args = parser.parse_args()

    if args.full:
        direc = 'train'
        timestamp = datetime.datetime.now().strftime("%H:%M:%S")
        print("%s Start of full run" % (timestamp))

    else:
        direc = 'mintrain'

    if args.iterations:
        num_iter = int(args.iterations)
        assert num_iter > 0
        assert num_iter < 1001
    else:
        num_iter = 5

    if args.classifier:
        classifier = args.classifier
    else:
        classifier = None

    if args.thread:
        ds = ff.Dataset(ff.MetricType().thread)
    else:
        ds = ff.Dataset()

    ds2 = None

    with open('error_log.txt', 'a') as errfile:
        wr = csv.writer(errfile, dialect = 'excel')
    
        for clf in cl.getClassifiers():
            c = clf()
            if classifier is not None:
                # let only a specific classifier run
                if c.name() != classifier: continue
                # special case for combined
                if c.name() == 'Combined':
                    # create two datasets and ignore the -t parameter
                    ds = ff.Dataset(ff.MetricType().process)
                    ds2 = ff.Dataset(ff.MetricType().thread)
            accuracy, weights = validate(num_iter, c, direc, ds, ds2)
            timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            avgAcc = accuracy.mean()
            stdAcc = accuracy.std() * 2

            wr.writerow([timestamp, num_iter, direc, c.name(), avgAcc, stdAcc, 
                         np.max(accuracy), np.min(accuracy)])

            try:
                with open('weight_'+c.name()+'.txt', 'w') as weightfile:
                    wcsv = csv.writer(weightfile, dialect='excel')
                    wcsv.writerow(["Key","mean","std"])
                    w_mean = np.abs(weights.mean(0))
                    w_std  = weights.std(0) * 2

                    for i, key in enumerate(ds.getFeatureDict()):
                        wcsv.writerow([key, w_mean[i], w_std[i]])
            except:
                print "no weights found"

            timestamp = datetime.datetime.now().strftime("%H:%M:%S")

            print("%s %s accuracy: %0.2f (+/- %0.2f)" % (timestamp, c.name(), avgAcc, stdAcc))
        
if __name__ == "__main__":
    main()