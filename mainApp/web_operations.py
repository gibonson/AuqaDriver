import requests
import re
import json
import os

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
                    response = None
                    try:
                        attempt += 1
                        if event.eventType == "JSON":
                            jsonEvent = json.loads(eventPayloadAfterInjection)
                            jsonEvent["requestID"] = self.requestID
                            response = requests.post(event.eventAddress, json=jsonEvent, timeout=2)
                            logger.info("Response: " + str(response.status_code) + ", " + str(response.content) + " " + response.text)

                        elif event.eventType == "HTTP":
                            eventAddress =  event.eventAddress + "/" + eventPayloadAfterInjection
                            print(eventAddress)
                            response = requests.post(eventAddress, timeout=2)
                            logger.info("Response: " + str(response.status_code) + ", " + str(response.content) + " " + response.text)
                        
                        elif event.eventType == "PHOTO":
                            eventAddress =  event.eventAddress + "/" + eventPayloadAfterInjection
                            print(eventAddress)
                            response = requests.get(eventAddress, timeout=2)
                            SAVE_DIR = "userFiles/media"

                            if response.status_code == 200:
                                filename = datetime.now().strftime("%Y%m%d_%H%M%S.jpg")
                                filepath = os.path.join(SAVE_DIR, self.eventName + "_" + filename)

                                with open(filepath, "wb") as f:
                                    f.write(response.content)

                                print(f"Picture saver: {filepath}")
                                errorMessage = f"Picture: {filepath}, Attempt: {attempt}. success: {response.status_code}, Address: {event.eventAddress}"

                            else:
                                print("Error:", response.status_code)
                            logger.info("Response: " + str(response.status_code) + ", " + filename + " ")
                        
                        else:
                            errorMessage = "Event type not supported"    

                        if response is not None:
                            if response.status_code == 200:
                                logger.debug(
                                    f"Attempt: {attempt}. success: {response.status_code} response: {str(response.text[:100])} while trying to reach {event.eventAddress}"
                                )
                                if event.eventType == "PHOTO":
                                    break
                                try:
                                    requestData = response.json()
                                    
                                    requestData["requestID"] = self.requestID
                                    ResponseTrigger(requestData).execute()
                                except (ValueError, json.JSONDecodeError) as json_err:
                                    errorMessage = f"Attempt: {attempt}. Received 200 OK, but failed to parse JSON. Error: {json_err}. Response text: {str(response.text[:100])}"
                                    break
                            
                            else:
                                errorMessage = f"Attempt: {attempt}. error response: {response.status_code} response: {str(response.text[:100])} while trying to reach {event.eventAddress}"

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
        # __init__ tylko przygotowuje dane (zabezpieczone przez .get())
        self.requestData = requestData
        self.addInfo = requestData.get("addInfo", "")
        self.deviceName = requestData.get("deviceName", "")
        self.deviceIP = requestData.get("deviceIP", "")
        self.type = requestData.get("type", "")
        self.value = requestData.get("value", 0)
        self.requestID = requestData.get("requestID", "")

    def execute(self) -> None:
        # Metoda execute() robi faktyczną robotę (logika biznesowa)
        logger.debug(f"Request to validation: {self.requestData}")
        try:
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
                            
                        elif validationItem.actionType in ["email", "pushover"]:
                            message = validationItem.message
                            message = message.replace("<addInfo>", validationItem.addInfo)
                            message = message.replace("<type>", validationItem.type)
                            message = message.replace("<condition>", validationItem.condition)
                            message = message.replace("<value>", str(validationItem.value))
                            message = message.replace("<self.value>", str(self.value))
                            message = message.replace("<date>", str(datetime.now().strftime('%Y-%m-%d')))
                            message = message.replace("<time>", str(datetime.now().strftime('%H:%M:%S')))

                            subject = f"Notification: {self.type} for {self.deviceName}"
                            logger.debug(f"{validationItem.actionType}, subject: {subject}, and message: {message}")
                            
                            if validationItem.actionType == "email":
                                emailSender(subject=subject, message=message)
                            if validationItem.actionType == "pushover":
                                pushoverSender(message=subject + message)
                             
                        elif validationItem.actionType == "event":
                            logger.debug("Event to start and add to archive")
                            # Tutaj kolejna klasa od razu z poprawnym użyciem jej metody .collector()
                            WebContentCollector(validationItem.eventId, requestID=self.requestID).collector()

            if should_archive:
                self.requestData["addInfo"] = self.requestData["addInfo"][:30]
                # Pamiętaj o użyciu .save(), które dodaliśmy poprzednio!
                ArchiveAdder(requestData=self.requestData).save()

        except Exception as e:
            logger.error(f"An error occurred in ResponseTrigger: {e}")