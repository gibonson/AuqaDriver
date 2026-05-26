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

def get_config_backup_dir():
    config_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'userFiles', 'config', 'backup'))
    os.makedirs(config_dir, exist_ok=True)
    return config_dir

def get_event_config_path():
    return os.path.join(get_config_dir(), 'events.json')


def get_event_config_backup_path():
    timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
    return os.path.join(get_config_backup_dir(), f'events_{timestamp}.json')


def get_scheduler_config_path():
    return os.path.join(get_config_dir(), 'events_scheduler.json')


def get_scheduler_config_backup_path():
    timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
    return os.path.join(get_config_backup_dir(), f'events_scheduler_{timestamp}.json')


def get_report_config_path():
    return os.path.join(get_config_dir(), 'archive_reports.json')


def get_report_config_backup_path():
    timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
    return os.path.join(get_config_backup_dir(), f'archive_reports_{timestamp}.json')


def load_event_config():
    path = get_event_config_path()
    if not os.path.exists(path):
        save_event_config(json.dumps([], indent=2))
    with open(path, 'r', encoding='utf-8') as config_file:
        return config_file.read()


def load_scheduler_config():
    path = get_scheduler_config_path()
    if not os.path.exists(path):
        save_scheduler_config(json.dumps([], indent=2))
    with open(path, 'r', encoding='utf-8') as config_file:
        return config_file.read()


def load_report_config():
    path = get_report_config_path()
    if not os.path.exists(path):
        save_report_config(json.dumps([], indent=2))
    with open(path, 'r', encoding='utf-8') as config_file:
        return config_file.read()


def parse_config_text(text):
    try:
        return json.loads(text)
    except json.JSONDecodeError as json_error:
        raise ValueError(f'Niepoprawny JSON: {json_error}')


def validate_event_config_text(text):
    config = parse_config_text(text)
    return validate_event_config_object(config)


def validate_event_config_object(config):
    if not isinstance(config, list):
        raise ValueError('Konfiguracja eventów musi być listą obiektów.')

    seen_names = set()
    for index, event in enumerate(config, start=1):
        if not isinstance(event, dict):
            raise ValueError(f'Event #{index} musi być obiektem JSON.')

        required_keys = ['eventAddress', 'eventPayload', 'eventStatus', 'eventName']
        for key in required_keys:
            if key not in event:
                raise ValueError(f'Event #{index}: brak pola {key}.')

        eventName = event.get('eventName')
        if not eventName:
            raise ValueError(f'Event #{index}: eventName nie może być pusty.')
        if eventName in seen_names:
            raise ValueError(f'Event #{index}: duplikat eventName "{eventName}".')
        seen_names.add(eventName)

        eventAddress = event.get('eventAddress')
        if not eventAddress:
            raise ValueError(f'Event #{index}: eventAddress nie może być pusty.')

        status = event.get('eventStatus')
        if status not in ['Ready', 'Not Ready']:
            raise ValueError(f'Event #{index}: eventStatus musi być "Ready" lub "Not Ready".')

    return config


def validate_report_config_text(text):
    config = parse_config_text(text)
    return validate_report_config_object(config)


def validate_report_config_object(config):
    if not isinstance(config, list):
        raise ValueError('Konfiguracja raportów musi być listą obiektów.')

    seen_names = set()
    for index, report in enumerate(config, start=1):
        if not isinstance(report, dict):
            raise ValueError(f'Raport #{index} musi być obiektem JSON.')

        required_keys = ['reportName', 'queryString', 'minValue', 'okMinValue', 'okMaxValue', 'maxValue', 'status']
        for key in required_keys:
            if key not in report:
                raise ValueError(f'Raport #{index}: brak pola {key}.')

        reportName = report.get('reportName')
        if not reportName:
            raise ValueError(f'Raport #{index}: reportName nie może być pusty.')
        if reportName in seen_names:
            raise ValueError(f'Raport #{index}: duplikat reportName "{reportName}".')
        seen_names.add(reportName)

        queryString = report.get('queryString')
        if not queryString:
            raise ValueError(f'Raport #{index}: queryString nie może być pusty.')

        for field_name in ['minValue', 'okMinValue', 'okMaxValue', 'maxValue']:
            value = report.get(field_name)
            if value is None:
                raise ValueError(f'Raport #{index}: brak pola {field_name}.')
            try:
                int(value)
            except (ValueError, TypeError):
                raise ValueError(f'Raport #{index}: pole {field_name} musi być liczbą.')

        status = report.get('status')
        if status not in ['Ready', 'Not Ready']:
            raise ValueError(f'Raport #{index}: status musi być "Ready" lub "Not Ready".')

    return config


def validate_scheduler_config_text(text):
    config = parse_config_text(text)
    return validate_scheduler_config_object(config)


def validate_scheduler_config_object(config):
    if not isinstance(config, list):
        raise ValueError('Konfiguracja schedulerów musi być listą obiektów.')

    seen_ids = set()
    for index, scheduler in enumerate(config, start=1):
        if not isinstance(scheduler, dict):
            raise ValueError(f'Scheduler #{index} musi być obiektem JSON.')

        required_keys = ['schedulerName', 'reportList', 'eventList', 'trigger', 'hour', 'minute', 'second', 'schedulerStatus']
        for key in required_keys:
            if key not in scheduler:
                raise ValueError(f'Scheduler #{index}: brak pola {key}.')

        schedulerName = scheduler.get('schedulerName')
        if not schedulerName:
            raise ValueError(f'Scheduler #{index}: schedulerName nie może być pusty.')
        if schedulerName in seen_ids:
            raise ValueError(f'Scheduler #{index}: duplikat schedulerName "{schedulerName}".')
        seen_ids.add(schedulerName)

        trigger = scheduler.get('trigger')
        if trigger not in ['interval', 'cron']:
            raise ValueError(f'Scheduler #{index}: trigger musi być "interval" lub "cron".')

        status = scheduler.get('schedulerStatus')
        if status not in ['Ready', 'Not Ready']:
            raise ValueError(f'Scheduler #{index}: schedulerStatus musi być "Ready" lub "Not Ready".')

        for field_name in ['hour', 'minute', 'second']:
            value = scheduler.get(field_name)
            if value is None:
                raise ValueError(f'Scheduler #{index}: brak pola {field_name}.')
            try:
                value_int = int(value)
            except (ValueError, TypeError):
                raise ValueError(f'Scheduler #{index}: pole {field_name} musi być liczbą.')
            if field_name == 'hour' and not (0 <= value_int <= 23):
                raise ValueError(f'Scheduler #{index}: hour musi być w zakresie 0-23.')
            if field_name in ['minute', 'second'] and not (0 <= value_int <= 59):
                raise ValueError(f'Scheduler #{index}: {field_name} musi być w zakresie 0-59.')

        day = scheduler.get('day')
        if day is not None and day != '' and not str(day).isdigit():
            raise ValueError(f'Scheduler #{index}: pole day musi być liczbą lub pusty.')

        day_of_week = scheduler.get('day_of_week')
        allowed_days = [None, '', 'mon', 'tue', 'wed', 'thu', 'fri', 'sat', 'sun']
        if day_of_week not in allowed_days:
            raise ValueError(f'Scheduler #{index}: day_of_week musi być jednym z {allowed_days}.')

        report_list = scheduler.get('reportList')
        if report_list is not None and not isinstance(report_list, list):
            raise ValueError(f'Scheduler #{index}: reportList musi być listą.')

        event_list = scheduler.get('eventList')
        if event_list is not None and not isinstance(event_list, list):
            raise ValueError(f'Scheduler #{index}: eventList musi być listą.')

    return config


def backup_event_config():
    path = get_event_config_path()
    if os.path.exists(path):
        backup_path = get_event_config_backup_path()
        shutil.copy2(path, backup_path)
        logger.info(f'Backup konfiguracji eventów zapisano w: {backup_path}')
        return backup_path
    return None


def backup_report_config():
    path = get_report_config_path()
    if os.path.exists(path):
        backup_path = get_report_config_backup_path()
        shutil.copy2(path, backup_path)
        logger.info(f'Backup konfiguracji raportów zapisano w: {backup_path}')
        return backup_path
    return None


def backup_scheduler_config():
    path = get_scheduler_config_path()
    if os.path.exists(path):
        backup_path = get_scheduler_config_backup_path()
        shutil.copy2(path, backup_path)
        logger.info(f'Backup konfiguracji schedulerów zapisano w: {backup_path}')
        return backup_path
    return None


def save_event_config(text):
    path = get_event_config_path()
    with open(path, 'w', encoding='utf-8') as config_file:
        config_file.write(text)
    logger.info(f'Konfiguracja eventów zapisana w: {path}')
    return path


def save_report_config(text):
    path = get_report_config_path()
    with open(path, 'w', encoding='utf-8') as config_file:
        config_file.write(text)
    logger.info(f'Konfiguracja raportów zapisana w: {path}')
    return path


def save_scheduler_config(text):
    path = get_scheduler_config_path()
    with open(path, 'w', encoding='utf-8') as config_file:
        config_file.write(text)
    logger.info(f'Konfiguracja schedulerów zapisana w: {path}')
    return path


def restart_application():
    logger.warning('kiedyś reastart aplikacji albo konfiguracji.')
