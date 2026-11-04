import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))


class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY", "dev-secret-key-change-in-production")

    # Default: local SQLite file so the project runs out of the box with no
    # external database server. To use MySQL (as specified in the project
    # proposal), install PyMySQL (already in requirements.txt) and set:
    #
    #   SQLALCHEMY_DATABASE_URI = (
    #       "mysql+pymysql://<user>:<password>@<host>:3306/<db_name>"
    #   )
    #
    # e.g. "mysql+pymysql://root:password@localhost:3306/job_matching_db"
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        "DATABASE_URL", f"sqlite:///{os.path.join(BASE_DIR, 'instance', 'app.db')}"
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    MODEL_DIR = os.path.join(BASE_DIR, "ml", "saved_models")


class DevelopmentConfig(Config):
    """Local development configuration"""
    DEBUG = True
    FLASK_ENV = "development"


class ProductionConfig(Config):
    """Production configuration for online hosting"""
    DEBUG = False
    FLASK_ENV = "production"
    # SECRET_KEY will use the default from Config if not set in environment


# Configuration dictionary
config = {
    "development": DevelopmentConfig,
    "production": ProductionConfig,
    "default": DevelopmentConfig
}


def get_config(env=None):
    """Get configuration based on environment"""
    if env is None:
        env = os.environ.get("FLASK_ENV", "development")
    return config.get(env, DevelopmentConfig)
