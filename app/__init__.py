from flask import Flask
from flask_pymongo import PyMongo
from dotenv import load_dotenv
import logging
import os

load_dotenv()


mongo = PyMongo()
def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = os.urandom(24)
    app.config['MONGO_URI'] ='mongodb+srv://sabitha:sabitha@elearning.irf72.mongodb.net/emanagement?retryWrites=true&w=majority&appName=elearning'
    # Set up logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s %(levelname)s %(message)s',
        handlers=[
            logging.FileHandler("app.log"),  # Logs to file
            logging.StreamHandler()         # Logs to console
        ]
    )
    logger = logging.getLogger()
    # Test DB Connection
    try:
        mongo.init_app(app)
        with app.app_context():
            # Perform a ping to check the connection
            mongo.db.command('ping')
            logger.info("Database connection successful.")
    except Exception as e:
        logger.error(f"Failed to connect to the database: {e}")
        raise


    # Register Blueprints
    from app.routes import main
    app.register_blueprint(main)

    return app