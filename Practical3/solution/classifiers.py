import numpy as np
from sklearn import linear_model
from sklearn import svm
from sklearn import cross_validation

import util

class Classifier(object):
    def name(self):
        return 'unknown'

    def save(self, file):
        pass

    def load(self, file):
        pass

    def fit(self, X, y, feat_dict):
        pass

    def score(self, X, y):
        total = len(y)
        c = 0
        for i, j in zip(X,y):
            if i == j: c += 1
        return float(c) / float(total)
        '''
        # calculate accuracies
        item_count = 0
        accuracyByClass = []

        for i in range(len(util.malware_classes)):
            accuracyByClass.append({'true_pos':0, 'cond_pos':0, 'outcome_pos': 0, 'false_pos':0, 'false_neg':0})

        for i, fileid in enumerate(ids):
            if preds[i] == np.int64(classes[fileid]):
                item_count += 1
                accuracyByClass[classes[fileid]]['true_pos'] += 1
            else:
                accuracyByClass[int(preds[i])]['false_pos'] += 1
                accuracyByClass[classes[fileid]]['false_neg'] += 1
            accuracyByClass[classes[fileid]]['cond_pos'] += 1
            accuracyByClass[int(preds[i])]['outcome_pos'] += 1
    
        accuracy = float(item_count) / float(len(ids)) 
        j = 0
        for i in accuracyByClass:
            tp = float(i['true_pos'])
            fp = float(i['false_pos'])
            ocp = float(i['outcome_pos'])
            try:
                precision = tp/(tp+fp)
            except:
                precision = 0.0
            cp = float(i['cond_pos'])
            try:
                sensitivity = tp/cp
            except:
                sensitivity = 0.0
        #print i
        #print j, "Precision:", precision, "Sensitivity:",sensitivity
            j += 1

        return accuracy
        '''

    def predict(self, X):
        return np.ones(X.shape[0], np.int64) * 8 # hardcoded value for No virus


class RandomClassifier(Classifier):
    def __init__(self):
        self.learned_W = None

    def name(self):
        return 'random'

    def fit(self, X, y, feat_dict):
        self.learned_W = np.random.random((len(feat_dict),len(util.malware_classes)))
        return self.learned_W

    def predict(self, X):
        return np.argmax(X.dot(self.learned_W),axis=1)

class MostFrequent(Classifier):
    def name(self):
        return 'baseline'

class LogisticRegression(Classifier):
    def __init__(self):
        self.C = 100
        self.logreg = linear_model.LogisticRegression(C=self.C)

    def name(self):
        return 'LogisticRegression-'+str(self.C)

    def fit(self, X, y, feat_dict):
        self.logreg.fit(X, y)

    def predict(self, X):
        return self.logreg.predict(X)

class SVM(Classifier):
    def __init__(self):
        self.svm = svm.SVC(kernel='linear', C=1.0)

    def get_params(self, deep=False, *args):
        return self.svm.get_params(*args)

    def name(self):
        return 'SVM'

    def fit(self, X, y, feat_dict):
        self.svm.fit(X, y)

    def predict(self, X):
        return self.svm.predict(X)

def getClassifiers():
    return [
            LogisticRegression
           ]
