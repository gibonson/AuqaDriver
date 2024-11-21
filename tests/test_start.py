from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.select import Select
import time

testDelay = 3

# Inicjalizacja przeglądarki Firefox
driver = webdriver.Firefox()

# Otwórz stronę, na której znajduje się przycisk (zmień URL na właściwy)
driver.get("http://127.0.0.1:5000/device_list")

# Poczekaj chwilę na załadowanie strony
time.sleep(testDelay)

# Znajdź przycisk po jego klasie (można też dodać więcej specyfikacji, jeśli potrzebne)
add_device_button = driver.find_element(By.XPATH, "//button[normalize-space(text())='Add device']")

# Kliknij przycisk
add_device_button.click()

# Opcjonalnie: dalsze akcje po kliknięciu przycisku, np. weryfikacja, że formularz się rozwinął
# Sprawdź, czy formularz o ID "form" jest widoczny
form = driver.find_element(By.ID, "form")
assert form.is_displayed()

elem = driver.find_element(By.NAME, 'deviceName')  # Find the search box
elem.send_keys('seleniumhq' + Keys.RETURN)


elem = driver.find_element(By.NAME, 'deviceIP')  # Find the search box
elem.send_keys('192.168.192.192')

elem = driver.find_element(By.NAME, 'deviceStatus')  # Find the search box
elem.send_keys('seleniumhq')

select = Select(elem)
select.select_by_visible_text("Old")

submit_button = driver.find_element(by=By.ID, value="submit")
submit_button.click()

driver.get("http://127.0.0.1:5000/event_list")
time.sleep(testDelay)
driver.get("http://127.0.0.1:5000/scheduler_list")
time.sleep(testDelay)
driver.get("http://127.0.0.1:5000/report_list")
time.sleep(testDelay)
driver.get("http://127.0.0.1:5000/notification_list")
time.sleep(testDelay)
driver.get("http://127.0.0.1:5000/get_jobs")
time.sleep(testDelay)
driver.get("http://127.0.0.1:5000/get_jobs_and_scheduler")
time.sleep(testDelay)
driver.get("http://127.0.0.1:5000/archive_search")
time.sleep(testDelay)
driver.get("http://127.0.0.1:5000/emailSend")
time.sleep(testDelay)
driver.get("http://127.0.0.1:5000/get_dashboard")
time.sleep(testDelay)
driver.get("http://127.0.0.1:5000/get_report_all")
time.sleep(testDelay)
driver.get("http://127.0.0.1:5000/charts")
time.sleep(testDelay)
driver.get("http://127.0.0.1:5000/archive_add_manually")
time.sleep(testDelay)
driver.get("http://127.0.0.1:5000/ignore_list")
time.sleep(testDelay)





# Zamknij przeglądarkę
# driver.quit()