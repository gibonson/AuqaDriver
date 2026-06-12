import requests
import re
import json
from datetime import datetime
from mainApp.utils import DashboardData
from mainApp import app, logger
from mainApp.models.event import EventGetByEventName
from mainApp.models.archive import ArchiveAdder
from mainApp.models.event_validation import ValidationLister
from mainApp.notification_operations import emailSender, pushoverSender


class WebContentCollector:
    def __init__(self, eventName, requestID="A"):
        self.eventName = eventName
        if requestID == "A":
            self.requestID = "A" + str(int(datetime.now().timestamp()))
        else:
            self.requestID = requestID

    def collector(self):
        with app.app_context():
            event = EventGetByEventName(self.eventName).get_event()    
            if event is None or event.eventStatus != "Ready":
                logger.error(f"Event {self.eventName} not found or not ready")
            else:
                eventPayloadAfterInjection = InjectValuesIntoPayload(event.eventPayload).getPayload()
                logger.info("Event found, address: " + str(event.eventAddress) + ", Payload: " + str(event.eventPayload) + " -> " + str(eventPayloadAfterInjection))

                errorMessage = ""

                attempt = 0
                for attempt in range(3):
                    try:
                        attempt += 1

                        if event.eventType == "JSON":
                            jsonEvent = json.loads(eventPayloadAfterInjection)
                            jsonEvent["requestID"] = self.requestID
                            response = requests.post(event.eventAddress, json=jsonEvent, timeout=5)
                            logger.info("Response: " + str(response.status_code) + ", " + str(response.content) + " " + response.text)

                        elif event.eventType == "HTTP":
                            eventAddress =  event.eventAddress + "/" + eventPayloadAfterInjection
                            response = requests.post(eventAddress, timeout=5)
                            logger.info("Response: " + str(response.status_code) + ", " + str(response.content) + " " + response.text)
                        
                        else:
                            errorMessage = "Event type not supported"    

                        if response.status_code == 200:
                            logger.debug(
                                f"Attempt: {attempt}. success: {response.status_code} response: {response.text} while trying to reach {event.eventAddress}"
                            )
                            try:
                                requestData = response.json()
                                requestData["requestID"] = self.requestID
                                ResponseTrigger(requestData)
                            except (ValueError, json.JSONDecodeError) as json_err:
                                errorMessage = f"Attempt: {attempt}. Received 200 OK, but failed to parse JSON. Error: {json_err}. Response text: {response.text}"
                            
                            break
                        
                        else:
                            errorMessage = f"Attempt: {attempt}. error response: {response.status_code} response: {response.text} while trying to reach {event.eventAddress}"

                    except requests.exceptions.Timeout:
                            errorMessage = f"Attempt: {attempt}. Timeout error while trying to reach {event.eventAddress}"

                    except requests.exceptions.RequestException as e:
                            errorMessage= f"Attempt: {attempt}. Request error: {e} while trying to reach {event.eventAddress}"
                        
                if errorMessage != "":
                    logger.error(errorMessage)
                    requestData = {
                        "requestID": self.requestID,
                        "addInfo": errorMessage,
                        "deviceIP": event.eventAddress,
                        "deviceName": "",
                        "type": "Error",
                        "value": 0,
                    }
                    ResponseTrigger(requestData)



class InjectValuesIntoPayload:
    def __init__(self, payload):
        self.payload = payload
        
    def getPayload(self):
        valuesToChange = re.findall(r"<<(.*?)>>", self.payload)
        dashboardData = DashboardData()
        for value in valuesToChange:
            valueToInject = dashboardData.get_placeholder_value(value)
            self.payload = self.payload.replace(f"<<{value}>>", str(valueToInject))
        return self.payload 



class ResponseTrigger:
    def __init__(self, requestData: dict) -> None:
        logger.debug(f"Request to validation: {requestData}")
        try:
            self.addInfo = requestData["addInfo"]
            self.deviceName = requestData["deviceName"]
            self.deviceIP = requestData["deviceIP"]
            self.type = requestData["type"]
            self.value = requestData["value"]
            self.requestID = requestData["requestID"]

            validationLister = ValidationLister(status="Ready")
            validationList = validationLister.get_list()

            should_archive = True

            for validationItem in validationList:
                if (self.deviceIP, self.deviceName, self.type, self.addInfo) == (validationItem.deviceIP, validationItem.deviceName, validationItem.type, validationItem.addInfo):
                    boolean_condition_match = False
                    
                    if validationItem.condition == "less" and int(validationItem.value) > int(self.value):
                        boolean_condition_match = True
                    elif validationItem.condition == "more" and int(validationItem.value) < int(self.value):
                        boolean_condition_match = True
                    elif validationItem.condition == "equal" and int(validationItem.value) == int(self.value):
                        boolean_condition_match = True

                    if boolean_condition_match:
                        if validationItem.actionType == "ignore":
                            logger.debug("Ignore request")
                            should_archive = False
                            break
                            
                        elif validationItem.actionType == "email" or validationItem.actionType == "pushover":

                            message = validationItem.message
                            message = message.replace("<addInfo>", validationItem.addInfo)
                            message = message.replace("<type>", validationItem.type)
                            message = message.replace("<condition>", validationItem.condition)
                            message = message.replace("<value>", str(validationItem.value))
                            message = message.replace("<self.value>", str(self.value))
                            message = message.replace("<date>", str(datetime.now().strftime('%Y-%m-%d')))
                            message = message.replace("<time>", str(datetime.now().strftime('%H:%M:%S')))

                            subject = "Notification: " + self.type + " for " + self.deviceName
                            logger.debug(validationItem.actionType + ", subject: " + subject + ", and message: " + message)
                            if validationItem.actionType == "email":
                                emailSender(subject=subject, message=message)
                            if validationItem.actionType == "pushover":
                                pushoverSender(message=subject + message)
                             
                        elif validationItem.actionType == "event":
                            logger.debug("Event to start and add to archive")
                            WebContentCollector(validationItem.eventId, requestID=self.requestID).collector()


            if should_archive:
                requestData["addInfo"] = requestData["addInfo"][:30]
                ArchiveAdder(requestData=requestData)

        except Exception as e:
            logger.error(f"An error occurred: {e}")
            self.message = "Error: Record could not be parsed"