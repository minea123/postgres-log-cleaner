import logging
from logging.handlers import RotatingFileHandler

# Set up logging
logger = logging.getLogger('python_logger')
logger.setLevel(logging.DEBUG)  # Set the logging level (e.g., DEBUG, INFO, etc.)

# Set up the rotating file handler
file_handler = RotatingFileHandler('logs/python.out', maxBytes=5 * 1024 * 1024, backupCount=3)  # 5 MB max size, 3 backup files
file_formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
file_handler.setFormatter(file_formatter)

# Set up the console handler
console_handler = logging.StreamHandler()
console_formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
console_handler.setFormatter(console_formatter)

# Add the handlers to the logger
logger.addHandler(file_handler)
logger.addHandler(console_handler)
