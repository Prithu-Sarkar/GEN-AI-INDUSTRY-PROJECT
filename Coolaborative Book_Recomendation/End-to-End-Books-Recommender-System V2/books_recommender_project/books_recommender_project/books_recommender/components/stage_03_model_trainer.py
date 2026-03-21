import os
import sys
import pickle
import mlflow
import mlflow.sklearn
from sklearn.neighbors import NearestNeighbors
from scipy.sparse import csr_matrix
from books_recommender.logger.log import logging
from books_recommender.config.configuration import AppConfiguration
from books_recommender.exception.exception_handler import AppException


class ModelTrainer:
    def __init__(self, app_config=AppConfiguration()):
        try:
            self.model_trainer_config = app_config.get_model_trainer_config()
        except Exception as e:
            raise AppException(e, sys) from e

    def train(self):
        try:
            # Load pivot data
            book_pivot = pickle.load(open(self.model_trainer_config.transformed_data_file_dir, 'rb'))
            book_sparse = csr_matrix(book_pivot)

            algorithm = 'brute'
            metric = 'cosine'
            n_neighbors = 6

            # ── MLflow run ────────────────────────────────────────────────────
            mlflow.set_tracking_uri(os.environ.get('MLFLOW_TRACKING_URI', './mlruns'))
            mlflow.set_experiment('books_recommender')

            with mlflow.start_run(run_name='KNN_Collaborative_Filter'):
                model = NearestNeighbors(algorithm=algorithm, metric=metric, n_neighbors=n_neighbors)
                model.fit(book_sparse)

                # Log params
                mlflow.log_param('algorithm',   algorithm)
                mlflow.log_param('metric',      metric)
                mlflow.log_param('n_neighbors', n_neighbors)
                mlflow.log_param('pivot_shape', str(book_pivot.shape))

                # Log metrics
                mlflow.log_metric('n_books', book_pivot.shape[0])
                mlflow.log_metric('n_users', book_pivot.shape[1])

                # Log model
                mlflow.sklearn.log_model(model, artifact_path='knn_model')
                logging.info(f"MLflow run logged successfully.")
                print(f"✅ MLflow run logged. Tracking URI: {mlflow.get_tracking_uri()}")

            # Save model locally
            os.makedirs(self.model_trainer_config.trained_model_dir, exist_ok=True)
            file_name = os.path.join(
                self.model_trainer_config.trained_model_dir,
                self.model_trainer_config.trained_model_name
            )
            pickle.dump(model, open(file_name, 'wb'))
            logging.info(f"Saved model to {file_name}")
            print(f"✅ Model saved to: {file_name}")

        except Exception as e:
            raise AppException(e, sys) from e

    def initiate_model_trainer(self):
        try:
            logging.info(f"{'=' * 20}Model Trainer log started.{'=' * 20} ")
            self.train()
            logging.info(f"{'=' * 20}Model Trainer log completed.{'=' * 20} \n\n")
        except Exception as e:
            raise AppException(e, sys) from e
