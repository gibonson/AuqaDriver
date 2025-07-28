import requests
import re
import json
from datetime import datetime
from mainApp.models.event import Event
from mainApp.models.device import Device
from mainApp.response_operation import ResponseTrigger
from mainApp.dashboard_data import DashboardData
from mainApp import app, logger


class WebContentCollector:
    def __init__(self, id, requestID="A"):
        self.id = id
        self.requestID = requestID + str(int(datetime.now().timestamp()))

    def collector(self):
        with app.app_context():
            event = Event.query.get(self.id)
            if event is None:
                print("Event not found")
                response = requests.get(httpLink, timeout=5)
            elif event.deviceId == 0:
                httpLink = event.eventLink
                print("httpLink: " + httpLink)
                try:
                    response = requests.get(httpLink, timeout=5)
                    jsonResponse = response.json()
                    print("response: " + str(response.content))
                    requestData = {
                        "requestID": self.requestID,
                        "addInfo": jsonResponse["stacja"] + " temperatura",
                        "deviceIP": "danepubliczne",
                        "deviceName": "API IMGW",
                        "type": "°C",
                        "value": jsonResponse["temperatura"],
                    }
                    ResponseTrigger(requestData)
                    requestData = {
                        "requestID": self.requestID,
                        "addInfo": jsonResponse["stacja"] + " predkosc wiatru",
                        "deviceIP": "danepubliczne",
                        "deviceName": "API IMGW",
                        "type": "km/h",
                        "value": jsonResponse["predkosc_wiatru"],
                    }
                    ResponseTrigger(requestData)
                    requestData = {
                        "requestID": self.requestID,
                        "addInfo": jsonResponse["stacja"] + " kierunek wiatru",
                        "deviceIP": "danepubliczne",
                        "deviceName": "API IMGW",
                        "type": "°",
                        "value": jsonResponse["kierunek_wiatru"],
                    }
                    ResponseTrigger(requestData)
                    requestData = {
                        "requestID": self.requestID,
                        "addInfo": jsonResponse["stacja"] + " wilgotnosc",
                        "deviceIP": "danepubliczne",
                        "deviceName": "API IMGW",
                        "type": "%",
                        "value": jsonResponse["wilgotnosc_wzgledna"],
                    }
                    ResponseTrigger(requestData)
                    requestData = {
                        "requestID": self.requestID,
                        "addInfo": jsonResponse["stacja"] + " opad",
                        "deviceIP": "danepubliczne",
                        "deviceName": "API IMGW",
                        "type": "mm",
                        "value": jsonResponse["suma_opadu"],
                    }
                    ResponseTrigger(requestData)
                    requestData = {
                        "requestID": self.requestID,
                        "addInfo": jsonResponse["stacja"] + " cisnienie",
                        "deviceIP": "danepubliczne",
                        "deviceName": "API IMGW",
                        "type": "hPa",
                        "value": jsonResponse["cisnienie"],
                    }
                    ResponseTrigger(requestData)
                except requests.exceptions.Timeout:

                    logger.error(f"Timeout error while trying to reach {httpLink}")
                    # return {"error": "Connection timeout"}
                except requests.exceptions.RequestException as e:

                    logger.error(f"Request error: {e} while trying to reach {httpLink}")
                    # return {"error": "Connection error"}

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
