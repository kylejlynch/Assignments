import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import PolynomialFeatures
from sklearn.metrics.regression import r2_score
from sklearn.linear_model import Lasso, LinearRegression

np.random.seed(0)
n = 15
x = (np.linspace(0,10,n) + np.random.randn(n)/5)
y = (np.sin(x)+x/6 + np.random.randn(n)/10)
data = pd.DataFrame({'X' : x, 'y' : y})

X_train, X_test, y_train, y_test = train_test_split(data['X'], data['y'], random_state=0)

# You can use this function to help you visualize the dataset by
# plotting a scatterplot of the data points
# in the training and test sets.

import matplotlib.pyplot as plt
plt.figure()
plt.scatter(X_train, y_train, label='training data')
plt.scatter(X_test, y_test, label='test data')
plt.legend(loc=4)

res = np.zeros((4,100))
for i,deg in enumerate([1,3,6,9]) :
    poly = PolynomialFeatures(degree=deg)
    X_poly = poly.fit_transform(X_train.values.reshape(-1,1))
    linreg = LinearRegression().fit(X_poly, y_train)
    y = linreg.predict(poly.fit_transform(np.linspace(0,10,100).reshape(-1,1)))
    res[i,:] = y


r2_train = np.zeros(10)
r2_test = np.zeros(10)
for i in range(10):
    poly = PolynomialFeatures(degree=i)
    X_poly = poly.fit_transform(X_train.values.reshape(-1,1))
    linreg = LinearRegression().fit(X_poly, y_train)        
    r2_train[i] = linreg.score(X_poly, y_train)
    X_test_poly = poly.fit_transform(X_test.values.reshape(-1,1))
    r2_test[i] = linreg.score(X_test_poly, y_test)
#print((r2_train,r2_test))

# Create Polinomial Features
poly = PolynomialFeatures(degree=12)

# Shape Polinomial Features
X_polytrain = poly.fit_transform(X_train.values.reshape(-1,1))
X_polytest = poly.fit_transform(X_test.values.reshape(-1,1))

# Linear Regression
linreg = LinearRegression().fit(X_polytrain, y_train)
linear_r2_test = linreg.score(X_polytest, y_test)

# Lasso Regression
linlasso = Lasso(alpha=0.01, max_iter = 10000).fit(X_polytrain, y_train)
lasso_r2_test = linlasso.score(X_polytest, y_test)

#print(linear_r2_test, lasso_r2_test)


#Mushrooms.csv
mush_df = pd.read_csv('mushrooms.csv')
mush_df2 = pd.get_dummies(mush_df)

X_mush = mush_df2.iloc[:,2:]
y_mush = mush_df2.iloc[:,1]

# use the variables X_train2, y_train2 for Question 5
X_train2, X_test2, y_train2, y_test2 = train_test_split(X_mush, y_mush, random_state=0)

# For performance reasons in Questions 6 and 7, we will create a smaller version of the
# entire mushroom dataset for use in those questions.  For simplicity we'll just re-use
# the 25% test split created above as the representative subset.
#
# Use the variables X_subset, y_subset for Questions 6 and 7.
X_subset = X_test2
y_subset = y_test2

from sklearn.tree import DecisionTreeClassifier
clf = DecisionTreeClassifier(random_state=0).fit(X_train2, y_train2)
desc_list = pd.DataFrame({'feature' : X_train2.columns , 'importance' : clf.feature_importances_}).sort_values(by='importance', ascending=False)
desc_list = desc_list.feature.head().tolist()
print(desc_list,type(desc_list))

from sklearn.svm import SVC
from sklearn.model_selection import validation_curve

svc = SVC(kernel='rbf', C=1, random_state=0)
gamma = np.logspace(-4,1,6)
subtrain_scores, subtest_scores = validation_curve(svc, X_subset, y_subset,
                        param_name='gamma',
                        param_range=gamma,
                        scoring='accuracy')

scores = (subtrain_scores.mean(axis=1), subtest_scores.mean(axis=1))

#for i, num in enumerate(np.logspace(-4,1,6)):
#    print(i, num)

