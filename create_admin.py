import requests

BASE_URL = "http://localhost:5001"


def create_admin():
    payload = {
        "imie": "Admin",
        "nazwisko": "Systemowy",
        "login": "admin",
        "password": "admin123",
        "rola_id": 1,
        "email": "admin@serwis.pl",
        "nr_telefonu": "123456789",
        "czy_aktywny": True,
    }

    try:
        response = requests.post(f"{BASE_URL}/users", json=payload)

        if response.status_code == 201:
            print("Sukces! Utworzono użytkownika 'admin'.")
            print("Odpowiedź serwera:", response.json())
        else:
            print(f"Błąd {response.status_code}:")
            print(response.text)

    except requests.exceptions.ConnectionError:
        print("Nie można połączyć się z serwerem.")
        print("Upewnij się, że uruchomiłeś 'python -m backend.app' w innym terminalu.")


if __name__ == "__main__":
    create_admin()
