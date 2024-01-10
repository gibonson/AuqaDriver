import requests
import time
from mainApp.models import Devices, DevicesFunctions
from mainApp.models import Archive
from mainApp import app, db

class LinkCreator:
    def __init__(self, id):
        self.id = id

    def functions_list_link_creator(self):
        deviceFunctions = DevicesFunctions.query.get(self.id)
        devices = Devices.query.get(deviceFunctions.deviceId)
        IP = devices.deviceIP
        jobType = deviceFunctions.jobType
        actionLink = deviceFunctions.actionLink
        parameters = deviceFunctions.functionParameters
        httpLink = ""
        if jobType == "jobCollector":
            httpLink = "http://" + IP + "/NoGui"

        if jobType == "jobExecutor":
            httpLink = "http://" + IP + actionLink + "?" + parameters

        return httpLink


class WebContentExecutor:
    def __init__(self, httpAddress):
        self.httpAddress = httpAddress
        httpAddress = httpAddress.replace("http://","")
        self.ip = httpAddress.split("/")[0]
        self.addInfo = "/" + httpAddress.split("/")[1]
    
    def execute(self):
        try:
            timestamp = round(time.time())
            print(timestamp)
            response = requests.get(self.httpAddress,timeout=50)
            with app.app_context():
                addInfo = self.addInfo
                deviceId = self.ip
                value = 0
                unit = "OK"
                add_to_archiwe = Archive(timestamp=timestamp,deviceId = deviceId, value= value, unit = unit, addInfo = addInfo)
                db.session.add(add_to_archiwe)
                db.session.commit()


        except requests.exceptions.RequestException:
            print("connection issue")
            with app.app_context():
                addInfo = self.addInfo
                deviceId = self.ip
                value = 0
                unit = "Fail"
                add_to_archiwe = Archive(timestamp=timestamp,deviceId = deviceId, value= value, unit = unit, addInfo = addInfo)
                db.session.add(add_to_archiwe)
                db.session.commit()


class WebContentCollector:

    def __init__(self, httpAddress):
        self.httpAddress = httpAddress
        ip = httpAddress.replace("http://","")
        ip = ip.split("/")[0]
        self.deviceIP = ip
        self.deviceName = ""
        self.deviceRecieveFunctionValues = []
        self.deviceSendFunctionValues = [] 
    
    def collect(self):
        timestamp = round(time.time())
        try:
            print(timestamp)
            
            response = requests.get(self.httpAddress,timeout=5)
            print(response.content)
            response = str(response.content)
            response = response.replace("b'","")
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
                    deviceId = self.deviceIP
                    value = row[4]
                    unit = row[5]
                    add_to_archiwe = Archive(timestamp=timestamp,deviceId = deviceId, value= value, unit = unit, addInfo = addInfo)
                    db.session.add(add_to_archiwe)
                    db.session.commit()

            print()
            print("deviceSendFunctionValues = " + str(self.deviceSendFunctionValues))
            print()

            for row in self.deviceSendFunctionValues:
                print(row)
        except requests.exceptions.Timeout:
            print("connection issue")

