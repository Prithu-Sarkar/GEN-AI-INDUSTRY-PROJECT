# ── Deployment-free version: S3 sync removed ─────────────────────────────────
import os, sys
from networksecurity.exception.exception import NetworkSecurityException
from networksecurity.logging.logger import logging
from networksecurity.components.data_ingestion import DataIngestion
from networksecurity.components.data_validation import DataValidation
from networksecurity.components.data_transformation import DataTransformation
from networksecurity.components.model_trainer import ModelTrainer
from networksecurity.entity.config_entity import (
    TrainingPipelineConfig, DataIngestionConfig, DataValidationConfig,
    DataTransformationConfig, ModelTrainerConfig,
)
from networksecurity.entity.artifact_entity import (
    DataIngestionArtifact, DataValidationArtifact,
    DataTransformationArtifact, ModelTrainerArtifact,
)

class TrainingPipeline:
    def __init__(self):
        self.training_pipeline_config = TrainingPipelineConfig()

    def start_data_ingestion(self) -> DataIngestionArtifact:
        try:
            config = DataIngestionConfig(training_pipeline_config=self.training_pipeline_config)
            logging.info('Starting Data Ingestion')
            artifact = DataIngestion(data_ingestion_config=config).initiate_data_ingestion()
            logging.info(f'Data Ingestion complete: {artifact}')
            return artifact
        except Exception as e:
            raise NetworkSecurityException(e, sys)

    def start_data_validation(self, data_ingestion_artifact: DataIngestionArtifact) -> DataValidationArtifact:
        try:
            config = DataValidationConfig(training_pipeline_config=self.training_pipeline_config)
            logging.info('Starting Data Validation')
            artifact = DataValidation(
                data_ingestion_artifact=data_ingestion_artifact,
                data_validation_config=config
            ).initiate_data_validation()
            logging.info(f'Data Validation complete: {artifact}')
            return artifact
        except Exception as e:
            raise NetworkSecurityException(e, sys)

    def start_data_transformation(self, data_validation_artifact: DataValidationArtifact) -> DataTransformationArtifact:
        try:
            config = DataTransformationConfig(training_pipeline_config=self.training_pipeline_config)
            logging.info('Starting Data Transformation')
            artifact = DataTransformation(
                data_validation_artifact=data_validation_artifact,
                data_transformation_config=config
            ).initiate_data_transformation()
            logging.info(f'Data Transformation complete: {artifact}')
            return artifact
        except Exception as e:
            raise NetworkSecurityException(e, sys)

    def start_model_trainer(self, data_transformation_artifact: DataTransformationArtifact) -> ModelTrainerArtifact:
        try:
            config = ModelTrainerConfig(training_pipeline_config=self.training_pipeline_config)
            logging.info('Starting Model Training')
            artifact = ModelTrainer(
                model_trainer_config=config,
                data_transformation_artifact=data_transformation_artifact
            ).initiate_model_trainer()
            logging.info(f'Model Training complete: {artifact}')
            return artifact
        except Exception as e:
            raise NetworkSecurityException(e, sys)

    def run_pipeline(self) -> ModelTrainerArtifact:
        try:
            ingestion_artifact      = self.start_data_ingestion()
            validation_artifact     = self.start_data_validation(ingestion_artifact)
            transformation_artifact = self.start_data_transformation(validation_artifact)
            model_artifact          = self.start_model_trainer(transformation_artifact)
            return model_artifact
        except Exception as e:
            raise NetworkSecurityException(e, sys)
