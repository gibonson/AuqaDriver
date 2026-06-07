from mainApp import logger
from mainApp.config_operations import load_config_json


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
            raw_validation_list = load_config_json('event_validation.json')
            for raw in raw_validation_list:
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

    def get_list(self):
        return self.Validation
    