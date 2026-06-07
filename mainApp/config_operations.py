import os
import json
import shutil
import datetime

from mainApp import logger


def get_config_file_path(file_name):
    config_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'userFiles', 'config'))
    os.makedirs(config_dir, exist_ok=True)
    return os.path.join(config_dir, file_name)


def get_config_backup_file_path(file_name):
    backup_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'userFiles', 'config', 'backup'))
    os.makedirs(backup_dir, exist_ok=True)
    name, ext = os.path.splitext(file_name)
    timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
    return os.path.join(backup_dir, f'{name}_{timestamp}{ext}')


def load_config_json(file_name):
    path = get_config_file_path(file_name)
    with open(path, 'r', encoding='utf-8') as config_file:
        return json.load(config_file)


def load_config_text(file_name):
    path = get_config_file_path(file_name)
    if not os.path.exists(path):
        save_config_text(file_name, '[]')
    with open(path, 'r', encoding='utf-8') as config_file:
        return config_file.read()


def save_config_text(file_name, text):
    path = get_config_file_path(file_name)
    with open(path, 'w', encoding='utf-8') as config_file:
        config_file.write(text)
    logger.info(f'Konfiguracja zapisana w: {path}')
    return path


def backup_config_file(file_name):
    path = get_config_file_path(file_name)
    if os.path.exists(path):
        backup_path = get_config_backup_file_path(file_name)
        shutil.copy2(path, backup_path)
        logger.info(f'Backup konfiguracji zapisano w: {backup_path}')
        return backup_path
    return None


def parse_config_text(text):
    try:
        return json.loads(text)
    except json.JSONDecodeError as json_error:
        raise ValueError(f'Niepoprawny JSON: {json_error}')


def restart_application():
    logger.warning('kiedyś reastart aplikacji albo konfiguracji.')
