
import os
from collections import Counter
try:
    import xml.etree.cElementTree as ET
except ImportError:
    import xml.etree.ElementTree as ET
import numpy as np
from scipy import sparse
import yaml

import featurefunc
import util
import classifiers as cl

def extract_feats(ffs, fds, direc, datafile):
    rowfd = {}
    # parse file as an xml document
    tree = ET.parse(os.path.join(direc,datafile))
    # accumulate features
    [rowfd.update(ff(tree)) for ff in ffs]
    fds.append(rowfd)        

    return fds



## The following function does the feature extraction, learning, and prediction
def main():
    train_dir = "train"
    test_dir = "test"
    outputfile = "mypredictions-vec.csv"  # feel free to change this or take it as an argument

    lr = cl.SVM()

    # TODO put the names of the feature functions you've defined above in this list
    ffs = featurefunc.getFeatures()
    classes = {}
    ids = []
    fds = []

    for datafile in os.listdir(train_dir):
        # extract id and true class (if available) from filename
        id_str,clazz = datafile.split('.')[:2]
        ids.append(id_str)
        # add target class if this is training data
        if clazz != "X":
            classes[id_str] = util.malware_classes.index(clazz)

        extract_feats(ffs, fds, 'train', datafile)

    X,feat_dict = featurefunc.make_design_mat(fds,None)
    y = [classes[item] for item in ids]

    lr.fit(X,y,feat_dict)

    for i in feat_dict:
        print i
    
    # get rid of training data and load test data
    del X
    del y
    ids = []
    fds = []
    

    print "training complete. Now preparing for submit"

    for datafile in os.listdir(test_dir):
        # extract id and true class (if available) from filename
        id_str,clazz = datafile.split('.')[:2]
        ids.append(id_str)
        # add target class if this is training data
        if clazz != "X":
            classes[id_str] = util.malware_classes.index(clazz)

        extract_feats(ffs, fds, 'test', datafile)

    X,feat_dict = featurefunc.make_design_mat(fds,None)
    for i in feat_dict:
        print i
    

    preds = lr.predict(X)
    
    print "writing predictions..."
    util.write_predictions(preds, ids, outputfile)
    print "done!"

if __name__ == "__main__":
    main()
    