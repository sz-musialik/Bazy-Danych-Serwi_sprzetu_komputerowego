import requests

BASE_URL = "http://localhost:5001"


def create_admin():
    payload = {
        "imie": "Pracownik",
        "nazwisko": "Firmowy",
        "login": "pracownik",
        "password": "pracownik123",
        "rola_id": 3,
        "email": "pracownik@serwis.pl",
        "nr_telefonu": "312345678",
        "czy_aktywny": True,
    }

    try:
        response = requests.post(f"{BASE_URL}/users", json=payload)

        if response.status_code == 201:
            print("Sukces! Utworzono użytkownika 'pracownik'.")
            print("Odpowiedź serwera:", response.json())
        else:
            print(f"Błąd {response.status_code}:")
            print(response.text)

    except requests.exceptions.ConnectionError:
        print("Nie można połączyć się z serwerem.")
        print("Upewnij się, że uruchomiłeś 'python -m backend.app' w innym terminalu.")


if __name__ == "__main__":
    create_admin()
