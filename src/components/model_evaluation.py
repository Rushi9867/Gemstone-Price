import os
import sys
import pickle 
import mlflow
import numpy as np
import mlflow.sklearn
from urllib.parse import urlparse
from src.logger.logging import logging
from src.utils.utils import load_object
from src.exception.exception import customexception
from sklearn.metrics import mean_squared_error,mean_absolute_error,r2_score

class ModelEvaluation:
    def __init__(self):
        logging.info("Evaluation Started")

    def eval_metrics(self,actual,pred):
        rmse = np.sqrt(mean_squared_error(actual,pred))
        mae  = mean_absolute_error(actual,pred)
        r2   = r2_score(actual,pred)
        logging.info('evaluation metrics captured')
        return rmse,mae,r2

    def initiate_model_evaluation(self,train_array,test_array):
        try:
            X_test,y_test = (test_array[:,:-1],test_array[:,-1])
            model_path = os.path.join("artifacts","model.pkl")
            model = load_object(model_path)

            ## For Remote Server Only (DAGSHUB)
            remote_server_uri = "https://dagshub.com/Rushi9867/Diamond_Price_Prediction.mlflow"
            mlflow.set_tracking_uri(remote_server_uri)
            logging.info("Model has register")
            tracking_url_type_store = urlparse(mlflow.get_tracking_uri()).scheme
            print(tracking_url_type_store)

            with mlflow.start_run():
                prediction = model.predict(X_test)
                (rmse,mae,r2) = self.eval_metrics(y_test,prediction)
                mlflow.log_metric("RMSE",rmse)
                mlflow.log_metric("MAE",mae)
                mlflow.log_metric("R2",r2)

                 # Model registry does not work with file store
                if tracking_url_type_store != "file":

                    # Register the model
                    # There are other ways to use the Model Registry, which depends on the use case,
                    # please refer to the doc for more information:
                    # https://mlflow.org/docs/latest/model-registry.html#api-workflow
                    mlflow.sklearn.log_model(model, "model", registered_model_name="ml_model")
                else:
                    mlflow.sklearn.log_model(model, "model")

        except Exception as e:
            raise customexception(e,sys)
