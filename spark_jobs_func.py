
# Import necessary libraries
from pyspark.sql import SparkSession
from sklearn.datasets import load_iris



import mlrun
@mlrun.handler(outputs=['df'])
def spark_handler():
# Create a SparkSession
    spark = SparkSession.builder \
        .appName("SparkQueryExample") \
        .getOrCreate()

    df = load_iris(as_frame=True)
    df = df.frame
    
#     # Read data from a CSV file into a DataFrame
#     data = spark.read.csv("iris.csv", header=True, inferSchema=True)

#     # Perform a simple query
#     df = data.toPandas()
    return df
