from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
import pickle
import pandas as pd
from sklearn.datasets import load_iris
import os
import hashlib

def generate_short_md5_hash():
    # Generate a random sequence of bytes
    random_bytes = os.urandom(16)  # Generate 16 random bytes
    
    # Create a hash object using MD5
    hash_object = hashlib.md5()
    
    # Update the hash object with the random bytes
    hash_object.update(random_bytes)
    
    # Get the hexadecimal representation of the hash
    short_hash = hash_object.hexdigest()
    
    return short_hash


# Function that trains a RandomForestClassifier model on the 'iris' dataset, saves it as a pickle file and returns the training set and the model path
def create_iris_model():
    model_path = "iris_model.pkl"
    # Load dataset
    iris = load_iris()
    train_set = pd.DataFrame(
        iris["data"],
        columns=["sepal_length_cm", "sepal_width_cm", "petal_length_cm", "petal_width_cm"],
    )

    # Separate features and target variables
    X = iris.data
    y = iris.target

    # Split the data into training and test sets
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    # Create and train the Random Forest Classifier
    model = RandomForestClassifier(n_estimators=100, random_state=42)
    model.fit(X_train, y_train)

    # Save the trained model as pkl file
    with open(model_path, "wb") as f:
        pickle.dump(model, f)
        
    return train_set, model_path



# Function that gets the number of models to log, trains and saves a model on the 'iris' dataset and logs n models of it.
def log_n_models(context, number_of_models):
    # Train an iris model
    train_set, model_path = create_iris_model()
    
    for num in range(number_of_models):      
        # Log the model and give it a random hash suffix
        model_name = f"model_num_{generate_short_md5_hash()}"
        context.log_model(model_name, model_file=model_path, training_set=train_set, framework="sklearn")