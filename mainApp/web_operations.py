import requests
from mainApp.models.event import Event
from mainApp.models.device import Devices
from mainApp.response_operation import ResponseTrigger
from mainApp import app, logger

class LinkCreator:
    def __init__(self, id, eventLinkAndParameters = None):
        self.id = id
        self.eventLinkAndParameters = eventLinkAndParameters

    def functions_list_link_creator(self):
        deviceFunctions = Event.query.get(self.id)
        devices = Devices.query.get(deviceFunctions.deviceId)
        IP = devices.deviceIP
        eventLink = deviceFunctions.eventLink
        httpLink = "http://" + IP + eventLink
        return httpLink


class WebContentCollector:

    def __init__(self, httpAddress):
        self.httpAddress = httpAddress
        ip = httpAddress.replace("http://","")
        ip = ip.split("/")[0]
        self.deviceIP = ip
        self.addInfo = ""
        self.deviceRecieveFunctionValues = []
        self.deviceSendFunctionValues = [] 
    
    def collect(self):
        try:
            response = requests.get(self.httpAddress,timeout=5)
            # print(response.content)
            response = str(response.content)
            response = response.replace("b\"","")
            response = response.replace("\\n","")
            response = response.replace("'","")
            response = response.replace("<body>","")
            response = response.replace("</body>","")
            response = response.replace("<div>","")
            response = response.replace("</div>","")
            response = response.replace("<sep>","")

            responseContent = response.split("</br>")
            # print(responseContent)

            for i in range(len(responseContent)):
                responseContent[i] = responseContent[i].split("</sep>")

            openFormName = ""
            openFormLink = ""
            deviceName = ""
            
            for i in range(len(responseContent)):
                logger.debug(responseContent[i])
                if responseContent[i][0] == "":
                    responseContent[i] = ['']
                elif responseContent[i][0] == "hHtml":
                    deviceName = responseContent[i][1]
                    responseContent[i] = ['']
                elif responseContent[i][0] == "pHtml":
                    self.deviceRecieveFunctionValues.append([self.deviceIP,deviceName,responseContent[i][1],responseContent[i][2],responseContent[i][3]])
                    responseContent[i] = ['']
                elif responseContent[i][0] == "button":
                    self.deviceSendFunctionValues.append([self.deviceIP,deviceName,responseContent[i][1],responseContent[i][2],"button",responseContent[i][3]])
                    responseContent[i] = ['']
                elif responseContent[i][0] == "button2":
                    self.deviceSendFunctionValues.append([self.deviceIP,deviceName,responseContent[i][1],responseContent[i][2],"button2",responseContent[i][3]])
                    responseContent[i] = ['']
                elif responseContent[i][0] == "formBegin":
                    openFormName = responseContent[i][2]
                    openFormLink = responseContent[i][1]
                    responseContent[i] = ['']
                elif responseContent[i][0] == "formNumber":
                    self.deviceSendFunctionValues.append([self.deviceIP,deviceName,openFormName,openFormLink,"formNumber",responseContent[i][1],responseContent[i][2],responseContent[i][3]])
                    responseContent[i] = ['']
                elif responseContent[i][0] == "formEnd":
                    self.deviceSendFunctionValues.append([self.deviceIP,deviceName,openFormName,openFormLink,"formEnd",responseContent[i][1],"",""])
                    responseContent[i] = ['']


            logger.debug("deviceIP = " + self.deviceIP + "deviceName = " + deviceName + "deviceRecieveFunctionValues = " + str(self.deviceRecieveFunctionValues))

            for row in self.deviceRecieveFunctionValues:
                with app.app_context():
                    addInfo = row[2]
                    deviceIP = self.deviceIP
                    value = row[3]
                    type = row[4]
                    requestData = {'addInfo': row[2], 'deviceIP': self.deviceIP, 'deviceName': deviceName, 'type': row[4], 'value': row[3]}
                    ResponseTrigger(requestData)

            if self.deviceRecieveFunctionValues == []:
                with app.app_context():
                    requestData = {'addInfo': 'Unrecognized device', 'deviceIP': self.deviceIP, 'deviceName': '-', 'type': 'Error', 'value': 0}
                    ResponseTrigger(requestData)

        except requests.exceptions.Timeout:
            logger.error(f"Timeout error while trying to reach {self.httpAddress}")
            with app.app_context():
                requestData = {'addInfo': 'Connection timeout', 'deviceIP': self.deviceIP, 'deviceName': '-', 'type': 'Error', 'value': 0}
                ResponseTrigger(requestData)

        except requests.exceptions.ConnectionError as e:
            logger.error(f"Connection error: {e} while trying to reach {self.httpAddress}")
            with app.app_context():
                requestData = {'addInfo': 'Connection error', 'deviceIP': self.deviceIP, 'deviceName': '-', 'type': 'Error', 'value': 0}
                ResponseTrigger(requestData)

        except Exception as e:
            logger.error(f"An unexpected error occurred: {e}")
            with app.app_context():
                requestData = {'addInfo': 'Unexpected error', 'deviceIP': self.deviceIP, 'deviceName': '-', 'type': 'Error', 'value': 0}
                ResponseTrigger(requestData)