import requests
import re
import json
from datetime import datetime
from mainApp.models.event import Event
from mainApp.models.device import Device
# from mainApp.response_operation import ResponseTrigger
from mainApp.dashboard_data import DashboardData
from mainApp import app, logger


class WebContentCollector:
    def __init__(self, id, requestID="A"):
        self.id = id
        if requestID == "A":
            self.requestID = "A" + str(int(datetime.now().timestamp()))
        else:
            self.requestID = requestID

    def collector(self):
        with app.app_context():
            event = Event.query.get(self.id)
            if event is None:
                print("Event not found")
                response = requests.get(httpLink, timeout=5)
            # elif event.deviceId == 0:
            #     httpLink = event.eventLink
            #     print("httpLink: " + httpLink)
            #     try:
            #         response = requests.get(httpLink, timeout=5)
            #         jsonResponse = response.json()
            #         print("response: " + str(response.content))
            #         requestData = {
            #             "requestID": self.requestID,
            #             "addInfo": jsonResponse["stacja"] + " temperatura",
            #             "deviceIP": "danepubliczne",
            #             "deviceName": "API IMGW",
            #             "type": "°C",
            #             "value": jsonResponse["temperatura"],
            #         }
            #         ResponseTrigger(requestData)
            #         requestData = {
            #             "requestID": self.requestID,
            #             "addInfo": jsonResponse["stacja"] + " predkosc wiatru",
            #             "deviceIP": "danepubliczne",
            #             "deviceName": "API IMGW",
            #             "type": "km/h",
            #             "value": jsonResponse["predkosc_wiatru"],
            #         }
            #         ResponseTrigger(requestData)
            #         requestData = {
            #             "requestID": self.requestID,
            #             "addInfo": jsonResponse["stacja"] + " kierunek wiatru",
            #             "deviceIP": "danepubliczne",
            #             "deviceName": "API IMGW",
            #             "type": "°",
            #             "value": jsonResponse["kierunek_wiatru"],
            #         }
            #         ResponseTrigger(requestData)
            #         requestData = {
            #             "requestID": self.requestID,
            #             "addInfo": jsonResponse["stacja"] + " wilgotnosc",
            #             "deviceIP": "danepubliczne",
            #             "deviceName": "API IMGW",
            #             "type": "%",
            #             "value": jsonResponse["wilgotnosc_wzgledna"],
            #         }
            #         ResponseTrigger(requestData)
            #         requestData = {
            #             "requestID": self.requestID,
            #             "addInfo": jsonResponse["stacja"] + " opad",
            #             "deviceIP": "danepubliczne",
            #             "deviceName": "API IMGW",
            #             "type": "mm",
            #             "value": jsonResponse["suma_opadu"],
            #         }
            #         ResponseTrigger(requestData)
            #         requestData = {
            #             "requestID": self.requestID,
            #             "addInfo": jsonResponse["stacja"] + " cisnienie",
            #             "deviceIP": "danepubliczne",
            #             "deviceName": "API IMGW",
            #             "type": "hPa",
            #             "value": jsonResponse["cisnienie"],
            #         }
            #         ResponseTrigger(requestData)
            #     except requests.exceptions.Timeout:

            #         logger.error(f"Timeout error while trying to reach {httpLink}")
            #         # return {"error": "Connection timeout"}
            #     except requests.exceptions.RequestException as e:

            #         logger.error(f"Request error: {e} while trying to reach {httpLink}")
            #         # return {"error": "Connection error"}

            else:
                device = Device.query.get(event.deviceId)
                deviceIP = device.deviceIP
                deviceSSL = device.deviceSSL
                devicePort = device.devicePort
                deviceName = device.deviceName
                deviceProtocol = device.deviceProtocol
                eventLink = event.eventLink

                placeholders = WebContentCollector.extract_placeholders(eventLink)
                resolver = PlaceholderGetter(placeholders)
                received_values = resolver.vlue_getter()

                print(received_values)
                print(placeholders)
                jsonEvent = self.inject_values_into_link(eventLink, received_values)
                jsonEvent = json.loads(jsonEvent)
                jsonEvent["requestID"] = self.requestID
                if deviceProtocol == "json":
                    httpLink = deviceSSL + "://" + deviceIP + "/json"
                    print("httpLink: " + httpLink)
                    print("type of meaasge: " + str(type(jsonEvent)))
                    print(jsonEvent)
                    attempt = 1
                    for attempt in range(5):
                        try:
                            attempt += 1
                            response = requests.post(
                                httpLink, json=jsonEvent, timeout=5
                            )
                            print(response.status_code)
                            print(
                                response.raise_for_status()
                            )  # Sprawdza, czy odpowiedź jest poprawna
                            print("response: " + str(response.content))
                            print("response:", response.text)
                            if response.status_code == 200:
                                logger.error(
                                    f"Attempt: {attempt}. success: {response.status_code} response: {response.text} while trying to reach {httpLink}"
                                )
                                requestData = response.json()
                                requestData["requestID"] = self.requestID
                                ResponseTrigger(requestData)

                                break
                            else:
                                logger.error(
                                    f"Attempt: {attempt}. error response: {response.status_code} response: {response.text} while trying to reach {httpLink}"
                                )
                                requestData = {
                                    "requestID": self.requestID,
                                    "addInfo": "Other  error "
                                    + str(response.status_code)
                                    + ". Attempt:"
                                    + str(attempt),
                                    "deviceIP": deviceIP,
                                    "deviceName": deviceName,
                                    "type": "error",
                                    "value": 0,
                                }
                            ResponseTrigger(requestData)

                        except requests.exceptions.Timeout:

                            logger.error(
                                f"Attempt: {attempt}. Timeout error while trying to reach {httpLink}"
                            )
                            requestData = {
                                "requestID": self.requestID,
                                "addInfo": "Timmeout error. Attempt:" + str(attempt),
                                "deviceIP": deviceIP,
                                "deviceName": deviceName,
                                "type": "error",
                                "value": 0,
                            }
                            ResponseTrigger(requestData)

                        except requests.exceptions.RequestException as e:

                            logger.error(
                                f"Attempt: {attempt}. Request error: {e} while trying to reach {httpLink}"
                            )
                            requestData = {
                                "requestID": self.requestID,
                                "addInfo": "Other  error. Attempt:" + str(attempt),
                                "deviceIP": deviceIP,
                                "deviceName": deviceName,
                                "type": "Error",
                                "value": 0,
                            }
                            ResponseTrigger(requestData)

                elif deviceProtocol == "http":
                    # to development
                    httpLink = (
                        deviceSSL + "://" + deviceIP + ":" + str(devicePort) + eventLink
                    )

    def extract_placeholders(eventLink):
        """zwraca w formie tabel
        nazwy wszystkich zmiennych w linku
        znajdujących sie w <<>>"""
        pattern = r"<<(.*?)>>"  # Wzorzec do znajdowania tekstu w <<>>
        return re.findall(pattern, eventLink)

    def inject_values_into_link(self, eventLink, received_values):
        """
        Zastępuje placeholdery w eventLink odpowiednimi wartościami.

        Args:
            eventLink (str): Link zawierający placeholdery w formacie <<placeholder>>.
            values (dict): Słownik z wartościami dla placeholderów.

        Returns:
            str: Link z wstrzykniętymi wartościami.
        """
        for placeholder, value in received_values.items():
            eventLink = eventLink.replace(f"<<{placeholder}>>", str(value))
        return eventLink


class PlaceholderGetter:
    def __init__(self, placeholders):
        """
        Inicjalizuje klasę z listą placeholderów.

        Args:
            placeholders (list): Lista placeholderów do przetworzenia.
        """
        self.placeholders = placeholders
        self.dashboard_data = DashboardData()  # Inicjalizacja DashboardData

    def vlue_getter(self):
        """
        Przetwarza listę placeholderów i przypisuje im odpowiednie wartości.

        Returns:
            dict: Słownik z przypisanymi wartościami dla placeholderów.
        """
        return {
            placeholder: self.dashboard_data.get_placeholder_value(placeholder)
            for placeholder in self.placeholders
        }


from mainApp.models.archive import ArchiveAdder
from mainApp.models.validation import ValidationLister
from mainApp.email_operations import emailSender



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

            boolean_condition_ignore = False
            boolean_condition_email = False
            boolean_condition_event = False
            boolean_condition_match = False

            for validationItem in validationList:

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


    # def handle_notification(self, readyNotification):

    #     message = readyNotification.message
    #     message = message.replace("<addInfo>",readyNotification.addInfo)
    #     message = message.replace("<type>",readyNotification.type)
    #     message = message.replace("<condition>",readyNotification.condition)
    #     message = message.replace("<value>",str(readyNotification.value))
    #     message = message.replace("<self.value>",str(self.value))
    #     message = message.replace("<date>",str(datetime.now().strftime('%Y-%m-%d')))
    #     message = message.replace("<time>",str(datetime.now().strftime('%H:%M:%S')))


    #     if readyNotification.notificationType == "email":
    #         subject = "Notification: " + readyNotification.type + " for " + readyNotification.deviceName
    #         logger.debug("Email to send. subject: " + subject + ", and message: " + message)
    #         requestData = {'addInfo': 'Automatic-> email sent', 'deviceIP': readyNotification.deviceIP, 'deviceName': readyNotification.deviceName, 'type': 'Info', 'value': '-'}
    #         ArchiveAdder(requestData)
    #         # emailSender(subject=subject, message=message)
    #     elif readyNotification.notificationType == "function":
    #         requestData = {'addInfo': 'Automatic -> event start: ' + readyNotification.eventId , 'deviceIP': readyNotification.deviceIP, 'deviceName': readyNotification.deviceName, 'type': 'Info', 'value': '-'}
    #         ArchiveAdder(requestData)
    #         logger.debug("ID function to run: " + readyNotification.eventId)


# class NotificationTrigger:
#     def __init__(self, requestData: dict) -> None:
#         try:
#             self.addInfo = requestData["addInfo"]
#             self.deviceName = requestData["deviceName"]
#             self.deviceIP = requestData["deviceIP"]
#             self.type = requestData["type"]
#             self.value = requestData["value"]

#             logger.debug("Checking notification condition list")
#             validationLister = ValidationLister(status="Ready")
#             notificationList = validationLister.get_list()
#             for readyNotification in notificationList:
#                 if self.deviceIP == readyNotification.deviceIP and self.deviceName == readyNotification.deviceName and self.type == readyNotification.type and self.addInfo == readyNotification.addInfo:
#                     logger.debug("Notification condition checking")
#                     if readyNotification.condition == "less" and int(readyNotification.value) > int(self.value):
#                         logger.debug("Less condition")
#                         self.handle_notification(readyNotification=readyNotification)
#                     elif readyNotification.condition == "more"and int(readyNotification.value) < int(self.value):
#                         logger.debug("More condition")
#                         self.handle_notification(readyNotification=readyNotification)
#                     elif readyNotification.condition == "equal" and int(readyNotification.value) == int(self.value):
#                         logger.debug("Equal condition")
#                         self.handle_notification(readyNotification=readyNotification)
#                     else:
#                         logger.debug("Wrong condition")

#         except Exception as e:
#             logger.error(f"An error occurred: {e}")
#             self.message = "Error: Record could not be parsed"


#     def handle_notification(self, readyNotification):
#         from mainApp.web_operations import LinkCreator, WebContentCollector
#         from mainApp.models.archive import ArchiveAdder

#         message = readyNotification.message
#         message = message.replace("<addInfo>",readyNotification.addInfo)
#         message = message.replace("<type>",readyNotification.type)
#         message = message.replace("<condition>",readyNotification.condition)
#         message = message.replace("<value>",str(readyNotification.value))
#         message = message.replace("<self.value>",str(self.value))
#         message = message.replace("<date>",str(datetime.now().strftime('%Y-%m-%d')))
#         message = message.replace("<time>",str(datetime.now().strftime('%H:%M:%S')))


#         if readyNotification.notificationType == "email":
#             subject = "Notification: " + readyNotification.type + " for " + readyNotification.deviceName
#             logger.debug("Email to send. subject: " + subject + ", and message: " + message)
#             requestData = {'addInfo': 'Automatic-> email sent', 'deviceIP': readyNotification.deviceIP, 'deviceName': readyNotification.deviceName, 'type': 'Info', 'value': '-'}
#             ArchiveAdder(requestData)
#             # emailSender(subject=subject, message=message)
#         elif readyNotification.notificationType == "function":
#             requestData = {'addInfo': 'Automatic -> event start: ' + readyNotification.eventId , 'deviceIP': readyNotification.deviceIP, 'deviceName': readyNotification.deviceName, 'type': 'Info', 'value': '-'}
#             ArchiveAdder(requestData)
#             logger.debug("ID function to run: " + readyNotification.eventId)
#             WebContentCollector(LinkCreator(readyNotification.eventId, message).functions_list_link_creator()).collect()
