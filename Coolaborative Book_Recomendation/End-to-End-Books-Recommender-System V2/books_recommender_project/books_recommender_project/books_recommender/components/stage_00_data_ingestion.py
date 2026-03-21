import os
import sys
import shutil
import zipfile
from urllib import request as urllib_request
from books_recommender.logger.log import logging
from books_recommender.exception.exception_handler import AppException
from books_recommender.config.configuration import AppConfiguration


# ─────────────────────────────────────────────────────────────────────────────
# Paths to your locally uploaded CSV files in Colab
# Adjust these paths if you uploaded the files elsewhere
# ─────────────────────────────────────────────────────────────────────────────
LOCAL_RATINGS_CSV  = "/content/BX-Book-Ratings.csv"   # uploaded via Colab UI
LOCAL_USERS_CSV    = "/content/BX-Users.csv"           # uploaded via Colab UI
LOCAL_BOOKS_CSV    = "/content/BX-Books.csv"           # saved locally in Colab


class DataIngestion:
    def __init__(self, app_config=AppConfiguration()):
        try:
            logging.info(f"{'=' * 20}Data Ingestion log started.{'=' * 20} ")
            self.data_ingestion_config = app_config.get_data_ingestion_config()
            self.data_validation_config = app_config.get_data_validation_config()
        except Exception as e:
            raise AppException(e, sys) from e

    def ingest_local_data(self):
        """
        Copies locally uploaded CSVs (BX-Books, BX-Book-Ratings, BX-Users)
        into the ingested_data directory so the rest of the pipeline can find them.
        """
        try:
            ingested_dir = self.data_ingestion_config.ingested_dir
            os.makedirs(ingested_dir, exist_ok=True)

            files_to_copy = [
                (LOCAL_BOOKS_CSV,   "BX-Books.csv"),
                (LOCAL_RATINGS_CSV, "BX-Book-Ratings.csv"),
                (LOCAL_USERS_CSV,   "BX-Users.csv"),
            ]

            for src, dest_name in files_to_copy:
                dest = os.path.join(ingested_dir, dest_name)
                if os.path.exists(src):
                    shutil.copy2(src, dest)
                    logging.info(f"Copied {src} -> {dest}")
                else:
                    logging.warning(f"File not found, skipping: {src}")
                    print(f"⚠️  WARNING: {src} not found. Please upload it to Colab.")

            logging.info(f"All local data files copied to {ingested_dir}")
        except Exception as e:
            raise AppException(e, sys) from e

    def initiate_data_ingestion(self):
        try:
            self.ingest_local_data()
            logging.info(f"{'=' * 20}Data Ingestion log completed.{'=' * 20} \n\n")
        except Exception as e:
            raise AppException(e, sys) from e
