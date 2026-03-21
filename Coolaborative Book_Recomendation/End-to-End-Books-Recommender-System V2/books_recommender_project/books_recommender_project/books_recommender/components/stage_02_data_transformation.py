import os
import sys
import pickle
import pandas as pd
from books_recommender.logger.log import logging
from books_recommender.config.configuration import AppConfiguration
from books_recommender.exception.exception_handler import AppException


class DataTransformation:
    def __init__(self, app_config=AppConfiguration()):
        try:
            self.data_transformation_config = app_config.get_data_transformation_config()
            self.data_validation_config = app_config.get_data_validation_config()
        except Exception as e:
            raise AppException(e, sys) from e

    def get_data_transformer(self):
        try:
            df = pd.read_csv(self.data_transformation_config.clean_data_file_path)

            # Create pivot table: rows=books, cols=users, values=ratings
            book_pivot = df.pivot_table(columns='user_id', index='title', values='rating')
            book_pivot.fillna(0, inplace=True)
            logging.info(f"Book pivot table shape: {book_pivot.shape}")
            print(f"📊 Pivot table shape: {book_pivot.shape}")

            # Save transformed data
            os.makedirs(self.data_transformation_config.transformed_data_dir, exist_ok=True)
            t_path = os.path.join(self.data_transformation_config.transformed_data_dir, 'transformed_data.pkl')
            pickle.dump(book_pivot, open(t_path, 'wb'))
            logging.info(f"Saved transformed_data.pkl to {t_path}")

            # Save serialized objects for recommendation engine
            ser_dir = self.data_validation_config.serialized_objects_dir
            os.makedirs(ser_dir, exist_ok=True)

            book_names = book_pivot.index
            pickle.dump(book_names, open(os.path.join(ser_dir, 'book_names.pkl'), 'wb'))
            pickle.dump(book_pivot,  open(os.path.join(ser_dir, 'book_pivot.pkl'),  'wb'))
            logging.info(f"Saved book_names.pkl and book_pivot.pkl to {ser_dir}")
            print(f"✅ Serialized objects saved to: {ser_dir}")

        except Exception as e:
            raise AppException(e, sys) from e

    def initiate_data_transformation(self):
        try:
            logging.info(f"{'=' * 20}Data Transformation log started.{'=' * 20} ")
            self.get_data_transformer()
            logging.info(f"{'=' * 20}Data Transformation log completed.{'=' * 20} \n\n")
        except Exception as e:
            raise AppException(e, sys) from e
