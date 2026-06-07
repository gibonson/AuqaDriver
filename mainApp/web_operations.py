import requests
import re
import json
from datetime import datetime
from mainApp.models.event import EventGetByEventName
# from mainApp.models.device import Device
# from mainApp.response_operation import ResponseTrigger
from mainApp.dashboard_data import DashboardData
from mainApp import app, logger


class WebContentCollector:
    def __init__(self, eventName, requestID="A"):
        self.eventName = eventName
        if requestID == "A":
            self.requestID = "A" + str(int(datetime.now().timestamp()))
        else:
            self.requestID = requestID

    def collector(self):
        event = EventGetByEventName(self.eventName).get_event()    
        if event is None or event.eventStatus != "Ready":
            print("Event not found or not ready")
        else:
            print("Event found: ")
            print(str(event.eventAddress))
            print(str(event.eventPayload))
            received_values2 = InjectValuesIntoPayload(event.eventPayload).getPayload()
            print("var2: " + str(received_values2))
       
            if event.eventType == "JSON":
                print("Event JSON")
                
            elif event.eventType == "HTTP":
                print("Event HTTP")
                
            else:
                print("Event type not supported")       
       


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

      
       
        #         if (eventPayload.startswith("{") and eventPayload.endswith("}")): 
        #             jsonEvent = self.inject_values_into_link(eventPayload, received_values)
        #             jsonEvent = json.loads(jsonEvent)
        #             jsonEvent["requestID"] = self.requestID
        #             print("httpLink: " + eventAddress)                   
        #             print("type of meaasge: " + str(type(jsonEvent)))
        #             print(jsonEvent)
        #             attempt = 1
        #             for attempt in range(2):
        #                 try:
        #                     attempt += 1
        #                     response = requests.post(
        #                         eventAddress, json=jsonEvent, timeout=5
        #                     )
        #                     print(response.status_code)
        #                     print(
        #                         response.raise_for_status()
        #                     )  # Sprawdza, czy odpowiedź jest poprawna
        #                     print("response: " + str(response.content))
        #                     print("response:", response.text)
        #                     if response.status_code == 200:
        #                         logger.error(
        #                             f"Attempt: {attempt}. success: {response.status_code} response: {response.text} while trying to reach {eventAddress}"
        #                         )
        #                         requestData = response.json()
        #                         requestData["requestID"] = self.requestID
        #                         ResponseTrigger(requestData)

        #                         break
        #                     else:
        #                         logger.error(
        #                             f"Attempt: {attempt}. error response: {response.status_code} response: {response.text} while trying to reach {eventAddress}"
        #                         )
        #                         requestData = {
        #                             "requestID": self.requestID,
        #                             "addInfo": "Other  error "
        #                             + str(response.status_code)
        #                             + ". Attempt:"
        #                             + str(attempt),
        #                             "deviceIP": eventAddress,
        #                             "deviceName": "",
        #                             "type": "error",
        #                             "value": 0,
        #                         }
        #                     ResponseTrigger(requestData)

        #                 except requests.exceptions.Timeout:

        #                     logger.error(
        #                         f"Attempt: {attempt}. Timeout error while trying to reach {eventAddress}"
        #                     )
        #                     requestData = {
        #                         "requestID": self.requestID,
        #                         "addInfo": "Timmeout error. Attempt:" + str(attempt),
        #                         "deviceIP": eventAddress,
        #                         "deviceName": "",
        #                         "type": "error",
        #                         "value": 0,
        #                     }
        #                     ResponseTrigger(requestData)

        #                 except requests.exceptions.RequestException as e:

        #                     logger.error(
        #                         f"Attempt: {attempt}. Request error: {e} while trying to reach {eventAddress}"
        #                     )
        #                     requestData = {
        #                         "requestID": self.requestID,
        #                         "addInfo": "Other  error. Attempt:" + str(attempt),
        #                         "deviceIP": eventAddress,
        #                         "deviceName": "",
        #                         "type": "Error",
        #                         "value": 0,
        #                     }
        #                     ResponseTrigger(requestData)

        #         else:
        #             print("totally not json")
        #             eventAddress =  eventAddress + "/" + eventPayload
        #             attempt = 1
        #             for attempt in range(2):
        #                 try:
        #                     response = requests.post(eventAddress, timeout=5)
        #                     print(response.status_code)
        #                     print(response.raise_for_status())
        #                     if response.status_code == 200:
        #                         logger.error(
        #                             f"Attempt: {attempt}. success: {response.status_code} response: {response.text} while trying to reach {eventAddress}"
        #                         )
        #                         requestData = response.json()
        #                         requestData["requestID"] = self.requestID
        #                         ResponseTrigger(requestData)

        #                         break
        #                     else:
        #                         logger.error(
        #                             f"Attempt: {attempt}. error response: {response.status_code} response: {response.text} while trying to reach {eventAddress}"
        #                         )
        #                         requestData = {
        #                             "requestID": self.requestID,
        #                             "addInfo": "Other  error "
        #                             + str(response.status_code)
        #                             + ". Attempt:"
        #                             + str(attempt),
        #                             "deviceIP": eventAddress,
        #                             "deviceName": "",
        #                             "type": "error",
        #                             "value": 0,
        #                         }
        #                     ResponseTrigger(requestData)
                            
        #                 except requests.exceptions.Timeout:

        #                     logger.error(
        #                         f"Attempt: {attempt}. Timeout error while trying to reach {eventAddress}"
        #                     )
        #                     requestData = {
        #                         "requestID": self.requestID,
        #                         "addInfo": "Timmeout error. Attempt:" + str(attempt),
        #                         "deviceIP": eventAddress,
        #                         "deviceName": "",
        #                         "type": "error",
        #                         "value": 0,
        #                     }
        #                     ResponseTrigger(requestData)

        #                 except requests.exceptions.RequestException as e:

        #                     logger.error(
        #                         f"Attempt: {attempt}. Request error: {e} while trying to reach {eventAddress}"
        #                     )
        #                     requestData = {
        #                         "requestID": self.requestID,
        #                         "addInfo": "Other  error. Attempt:" + str(attempt),
        #                         "deviceIP": eventAddress,
        #                         "deviceName": "",
        #                         "type": "Error",
        #                         "value": 0,
        #                     }
        #                     ResponseTrigger(requestData)




from mainApp.models.archive import ArchiveAdder
from mainApp.models.event_validation import ValidationLister
from mainApp.email_operations import emailSender, pushoverSender



from mainApp import logger
import time
from datetime import datetime


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

            logger.debug("Checking validation list")
            validationLister = ValidationLister(status="Ready")
            validationList = validationLister.get_list()



            for validationItem in validationList:

                boolean_condition_ignore = False
                boolean_condition_email = False
                boolean_condition_event = False
                boolean_condition_match = False

                if (self.deviceIP, self.deviceName, self.type, self.addInfo) == (validationItem.deviceIP, validationItem.deviceName, validationItem.type, validationItem.addInfo):
                    logger.debug(" deviceIP, deviceName, type, addinfo match")
                    if validationItem.condition == "less" and int(validationItem.value) > int(self.value):
                         logger.debug("less condition match")
                         boolean_condition_match = True
                    if validationItem.condition == "more" and int(validationItem.value) < int(self.value):
                         logger.debug("more condition match")
                         boolean_condition_match
                    if validationItem.condition == "equal" and int(validationItem.value) == int(self.value):
                         logger.debug("equal condition match")
                         boolean_condition_match = True
                    else:
                        logger.debug("condition not match, skipping to next validation item")
                    if boolean_condition_match == True:
                        if validationItem.actionType == "ignore":
                            boolean_condition_ignore = True
                            logger.debug("Ignore request")
                        if validationItem.actionType == "email":
                            boolean_condition_email = True
                            logger.debug("Send email action")
                        if validationItem.actionType == "event":
                            boolean_condition_event = True
                            logger.debug("Start event action")            
                else:
                    logger.debug("Vdev ip, name type, addinfo not match -> adding to archive")
                
                if boolean_condition_ignore == True and boolean_condition_match == True:
                    logger.debug("Request to ignore")
                elif boolean_condition_email == True and boolean_condition_match == True:
                    logger.debug("Email to send and add to archive")
                    ArchiveAdder(requestData=requestData)
                    
                    print("Preparing email")
                    print(validationItem.message)
                    message = validationItem.message
                    message = message.replace("<addInfo>",validationItem.addInfo)
                    message = message.replace("<type>",validationItem.type)
                    message = message.replace("<condition>",validationItem.condition)
                    message = message.replace("<value>",str(validationItem.value))
                    message = message.replace("<self.value>",str(self.value))
                    message = message.replace("<date>",str(datetime.now().strftime('%Y-%m-%d')))
                    message = message.replace("<time>",str(datetime.now().strftime('%H:%M:%S')))

                    subject = "Notification: " + self.type + " for " + self.deviceName
                    logger.debug("Email to send. subject: " + subject + ", and message: " + message)
                    # emailSender(subject=subject, message=message)
                    pushoverSender(message=subject + message)
                elif boolean_condition_event == True and boolean_condition_event == True:
                    logger.debug("Event to start and add to archive")
                    ArchiveAdder(requestData=requestData)
                    WebContentCollector(validationItem.eventId, requestID = self.requestID).collector()

                else:
                    logger.debug("Adding to archive only")
                    ArchiveAdder(requestData=requestData)

        except Exception as e:
            logger.error(f"An error occurred: {e}")
            self.message = "Error: Record could not be parsed"
