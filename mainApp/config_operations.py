import os
import json
import shutil
import datetime
import sys

from mainApp import app, logger


def get_config_dir():
    config_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'userFiles', 'config'))
    os.makedirs(config_dir, exist_ok=True)
    return config_dir


def get_event_config_path():
    return os.path.join(get_config_dir(), 'events.json')


def get_event_config_backup_path():
    timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
    return os.path.join(get_config_dir(), f'events_{timestamp}.json')


def load_event_config():
    path = get_event_config_path()
    if not os.path.exists(path):
        save_event_config(json.dumps([], indent=2))
    with open(path, 'r', encoding='utf-8') as config_file:
        return config_file.read()


def validate_event_config_text(text):
    try:
        config = json.loads(text)
    except json.JSONDecodeError as json_error:
        raise ValueError(f'Niepoprawny JSON: {json_error}')
    return validate_event_config_object(config)


def validate_event_config_object(config):
    if not isinstance(config, list):
        raise ValueError('Konfiguracja eventów musi być listą obiektów.')

    for index, event in enumerate(config, start=1):
        if not isinstance(event, dict):
            raise ValueError(f'Event #{index} musi być obiektem JSON.')

        required_keys = ['eventAddress', 'eventPayload', 'eventStatus']
        for key in required_keys:
            if key not in event:
                raise ValueError(f'Event #{index}: brak pola {key}.')

        status = event.get('eventStatus')
        if status not in ['Ready', 'Not Ready']:
            raise ValueError(f'Event #{index}: eventStatus musi być "Ready" lub "Not Ready".')

        group_id = event.get('eventGroupId')
        if group_id is not None and not isinstance(group_id, int):
            raise ValueError(f'Event #{index}: eventGroupId musi być liczbą całkowitą lub null.')

    return config


def backup_event_config():
    path = get_event_config_path()
    if os.path.exists(path):
        backup_path = get_event_config_backup_path()
        shutil.copy2(path, backup_path)
        logger.info(f'Backup konfiguracji eventów zapisano w: {backup_path}')
        return backup_path
    return None


def save_event_config(text):
    path = get_event_config_path()
    with open(path, 'w', encoding='utf-8') as config_file:
        config_file.write(text)
    logger.info(f'Konfiguracja eventów zapisana w: {path}')
    return path


def restart_application():
    logger.warning('Restart aplikacji w celu załadowania nowej konfiguracji.')
    executable = sys.executable
    args = [executable] + sys.argv
    os.execv(executable, args)
