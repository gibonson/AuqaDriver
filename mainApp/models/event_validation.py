import json
import os

from mainApp.config_operations import load_config_text
from mainApp import logger

class Validation:
    def __init__(
        self,
        id,
        description,
        deviceIP,
        deviceName,
        addInfo,
        type,
        condition,
        value,
        status,
        actionType,
        eventId=None,
        message=''
    ):
        self.id = id
        self.description = description
        self.deviceIP = deviceIP
        self.deviceName = deviceName
        self.addInfo = addInfo
        self.type = type
        self.condition = condition
        self.value = value
        self.status = status
        self.actionType = actionType
        self.eventId = eventId
        self.message = message


class ValidationLister:
    def __init__(self, status='All', actionType='All'):
        self.Validation = []
        try:
            raw_validations = load_config_text('event_validation.json', default=[])
            if not isinstance(raw_validations, list):
                raw_validations = []
            for raw in raw_validations:
                if not isinstance(raw, dict):
                    continue
                validation = Validation(
                    id=raw.get('id'),
                    description=raw.get('description'),
                    deviceIP=raw.get('deviceIP'),
                    deviceName=raw.get('deviceName'),
                    addInfo=raw.get('addInfo'),
                    type=raw.get('type'),
                    condition=raw.get('condition'),
                    value=raw.get('value'),
                    status=raw.get('status'),
                    actionType=raw.get('actionType'),
                    eventId=raw.get('eventId'),
                    message=raw.get('message', '')
                )
                self.Validation.append(validation)
        except Exception as e:
            logger.error(f'An error occurred while fetching Validation: {e}')
            self.Validation = []

    def get_list(self):
        return self.Validation
    