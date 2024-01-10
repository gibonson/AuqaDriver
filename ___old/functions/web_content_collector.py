from functions import requests
from functions import time

class WebContentCollector:

    def __init__(self, deviceIP, deviceName):
        self.deviceIP = deviceIP
        self.deviceName = deviceName
        self.deviceRecieveFunctionValues = []
        self.deviceSendFunctionValues = [] 
    
    def collect(self):
        try:
            timestamp = round(time.time())
            print(timestamp)

            response = requests.get("http://" + self.deviceIP + "/NoGui",timeout=5)
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
                print(row)

            print()
            print("deviceSendFunctionValues = " + str(self.deviceSendFunctionValues))
            print()

            for row in self.deviceSendFunctionValues:
                print(row)
        except requests.exceptions.Timeout:
            print("cos sie zesralo")