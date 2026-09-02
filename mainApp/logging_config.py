import logging
import os

def setup_logging():
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.DEBUG)

    # formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')

    # add heandler for file
    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'userFiles'))
    os.makedirs(base_dir, exist_ok=True)
    log_path = os.path.join(base_dir, 'app.log')
    
    file_handler = logging.FileHandler(log_path, encoding='utf-8')
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(formatter)

    # add heandler for console
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.DEBUG)
    console_handler.setFormatter(formatter)

    # add heandlers to logger
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)

    return logger