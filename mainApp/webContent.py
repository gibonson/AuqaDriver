import requests
import time
from mainApp.models.function import DevicesFunctions
from mainApp.models.device import Devices
from mainApp.models.archive import Archive
from mainApp import app, db, logger

class LinkCreator:
    def __init__(self, id):
        self.id = id

    def functions_list_link_creator(self):
        deviceFunctions = DevicesFunctions.query.get(self.id)
        devices = Devices.query.get(deviceFunctions.deviceId)
        IP = devices.deviceIP
        actionLink = deviceFunctions.actionLink
        if deviceFunctions.functionParameters != "":
            parameters = deviceFunctions.functionParameters
            httpLink = "http://" + IP + actionLink + "?" + parameters
        else:
            httpLink = "http://" + IP + actionLink
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
        timestamp = round(time.time())
        try:
            print(timestamp)
            
            response = requests.get(self.httpAddress,timeout=5)
            print(response.content)
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
            print(responseContent)
            print()

            for i in range(len(responseContent)):
                responseContent[i] = responseContent[i].split("</sep>")

            openFormName = ""
            openFormLink = ""
            deviceName = ""
            
            for i in range(len(responseContent)):
                print(responseContent[i])
                if responseContent[i][0] == "":
                    responseContent[i] = ['']
                elif responseContent[i][0] == "hHtml":
                    deviceName = responseContent[i][1]
                    responseContent[i] = ['']
                elif responseContent[i][0] == "pHtml":
                    self.deviceRecieveFunctionValues.append([timestamp,self.deviceIP,deviceName,responseContent[i][1],responseContent[i][2],responseContent[i][3]])
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


            print()

            print("deviceIP = " + self.deviceIP)
            print("deviceName = " + deviceName)

            print()
            print("deviceRecieveFunctionValues = " + str(self.deviceRecieveFunctionValues))
            print()


            for row in self.deviceRecieveFunctionValues:
                with app.app_context():
                    print(row)
                    addInfo = row[3]
                    deviceIP = self.deviceIP
                    value = row[4]
                    type = row[5]
                    add_to_archiwe = Archive(timestamp=timestamp,deviceIP = deviceIP, deviceName= deviceName, addInfo = addInfo, value= value, type = type)
                    db.session.add(add_to_archiwe)
                    db.session.commit()

            if self.deviceRecieveFunctionValues == []:
                print("Unrecognized device")
                with app.app_context():
                    addInfo = "Unrecognized device"
                    deviceIP = self.deviceIP
                    deviceName = "-"
                    type = "Log"
                    value = 0
                    add_to_archiwe = Archive(timestamp=timestamp,deviceIP = deviceIP, deviceName= deviceName, addInfo = addInfo, value= value, type = type)
                    db.session.add(add_to_archiwe)
                    db.session.commit()

            # print()
            # print("deviceSendFunctionValues = " + str(self.deviceSendFunctionValues))
            # print()

            # for row in self.deviceSendFunctionValues:
            #     print(row)
        except requests.exceptions.Timeout:
            print("connection issue")
            with app.app_context():
                addInfo = "Connection error"
                deviceIP = self.deviceIP
                deviceName = "-"
                type = "Log"
                value = 0
                add_to_archiwe = Archive(timestamp=timestamp,deviceIP = deviceIP, deviceName= deviceName, addInfo = addInfo, value= value, type = type)
                db.session.add(add_to_archiwe)
                db.session.commit()

