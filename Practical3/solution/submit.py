
import numpy as np
from scipy import sparse
import itertools as iter

import featurefunc as ff
import classifiers as cl
import util


## The following function does the feature extraction, learning, and prediction
def main():
    train_dir = "train"
    test_dir = "test"
    outputfile = "mypredictions.csv"  # feel free to change this or take it as an argument

    lr = cl.LogisticRegression()
    knn = cl.kNN()
    
    ds = ff.Dataset()

    print "training..."

    X, y, ids = ds.getDataset(train_dir)
    lr.fit(X,y)
    knn.fit(X,y)
    del X
    del y
    print "training complete. Now preparing for submit"

    X, y, ids = ds.getDataset(test_dir)
    predsLR = lr.predict(X)
    pbLR    = lr.classifier_().predict_proba(X)

    predskNN = knn.predict(X)
    pbkNN = knn.classifier_().predict_proba(X)

    featDict = ds.getFeatureDict()
    #print "feature", featDict['Swizzor_found']
    X_arr = X.toarray()

    finalpred = []
    for i in xrange(len(predsLR)):
        if X_arr[i][featDict['Swizzor_found']] > 0:
            choice = 10
        elif np.max(pbkNN[i]) > 0.8:
            # if kNN is more .8 sure, it is very accurate
            choice = predskNN[i]
        elif np.max(pbkNN[i]) - np.max(pbLR[i]) > 0.4:
            # if kNN is 0.4 more sure than LR, use that
            choice = predskNN[i]
        else:
            choice = predsLR[i]
        finalpred.append(choice)
    
    print "writing predictions..."
    util.write_predictions(finalpred, ids, outputfile)
    print "done!"

if __name__ == "__main__":
    main()
    
