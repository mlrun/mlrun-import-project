import mlrun 
import random

def deploy_serving_functions(context, number_of_servings, number_of_models):
    project = context.get_project_object()
    
    # Get a list of the logged models
    models = project.list_models()
    
    # Create servings
    for serving_num in range(number_of_servings):
        serving_fn = project.set_function("hub://v2_model_server", f"serving-func{str(serving_num)}", kind="serving", image="mlrun/mlrun")
        serving_fn.set_config("spec.readinessTimeoutSeconds", 1200)

        # Add the models to the serving function's routing spec
        for model_num in range(number_of_models):
            
            # Get a random model from the logged models and add it to the serving
            random_model = models[random.randint(0, len(models) -1 )]
            serving_fn.add_model(key=random_model.key, model_path=random_model.uri)

        # Enable model monitoring
        serving_fn.set_tracking()
        serving_fn.deploy()
