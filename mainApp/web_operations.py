import requests
import re
from datetime import datetime
from mainApp.models.event import Event
from mainApp.models.device import Device
from mainApp.response_operation import ResponseTrigger
from mainApp.dashboard_data import DashboardData
from mainApp import app, logger

class LinkCreator:
    def __init__(self, id, eventLink = None):
        self.id = id
        self.eventLink = eventLink

    def extract_placeholders(eventLink):
        """zwraca w formie tabel 
        nazwy wszystkich zmiennych w linku
        znajdujących sie w <<>>"""
        pattern = r"<<(.*?)>>"  # Wzorzec do znajdowania tekstu w <<>>
        return re.findall(pattern, eventLink)
    
    def functions_api_link_creator(self):
        """
        Tworzy link do API funkcji na podstawie ID zdarzenia.

        Returns:
            str: Link do API funkcji.
        """
        event = Event.query.get(self.id)
        eventLink = event.eventLink
        httpLink = eventLink
        return httpLink

    def functions_list_link_creator(self):
        event = Event.query.get(self.id)
        device = Device.query.get(event.deviceId)
        IP = device.deviceIP
        eventLink = event.eventLink


        placeholders = LinkCreator.extract_placeholders(eventLink)
        resolver = PlaceholderGetter(placeholders)
        received_values = resolver.vlue_getter()

        print(received_values)
        print(placeholders)
        eventLink = self.inject_values_into_link(eventLink, received_values)
        httpLink = "http://" + IP + eventLink
        return httpLink



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
        return {placeholder: self.dashboard_data.get_placeholder_value(placeholder) for placeholder in self.placeholders}

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