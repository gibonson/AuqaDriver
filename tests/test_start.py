from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import time


# Inicjalizacja przeglądarki Firefox
driver = webdriver.Firefox()

# Otwórz stronę, na której znajduje się przycisk (zmień URL na właściwy)
driver.get("http://127.0.0.1:5000/device_list")

# Poczekaj chwilę na załadowanie strony
time.sleep(3)

# Znajdź przycisk po jego klasie (można też dodać więcej specyfikacji, jeśli potrzebne)
add_device_button = driver.find_element(By.XPATH, "//button[normalize-space(text())='Add device']")

# Kliknij przycisk
add_device_button.click()



# Opcjonalnie: dalsze akcje po kliknięciu przycisku, np. weryfikacja, że formularz się rozwinął
# Sprawdź, czy formularz o ID "form" jest widoczny
form = driver.find_element(By.ID, "form1")
assert form.is_displayed()

# Zamknij przeglądarkę
driver.quit()