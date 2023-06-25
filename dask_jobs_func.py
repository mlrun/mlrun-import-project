import numpy as np
from mlrun.frameworks.sklearn import apply_mlrun
from sklearn.datasets import make_classification
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score
def train(context,i):
    # Create dummy feature matrix and target variable
    X,y = make_classification(random_state=1,)

    # Split the data into training and test sets
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    # Create a Random Forest classifier
    clf = RandomForestClassifier()
    apply_mlrun(model=clf,x_test=X_test,y_test=y_test,context=context,model_name=f'model_{i}')
    # Train the model
    clf.fit(X_train, y_train)

