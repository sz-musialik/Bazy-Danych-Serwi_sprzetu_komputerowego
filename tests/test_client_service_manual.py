from backend.services.client_service import ClientService

def test_create_client():
    client_id = ClientService.create_client(
        nazwa="Jan Kowalski",
        email="jan@test.pl"
    )
    assert isinstance(client_id, int)
    print("OK, client_id =", client_id)

if __name__ == "__main__":
    test_create_client()
