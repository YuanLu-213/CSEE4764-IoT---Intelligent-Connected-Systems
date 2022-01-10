from sklearn import svm
from sklearn.preprocessing import StandardScaler
from joblib import dump
from sklearn.ensemble import RandomForestClassifier
from pymongo import MongoClient
from sklearn.pipeline import make_pipeline
from sklearn.model_selection import train_test_split

client = MongoClient('') #创建mongoclient链接运行的mongo， 加mongodb URI
db = client.list_database_names()
la6_db = client[""]#连接database，加database名字
    
lab6_data = db[""]#找collection，加collection名字

clf = make_pipeline(StandardScaler(), svm.SVC(kernel='linear'))
round = 1 
data = []
train_data = []
labels = []

while (round <= 20):

    all_samples = .find({'round': round})

    for sample in all_samples:
        
        label = sample["label"]
        samples = sample["sample"]
        
        labels.append(label)
        data.append(samples)
        train, test = train_test_split(data)
        train_data.append(train)

    round += 1
    
clf = RandomForestClassifier(n_estimators = 100)
clf.fit(train_data, labels)
dump(clf, 'gesture.joblib')






