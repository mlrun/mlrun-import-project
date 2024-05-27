import time
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from mlrun.artifacts import (
    PlotlyArtifact,
)


# 10 sec sleep function
def func_sec(context):
    time.sleep(10)
    for i in range(20):
        context.logger.info(str(i)*100)
        
    return 1

# 10 min sleep function
def func_min(context):
    time.sleep(600)
    for i in range(20):
        context.logger.info(str(i)*100)
        
    return 1

# 1 hours sleep function
def func_hour(context):
    time.sleep(3600)
    for i in range(20):
        context.logger.info(str(i)*100)
        
    return 1



# artifact logging function
def func_artifact(context):
    for i in range(20):
        context.logger.info(str(i)*100)
    # Define the data for the graph
    x_data = ['Category 1', 'Category 2', 'Category 3', 'Category 4', 'Category 5']
    y_data = [25, 40, 30, 10, 20]

    # Create a bar graph
    fig = go.Figure(data=go.Bar(x=x_data, y=y_data))

    # Customize the bar colors
    colors = ['#FFA500', '#FF4500', '#FFD700', '#FF6347', '#FF8C00']
    fig.update_traces(marker_color=colors, marker_line_color='rgb(0,0,0)', marker_line_width=1)

    # Set the axis labels and title
    fig.update_layout(
        xaxis_title='Categories',
        yaxis_title='Values',
        title='Sample Bar Graph'
    )

    context.log_artifact(PlotlyArtifact(key="plot", figure=fig))
    return 1

# dataset logging function
def func_dataset(context, num_rows, num_columns):
    # Generate random data
    data = np.random.rand(num_rows, num_columns)

    # Create column names
    columns = [f'Column_{str(i)}' for i in range(num_columns)]

    # Create the DataFrame
    df = pd.DataFrame(data, columns=columns)
    
     # Create the DataFrame and give it a name with a random int suffix
    df = pd.DataFrame(data, columns=columns)
    context.log_dataset(f"mydf_{str(random.randint(0,num_rows))}", df)
    return 1
                 
 