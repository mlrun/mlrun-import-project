import os
import mlrun
from sklearn.datasets import load_iris
import pandas as pd

def setup(
    project: mlrun.projects.MlrunProject,
) -> mlrun.projects.MlrunProject:
    """
    Creating the project for the demo. This function is expected to call automatically when calling the function
    `mlrun.get_or_create_project`.

    :param project: The project to set up.

    :returns: A fully prepared project for this demo.
    """
   
    
    
    # Set the job functions:
    run_job_functions(project=project)
    run_spark_function(project=project)
    run_dask_function(project=project)
    deploy_nuclio_functions(project=project)
    deploy_serving_functions(number_of_servings=, number_of_models=, project=project)
    run_pipelines(number_of_pipelines=,project=project)
    
    
#     # Set custom artifact path
#     project.artifact_path = os.environ["ARTIFACT_PATH"]

#     # Set the workflows:
#     project.set_workflow(name="main", workflow_path="./.mlrun/workflow.py")

#     # Set the project git source:
#     source = os.environ["MLRUN_SOURCE"]
#     if source:
#         project.set_source(source=source, pull_at_runtime=True, workdir=workdir)

#     # Run extra configurations defined in the 'project_setup_extras.py' file
#     project, build_commands = run_extras(project, project.get_param("run_build"))

#     # Build the handler function
#     if project.get_param("run_build"):
#         project.build_function(handlers_fn, commands=build_commands, overwrite_build_params=True)

#     # Save and return the project:
#     project.save()
    return project

def _set_secrets(project: mlrun.projects.MlrunProject):

    # Set the secrets:
    project.set_secrets(file_path=project.get_param("env-file"))
    


def run_job_functions(project: mlrun.projects.MlrunProject):
    normal_job_sec = project.set_function(func="jobs_func.py", name="normal_job_sec", handler='func_sec', image="mlrun/mlrun", kind="job")
    normal_job_min = project.set_function(func="jobs_func.py", name="normal_job_min", handler='func_min', image="mlrun/mlrun", kind="job")
    normal_job_hour = project.set_function(func="jobs_func.py", name="normal_job_hour", handler='func_hour', image="mlrun/mlrun", kind="job")
    
    for i in range(3):
        job_num = str(i)
        project.run_function("normal_job_sec", name=f"sched_job_sec_30m_{job_num}", schedule="30 * * * *", watch=False)
        project.run_function("normal_job_min", name=f"sched_job_min_30m_{job_num}", schedule="30 * * * *", watch=False)
        project.run_function("normal_job_hour", name=f"sched_job_hour_30m_{job_num}", schedule="30 * * * *", watch=False)

        project.run_function("normal_job_sec", name=f"sched_job_sec_1h_{job_num}", schedule="0 * * * *", watch=False)
        project.run_function("normal_job_min", name=f"sched_job_min_1h_{job_num}", schedule="0 * * * *", watch=False)
        project.run_function("normal_job_hour", name=f"sched_job_hour_1h_{job_num}", schedule="0 * * * *", watch=False)

        project.run_function("normal_job_sec", name=f"sched_job_sec_4h_{job_num}", schedule="0 */4 * * *", watch=False)
        project.run_function("normal_job_min", name=f"sched_job_min_4h_{job_num}", schedule="0 */4 * * *", watch=False)
        project.run_function("normal_job_hour", name=f"sched_job_hour_4h_{job_num}", schedule="0 */4 * * *", watch=False)

        project.run_function("normal_job_sec", name=f"sched_job_sec_3d_{job_num}", schedule="0 0 */3 * *", watch=False)
        project.run_function("normal_job_min", name=f"sched_job_min_3d_{job_num}", schedule="0 0 */3 * *", watch=False)
        project.run_function("normal_job_hour", name=f"sched_job_hour_3d_{job_num}", schedule="0 0 */3 * *", watch=False)
    
def run_spark_function(project: mlrun.projects.MlrunProject):
    spark_func = mlrun.code_to_function(name="spark-read",
                                    kind="spark",
                                    handler="spark_handler",
                                    filename="spark_jobs_func.py",image='mlrun/mlrun'
                                   ).apply(mlrun.auto_mount())
    spark_func.with_executor_requests(cpu="1",mem="1G")
    spark_func.with_driver_requests(cpu="1",mem="1G")
    spark_func.with_driver_limits(cpu="1")
    spark_func.with_executor_limits(cpu="1")
    spark_func.with_igz_spark()
    spark_func.spec.image_pull_policy = "Always"
    spark_func.spec.replicas = 2
    spark_func.deploy()
    spark_func.run()
    
    
def run_dask_function(project: mlrun.projects.MlrunProject):
    func = project.set_function(func='./dask_jobs_func.py',name='dask_func',image='mlrun/mlrun',kind='job',handler='train')
    dask_cluster = mlrun.new_function("dask-cluster", kind='dask', image='mlrun/mlrun')
    dask_cluster.apply(mlrun.mount_v3io())        # add volume mounts
    dask_cluster.spec.service_type = "NodePort"   # open interface to the dask UI dashboard
    dask_cluster.spec.replicas = 1             # define one container
    dask_cluster.set_env("MLRUN_DBPATH",os.environ["MLRUN_DBPATH"])
    dask_cluster.set_env("MLRUN_DEFAULT_PROJECT",project.name)
    uri = dask_cluster.save()
    
    dask_cluster.deploy()
    project.run_function('dask_func',hyperparams={"i":[1,10,20,30,40]},hyper_param_options={"strategy":"list","parallel_runs":1,"dask_cluster_uri":uri,"teardown_dask":True})
    
    
    
def deploy_nuclio_functions(project: mlrun.projects.MlrunProject):
    project.set_function("nuclio_func.py", name="nuclio_func", handler="handler", image="mlrun/mlrun", kind="nuclio")
    for i in range(15):
        job_num = str(i)
        # Create a simple nuclio function
        project.deploy_function("nuclio_func", tag=job_num)
        

        
        
        
# Function that gets the number of models to log, trains and saves a model on the 'iris' dataset and logs n models of it.
def log_n_models(context, number_of_models):
    train_set, model_path = create_iris_model()
    for num in number_of_models:      
        # Log the model
        model_name = f"model_num_{str(num)}"
        context.log_model(model_name, model_file=model_path, training_set=train_set, framework="sklearn")
        
        
def deploy_serving_functions(number_of_servings, number_of_models, project: mlrun.projects.MlrunProject):
    for serving_num in number_of_servings:
        serving_fn = project.set_function("hub://v2_model_server", f"serving-func{str(serving_num)}", kind="serving", image="mlrun/mlrun")
        serving_fn.apply(mlrun.auto_mount())

        # Add the models to the serving function's routing spec
        for model_num in number_of_models:
            model_name = f"model_num_{str(model_num)}"
            serving_fn.add_model(model_name=model_name, model_path=f"store://models/{project.name}/{model_name}:latest")

        # (OPTIONAL) Create a tracking policy 
        # tracking_policy = {'default_batch_intervals':"*/1 * * * *", "default_batch_image":"mlrun/mlrun:1.6.0-rc15", "stream_image":"mlrun/mlrun:1.6.0-rc15", "default_controller_image":"mlrun/mlrun:1.6.0-rc15"}

        # Enable model monitoring (If you specified tracking_policy, pass it to 'tracking_policy' param)
        serving_fn.set_tracking()
        
        serving_fn.deploy_function()

        
        
def run_pipelines(number_of_pipelines, project: mlrun.projects.MlrunProject):
    project.set_workflow(name='workflow-func', workflow_path="workflow.py")

    project.run(name='workflow-func',watch=False, schedule = "0 * * * *")
        
