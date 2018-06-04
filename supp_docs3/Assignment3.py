import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.dummy import DummyClassifier
from sklearn.metrics import recall_score
from sklearn.metrics import recall_score, precision_score
from sklearn.svm import SVC
from sklearn.metrics import confusion_matrix
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import precision_recall_curve, roc_curve, auc
import matplotlib.pyplot as plt
from sklearn.model_selection import GridSearchCV


df = pd.read_csv('fraud_data.csv')

#percentage of the observations in the dataset are instances of fraud
print(df['Class'].sum()/df['Class'].count())

#X_train, X_test, y_train, y_test 
X = df.iloc[:,:-1]
y = df.iloc[:,-1]
X_train, X_test, y_train, y_test = train_test_split(X, y, random_state=0)

#Dummy that always predicts class 0
dummy_maj = DummyClassifier(strategy='most_frequent').fit(X_train,y_train)
dummy_maj_pred = dummy_maj.predict(X_test)
#Tuple with Dummy accuracy and recall
print((dummy_maj.score(X_test,y_test), recall_score(y_test,dummy_maj_pred)))

#Accuracy, recall, and precision using SVC classifer with the default parameters
#svm = SVC().fit(X_train,y_train)
#svm_pred = svm.predict(X_test)
#print((svm.score(X_test,y_test), recall_score(y_test,svm_pred),precision_score(y_test,svm_pred)))

#Using the SVC classifier with parameters {'C': 1e9, 'gamma': 1e-07}, what is the confusion matrix when using a threshold of -220 on the decision function
#svm2 = SVC(C = 1e9, gamma = 1e-07).fit(X_train,y_train)
#svm2_pred_thresh = svm2.decision_function(X_test) > -220
#cm = confusion_matrix(y_test,svm2_pred_thresh)
#print(cm)

#Train a logisitic regression classifier with default parameters using X_train and y_train
#For the logisitic regression classifier, create a precision recall curve and a roc curve using y_test and the probability estimates for X_test (probability it is fraud)
#Looking at the precision recall curve, what is the recall when the precision is 0.75?
#Looking at the roc curve, what is the true positive rate when the false positive rate is 0.16?
#This function should return a tuple with two floats, i.e. (recall, true positive rate)
lr = LogisticRegression().fit(X_train, y_train)
lr_pred = lr.predict(X_test)
lr_dec = lr.decision_function(X_test)
precision, recall, thresholds = precision_recall_curve(y_test, lr_pred)
fpr_lr, tpr_lr, _ = roc_curve(y_test, lr_dec)
closest_zero = np.argmin(np.abs(thresholds))
closest_zero_p = precision[closest_zero]
closest_zero_r = recall[closest_zero]
plt.figure()
plt.xlim([0.0, 1.01])
plt.ylim([0.0, 1.01])
plt.plot(precision, recall, label='Precision-Recall Curve')
plt.plot(closest_zero_p, closest_zero_r, 'o', markersize = 12, fillstyle = 'none', c='r', mew=3)
plt.xlabel('Precision', fontsize=16)
plt.ylabel('Recall', fontsize=16)
plt.axes().set_aspect('equal')
plt.show()

roc_auc_lr = auc(fpr_lr, tpr_lr)
plt.figure()
plt.xlim([-0.01, 1.00])
plt.ylim([-0.01, 1.01])
plt.plot(fpr_lr, tpr_lr, lw=3, label='LogRegr ROC curve (area = {:0.2f})'.format(roc_auc_lr))
plt.xlabel('False Positive Rate', fontsize=16)
plt.ylabel('True Positive Rate', fontsize=16)
plt.title('ROC curve', fontsize=16)
plt.legend(loc='lower right', fontsize=13)
plt.plot([0, 1], [0, 1], color='navy', lw=3, linestyle='--')
plt.axes().set_aspect('equal')
plt.show()

#Perform a grid search over the parameters listed below for a Logisitic Regression classifier, using recall for scoring and the default 3-fold cross validation.
#'penalty': ['l1', 'l2']
#'C':[0.01, 0.1, 1, 10, 100]
lr2 = LogisticRegression().fit(X_train, y_train)
grid_values = {'C': [0.01, 0.1, 1, 10, 100], 'penalty': ['l1', 'l2']}
grid = GridSearchCV(lr2, param_grid=grid_values, scoring='recall')
grid.fit(X_train, y_train)
cv_results = grid.cv_results_
results = np.array(cv_results['mean_test_score']).reshape(5,2)
print(results)
