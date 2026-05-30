import os
import json
import shutil
import datetime

from mainApp import logger


# def get_table_by_name(table_name):
#     table_mapping = {
#         'eventConfig': 'event_config.json',
#         'reportConfig': 'report_config.json',
#         'dashboardConfig': 'dashboard_config.json',
#         'validationConfig': 'validation_config.json',
#         'schedulerConfig': 'scheduler_config.json'
#     }
#     return table_mapping.get(table_name, None)

# def get_table(table_name):
    
    


def get_config_dir():
    config_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'userFiles', 'config'))
    os.makedirs(config_dir, exist_ok=True)
    return config_dir

def get_config_backup_dir():
    config_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'userFiles', 'config', 'backup'))
    os.makedirs(config_dir, exist_ok=True)
    return config_dir

def get_config_file_path(file_name, subfolder=None):
    config_dir = get_config_dir()
    if subfolder:
        config_dir = os.path.join(config_dir, subfolder)
        os.makedirs(config_dir, exist_ok=True)
    return os.path.join(config_dir, file_name)


def get_config_backup_file_path(file_name, subfolder=None):
    backup_dir = get_config_backup_dir()
    if subfolder:
        backup_dir = os.path.join(backup_dir, subfolder)
        os.makedirs(backup_dir, exist_ok=True)
    name, ext = os.path.splitext(file_name)
    timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
    return os.path.join(backup_dir, f'{name}_{timestamp}{ext}')


def load_json_config(file_name, subfolder=None, default=None):
    path = get_config_file_path(file_name, subfolder=subfolder)
    if not os.path.exists(path):
        save_json_config(file_name, default if default is not None else [], subfolder=subfolder)
    with open(path, 'r', encoding='utf-8') as config_file:
        return json.load(config_file)


def save_json_config(file_name, data, subfolder=None):
    path = get_config_file_path(file_name, subfolder=subfolder)
    with open(path, 'w', encoding='utf-8') as config_file:
        json.dump(data, config_file, indent=2, ensure_ascii=False)
    return path


def load_config_text(file_name, default='[]', subfolder=None):
    path = get_config_file_path(file_name, subfolder=subfolder)
    if not os.path.exists(path):
        save_config_text(file_name, default, subfolder=subfolder)
    with open(path, 'r', encoding='utf-8') as config_file:
        return config_file.read()


def save_config_text(file_name, text, subfolder=None):
    path = get_config_file_path(file_name, subfolder=subfolder)
    with open(path, 'w', encoding='utf-8') as config_file:
        config_file.write(text)
    logger.info(f'Konfiguracja zapisana w: {path}')
    return path


def backup_config_file(file_name, subfolder=None):
    path = get_config_file_path(file_name, subfolder=subfolder)
    if os.path.exists(path):
        backup_path = get_config_backup_file_path(file_name, subfolder=subfolder)
        shutil.copy2(path, backup_path)
        logger.info(f'Backup konfiguracji zapisano w: {backup_path}')
        return backup_path
    return None


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


def validate_dashboard_config_text(text):
    config = parse_config_text(text)
    return validate_dashboard_config_object(config)


def validate_dashboard_config_object(config):
    if not isinstance(config, list):
        raise ValueError('Konfiguracja dashboardów musi być listą obiektów.')

    seen_ids = set()
    for index, dashboard in enumerate(config, start=1):
        if not isinstance(dashboard, dict):
            raise ValueError(f'Dashboard #{index} musi być obiektem JSON.')

        required_keys = ['panelType', 'panelItemId', 'panelLocation', 'panelName', 'panelCode', 'panelStatus']
        for key in required_keys:
            if key not in dashboard:
                raise ValueError(f'Dashboard #{index}: brak pola {key}.')

        if not dashboard.get('panelType'):
            raise ValueError(f'Dashboard #{index}: panelType nie może być pusty.')
        if dashboard.get('panelItemId') is None or str(dashboard.get('panelItemId')) == '':
            raise ValueError(f'Dashboard #{index}: panelItemId nie może być puste.')
        if not dashboard.get('panelLocation'):
            raise ValueError(f'Dashboard #{index}: panelLocation nie może być puste.')
        if not dashboard.get('panelName'):
            raise ValueError(f'Dashboard #{index}: panelName nie może być puste.')
        if dashboard.get('panelCode') is None:
            raise ValueError(f'Dashboard #{index}: panelCode nie może być puste.')

        status = dashboard.get('panelStatus')
        if status not in ['Active', 'Inactive']:
            raise ValueError(f'Dashboard #{index}: panelStatus musi być "Active" lub "Inactive".')

    return config


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


def validate_validation_config_text(text):
    config = parse_config_text(text)
    return validate_validation_config_object(config)


def validate_scheduler_config_text(text):
    config = parse_config_text(text)
    return validate_scheduler_config_object(config)


def validate_validation_config_object(config):
    if not isinstance(config, list):
        raise ValueError('Konfiguracja walidacji musi być listą obiektów.')

    seen_ids = set()
    allowed_conditions = ['less', 'more', 'equal']
    allowed_action_types = ['email', 'event', 'ignore']
    allowed_status_values = ['Ready', 'Not Ready', 'Not ready']

    for index, validation in enumerate(config, start=1):
        if not isinstance(validation, dict):
            raise ValueError(f'Walidacja #{index} musi być obiektem JSON.')

        required_keys = ['id', 'description', 'deviceIP', 'deviceName', 'addInfo', 'type', 'condition', 'value', 'actionType', 'status']
        for key in required_keys:
            if key not in validation:
                raise ValueError(f'Walidacja #{index}: brak pola {key}.')

        validation_id = validation.get('id')
        try:
            validation_id_int = int(validation_id)
        except (ValueError, TypeError):
            raise ValueError(f'Walidacja #{index}: pole id musi być liczbą całkowitą.')
        if validation_id_int in seen_ids:
            raise ValueError(f'Walidacja #{index}: duplikat id "{validation_id_int}".')
        seen_ids.add(validation_id_int)

        description = validation.get('description')
        if not description:
            raise ValueError(f'Walidacja #{index}: description nie może być puste.')

        deviceIP = validation.get('deviceIP')
        if not deviceIP:
            raise ValueError(f'Walidacja #{index}: deviceIP nie może być pusty.')

        deviceName = validation.get('deviceName')
        if not deviceName:
            raise ValueError(f'Walidacja #{index}: deviceName nie może być pusty.')

        addInfo = validation.get('addInfo')
        if not addInfo:
            raise ValueError(f'Walidacja #{index}: addInfo nie może być puste.')

        type_value = validation.get('type')
        if not type_value:
            raise ValueError(f'Walidacja #{index}: type nie może być pusty.')

        condition = validation.get('condition')
        if condition not in allowed_conditions:
            raise ValueError(f'Walidacja #{index}: condition musi być jednym z {allowed_conditions}.')

        value = validation.get('value')
        try:
            int(value)
        except (ValueError, TypeError):
            raise ValueError(f'Walidacja #{index}: pole value musi być liczbą.')

        action_type = validation.get('actionType')
        if action_type not in allowed_action_types:
            raise ValueError(f'Walidacja #{index}: actionType musi być jednym z {allowed_action_types}.')

        status = validation.get('status')
        if status not in allowed_status_values:
            raise ValueError(f'Walidacja #{index}: status musi być "Ready" lub "Not Ready".')

        event_id = validation.get('eventId')
        if event_id is not None and event_id != '':
            try:
                int(event_id)
            except (ValueError, TypeError):
                raise ValueError(f'Walidacja #{index}: pole eventId musi być liczbą lub puste.')

    return config


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




def restart_application():
    logger.warning('kiedyś reastart aplikacji albo konfiguracji.')
