# from mainApp.models.archive import ArchiveAdder
# from mainApp.models.validation import ValidationLister
# from mainApp.email_operations import emailSender
# from mainApp.web_operations import WebContentCollector


# from mainApp import logger
# import time
# from datetime import datetime


# class ResponseTrigger:
#     def __init__(self, requestData: dict) -> None:
#         logger.debug(f"Request to validation: {requestData}")
#         try:
#             self.addInfo = requestData["addInfo"]
#             self.deviceName = requestData["deviceName"]
#             self.deviceIP = requestData["deviceIP"]
#             self.type = requestData["type"]
#             self.value = requestData["value"]
#             self.requestID = requestData["requestID"]

#             logger.debug("Checking validation list")
#             validationLister = ValidationLister(status="Ready")
#             validationList = validationLister.get_list()

#             boolean_condition_ignore = False
#             boolean_condition_email = False
#             boolean_condition_event = False
#             boolean_condition_match = False

#             for validationItem in validationList:

#                 if (self.deviceIP, self.deviceName, self.type, self.addInfo) == (validationItem.deviceIP, validationItem.deviceName, validationItem.type, validationItem.addInfo):
#                     logger.debug(" deviceIP, deviceName, type, addinfo match")
#                     if validationItem.condition == "less" and int(validationItem.value) > int(self.value):
#                          logger.debug("less condition match")
#                          boolean_condition_match = True
#                     if validationItem.condition == "more" and int(validationItem.value) < int(self.value):
#                          logger.debug("more condition match")
#                          boolean_condition_match
#                     if validationItem.condition == "equal" and int(validationItem.value) == int(self.value):
#                          logger.debug("equal condition match")
#                          boolean_condition_match = True
#                     else:
#                         logger.debug("condition not match, skipping to next validation item")
#                     if boolean_condition_match == True:
#                         if validationItem.actionType == "ignore":
#                             boolean_condition_ignore = True
#                             logger.debug("Ignore request")
#                         if validationItem.actionType == "email":
#                             boolean_condition_email = True
#                             logger.debug("Send email action")
#                         if validationItem.actionType == "event":
#                             boolean_condition_event = True
#                             logger.debug("Start event action")            
#             else:
#                 logger.debug("Vdev ip, name type, addinfo not match -> adding to archive")
            
#             if boolean_condition_ignore == True and boolean_condition_match == True:
#                 logger.debug("Request to ignore")
#             elif boolean_condition_email == True and boolean_condition_match == True:
#                 logger.debug("Email to send and add to archive")
#                 ArchiveAdder(requestData=requestData)
#             elif boolean_condition_event == True and boolean_condition_event == True:
#                 logger.debug("Event to start and add to archive")
#                 ArchiveAdder(requestData=requestData)
#                 WebContentCollector(validationItem.eventId, requestID = self.requestID).collect()

#             else:
#                 logger.debug("Adding to archive only")
#                 ArchiveAdder(requestData=requestData)

#         except Exception as e:
#             logger.error(f"An error occurred: {e}")
#             self.message = "Error: Record could not be parsed"


#     # def handle_notification(self, readyNotification):

#     #     message = readyNotification.message
#     #     message = message.replace("<addInfo>",readyNotification.addInfo)
#     #     message = message.replace("<type>",readyNotification.type)
#     #     message = message.replace("<condition>",readyNotification.condition)
#     #     message = message.replace("<value>",str(readyNotification.value))
#     #     message = message.replace("<self.value>",str(self.value))
#     #     message = message.replace("<date>",str(datetime.now().strftime('%Y-%m-%d')))
#     #     message = message.replace("<time>",str(datetime.now().strftime('%H:%M:%S')))


#     #     if readyNotification.notificationType == "email":
#     #         subject = "Notification: " + readyNotification.type + " for " + readyNotification.deviceName
#     #         logger.debug("Email to send. subject: " + subject + ", and message: " + message)
#     #         requestData = {'addInfo': 'Automatic-> email sent', 'deviceIP': readyNotification.deviceIP, 'deviceName': readyNotification.deviceName, 'type': 'Info', 'value': '-'}
#     #         ArchiveAdder(requestData)
#     #         # emailSender(subject=subject, message=message)
#     #     elif readyNotification.notificationType == "function":
#     #         requestData = {'addInfo': 'Automatic -> event start: ' + readyNotification.eventId , 'deviceIP': readyNotification.deviceIP, 'deviceName': readyNotification.deviceName, 'type': 'Info', 'value': '-'}
#     #         ArchiveAdder(requestData)
#     #         logger.debug("ID function to run: " + readyNotification.eventId)


# # class NotificationTrigger:
# #     def __init__(self, requestData: dict) -> None:
# #         try:
# #             self.addInfo = requestData["addInfo"]
# #             self.deviceName = requestData["deviceName"]
# #             self.deviceIP = requestData["deviceIP"]
# #             self.type = requestData["type"]
# #             self.value = requestData["value"]

# #             logger.debug("Checking notification condition list")
# #             validationLister = ValidationLister(status="Ready")
# #             notificationList = validationLister.get_list()
# #             for readyNotification in notificationList:
# #                 if self.deviceIP == readyNotification.deviceIP and self.deviceName == readyNotification.deviceName and self.type == readyNotification.type and self.addInfo == readyNotification.addInfo:
# #                     logger.debug("Notification condition checking")
# #                     if readyNotification.condition == "less" and int(readyNotification.value) > int(self.value):
# #                         logger.debug("Less condition")
# #                         self.handle_notification(readyNotification=readyNotification)
# #                     elif readyNotification.condition == "more"and int(readyNotification.value) < int(self.value):
# #                         logger.debug("More condition")
# #                         self.handle_notification(readyNotification=readyNotification)
# #                     elif readyNotification.condition == "equal" and int(readyNotification.value) == int(self.value):
# #                         logger.debug("Equal condition")
# #                         self.handle_notification(readyNotification=readyNotification)
# #                     else:
# #                         logger.debug("Wrong condition")

# #         except Exception as e:
# #             logger.error(f"An error occurred: {e}")
# #             self.message = "Error: Record could not be parsed"


# #     def handle_notification(self, readyNotification):
# #         from mainApp.web_operations import LinkCreator, WebContentCollector
# #         from mainApp.models.archive import ArchiveAdder

# #         message = readyNotification.message
# #         message = message.replace("<addInfo>",readyNotification.addInfo)
# #         message = message.replace("<type>",readyNotification.type)
# #         message = message.replace("<condition>",readyNotification.condition)
# #         message = message.replace("<value>",str(readyNotification.value))
# #         message = message.replace("<self.value>",str(self.value))
# #         message = message.replace("<date>",str(datetime.now().strftime('%Y-%m-%d')))
# #         message = message.replace("<time>",str(datetime.now().strftime('%H:%M:%S')))


# #         if readyNotification.notificationType == "email":
# #             subject = "Notification: " + readyNotification.type + " for " + readyNotification.deviceName
# #             logger.debug("Email to send. subject: " + subject + ", and message: " + message)
# #             requestData = {'addInfo': 'Automatic-> email sent', 'deviceIP': readyNotification.deviceIP, 'deviceName': readyNotification.deviceName, 'type': 'Info', 'value': '-'}
# #             ArchiveAdder(requestData)
# #             # emailSender(subject=subject, message=message)
# #         elif readyNotification.notificationType == "function":
# #             requestData = {'addInfo': 'Automatic -> event start: ' + readyNotification.eventId , 'deviceIP': readyNotification.deviceIP, 'deviceName': readyNotification.deviceName, 'type': 'Info', 'value': '-'}
# #             ArchiveAdder(requestData)
# #             logger.debug("ID function to run: " + readyNotification.eventId)
# #             WebContentCollector(LinkCreator(readyNotification.eventId, message).functions_list_link_creator()).collect()
