

import mlrun
import time
import pandas as pd
import numpy as np

def func(context):
    for i in range(20):
        context.logger.info(str(i)*100)
        
    return 1

# 10 sec function
def func_sec(context):
    time.sleep(10)
    for i in range(20):
        context.logger.info(str(i)*100)
        
    # Define the size of the sample DataFrame
    num_rows = 10
    num_columns = 5

    # Generate random data
    data = np.random.rand(num_rows, num_columns)

    # Create column names
    columns = ['Column 1', 'Column 2', 'Column 3', 'Column 4', 'Column 5']

    # Create the DataFrame
    df = pd.DataFrame(data, columns=columns)
    context.log_dataset("mydf", df)
        
    return 1

# 10 min function
def func_min(context):
    time.sleep(600)
    for i in range(20):
        context.logger.info(str(i)*100)
        
    return 1

# 1 hour function
def func_hour(context):
    time.sleep(3600)
    for i in range(20):
        context.logger.info(str(i)*100)
        
    return 1
