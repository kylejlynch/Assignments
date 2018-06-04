import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression
from sklearn.metrics import roc_curve, auc
from sklearn.neighbors import KNeighborsClassifier
from sklearn.svm import SVC
from sklearn.preprocessing import MinMaxScaler
scaler = MinMaxScaler()

data = pd.read_csv("train.csv", encoding = 'ISO-8859-1', low_memory=False).set_index('ticket_id')
datatest = pd.read_csv("test.csv", encoding = 'ISO-8859-1', low_memory=False).set_index('ticket_id')

data.dropna(subset = ['compliance'],inplace=True)
data['violation_cat'] = data['violation_code'].astype('category').cat.codes
violation_lookup = dict(zip(data['violation_code'].unique(), data['violation_cat'].unique()))
data['zip_code_cat'] = data['zip_code'].astype('category').cat.codes
zip_code_lookup = dict(zip(data['zip_code'].unique(), data['zip_code_cat'].unique()))
data['judge_sq'] = np.square(data['judgment_amount'])

datatest['violation_cat'] = data['violation_code'].astype('category').cat.codes
violation_lookup = dict(zip(datatest['violation_code'].unique(), datatest['violation_cat'].unique()))
datatest['zip_code_cat'] = datatest['zip_code'].astype('category').cat.codes
zip_code_lookup = dict(zip(datatest['zip_code'].unique(), datatest['zip_code_cat'].unique()))
datatest['judge_sq'] = np.square(datatest['judgment_amount'])

X = data[['late_fee', 'judgment_amount']]
y = data['compliance']
X_train, X_test, y_train, y_test = train_test_split(X, y, random_state=0)

#testX = datatest[['late_fee', 'judge_sq']]

knn = KNeighborsClassifier(n_neighbors = 15).fit(X_train, y_train)
y_score = knn.predict_proba(X_test)[:,1]

#testy_score = knn.predict_proba(testX)[:,1]
#df = pd.DataFrame(y_score).set_index(X_test.index)
#testdf = pd.DataFrame({'compliance' : testy_score}).set_index(testX.index)
#testdf = pd.Series(testdf['compliance'])

#print(testdf)

fpr, tpr, _ = roc_curve(y_test, y_score)
roc_auc = auc(fpr, tpr)
print(roc_auc)

#print(knn.score(X_train, y_train))
#print(knn.score(X_test, y_test))

#linreg = LinearRegression().fit(X_train, y_train)
#linear_test = linreg.score(X_test, y_test)

#X_train_scaled = scaler.fit_transform(X_train)
#X_test_scaled = scaler.fit_transform(X_test)
#clf = SVC(probability=True,gamma = 0.001).fit(X_train_scaled, y_train)
#print(clf.score(X_train_scaled, y_train))
#print(clf.score(X_test_scaled, y_test))
#y_score = clf.decision_function(X_test_scaled)