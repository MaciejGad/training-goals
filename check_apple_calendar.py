from caldav import DAVClient
import json
import os
import csv
import argparse
from datetime import datetime, date, timedelta

# Konfiguracja argumentów wiersza poleceń
parser = argparse.ArgumentParser(description="Pobiera wydarzenia 'Trening' z kalendarza 'Home' i aktualizuje 2k25.csv.")
parser.add_argument("--credentials", type=str, default="credentials.json", help="Ścieżka do pliku credentials.json (domyślnie: credentials.json)")
parser.add_argument("--csv", type=str, default="2k25.csv", help="Ścieżka do pliku csv z danymi (domyślnie: 2k25.csv)")

args = parser.parse_args()

# Ścieżki do plików
csv_file_path = args.csv
credentials_file_path = args.credentials 

# Sprawdź, czy plik credentials.json istnieje
if not os.path.exists(credentials_file_path):
    print(f"❌ Błąd: Plik {credentials_file_path} nie istnieje. Utwórz go w formacie: {{\"username\": \"twój_email\", \"password\": \"twoje_hasło\"}}")
    exit(1)

# Wczytaj Apple ID i hasło z pliku credentials.json
try:
    with open(credentials_file_path, "r") as cred_file:
        credentials = json.load(cred_file)
        username = credentials.get("username")
        password = credentials.get("password")

        if not username or not password:
            raise ValueError("Brak wymaganych danych w credentials.json")
except Exception as e:
    print(f"❌ Błąd podczas odczytu credentials.json: {e}")
    exit(1)

# Pobierz dzisiejszą datę
today = date.today()
today_str = today.strftime("%Y-%m-%d")

# Sprawdź, czy dzisiejsza data już istnieje w pliku CSV
if os.path.exists(csv_file_path):
    with open(csv_file_path, mode="r", newline="") as file:
        reader = csv.reader(file)
        rows = list(reader)
        if len(rows) > 0:  # Jeśli są jakieś wpisy
            last_row = rows[-1]
            if last_row[0] == today_str: # Sprawdzenie pierwszej kolumny
                print("ℹ️ Dzisiejsza data już istnieje w 2k25.csv. Przerywam działanie skryptu.")
                exit(0) 

# Połączenie z iCloud CalDAV
url = "https://caldav.icloud.com/"
client = DAVClient(url, username=username, password=password)
principal = client.principal()
calendars = principal.calendars()

# Zakres czasu dla dzisiejszych wydarzeń
today_start = datetime.combine(today, datetime.min.time())  # 00:00:00
today_end = datetime.combine(today, datetime.max.time())  # 23:59:59

# Zmienna oznaczająca, czy znaleziono wydarzenie "Trening"
training_found = False

# Filtruj tylko kalendarz "Home"
home_calendar = next((cal for cal in calendars if cal.name.lower() == "home"), None)

if not home_calendar:
    print("❌ Błąd: Nie znaleziono kalendarza 'Home'. Sprawdź jego nazwę w aplikacji Kalendarz.")
    exit(1)

# Pobierz wydarzenia tylko z kalendarza "Home"
events = home_calendar.date_search(start=today_start, end=today_end)
for event in events:
    vevent = event.icalendar_instance
    for component in vevent.walk():
        if component.name == "VEVENT":
            event_title = component.get("SUMMARY")

            # Jeśli znajdziemy wydarzenie zawierające "Trening", ustaw flagę na True i zakończ szukanie
            if event_title and "trening" in event_title.lower():
                training_found = True
                break  # Nie ma potrzeby dalszego przeszukiwania

    if training_found:
        break  # Jeśli znaleźliśmy "Trening", nie sprawdzamy kolejnych wydarzeń

# Jeśli znaleziono wydarzenie "Trening", aktualizujemy plik CSV

try:
    # Sprawdź, czy plik istnieje i odczytaj ostatnią wartość
    last_value = 0
    if os.path.exists(csv_file_path):
        with open(csv_file_path, mode="r", newline="") as file:
            reader = csv.reader(file)
            rows = list(reader)

            if len(rows) > 0:  # Jeśli są jakieś wpisy
                last_row = rows[-1]  # Pobierz ostatni wiersz
                try:
                    last_value = int(last_row[1])  # Pobierz wartość z drugiej kolumny
                except ValueError:
                    print("⚠️ Ostrzeżenie: Niepoprawna wartość w pliku CSV. Ustawiono wartość 0.")

    # Zwiększ wartość o 1 i zapisz nowy wpis
    if training_found:
        new_value = last_value + 1
    else:
        new_value = last_value
    with open(csv_file_path, mode="a", newline="") as file:
        writer = csv.writer(file)
        writer.writerow([today_str, new_value])

    print(f"✅ Zapisano trening nr {new_value} w dniu {today_str}. Zaktualizowano plik 2k25.csv")

except Exception as e:
    print(f"❌ Błąd podczas przetwarzania pliku CSV: {e}")