import requests


class ApiClient:
    def __init__(self, base_url="http://localhost:5001"):
        self.base_url = base_url
        self.token = None
        self.user_data = None

    def login(self, username, password):
        url = f"{self.base_url}/auth/login"
        payload = {"login": username, "password": password}
        try:
            response = requests.post(url, json=payload)
            response.raise_for_status()
            data = response.json()
            self.token = data.get("token")
            self.user_data = data.get("user")
            return True, "Zalogowano pomyślnie"
        except requests.exceptions.HTTPError as e:
            try:
                error_msg = e.response.json().get("error", "Błąd logowania")
            except:
                error_msg = str(e)
            return False, error_msg
        except Exception as e:
            return False, f"Błąd połączenia: {str(e)}"

    def get_auth_headers(self):
        if self.token:
            return {"Authorization": f"Bearer {self.token}"}
        return {}

    def _get(self, path, params=None):
        try:
            r = requests.get(
                f"{self.base_url}{path}", params=params, headers=self.get_auth_headers()
            )
            r.raise_for_status()
            return r.json()
        except Exception:
            return []

    def _post(self, path, json_data):
        try:
            r = requests.post(
                f"{self.base_url}{path}",
                json=json_data,
                headers=self.get_auth_headers(),
            )
            r.raise_for_status()
            return True, r.json()
        except Exception as e:
            error_msg = str(e)
            if hasattr(e, "response") and e.response is not None:
                try:
                    error_msg = e.response.json().get("error", str(e))
                except:
                    pass
            return False, error_msg

    def _put(self, path, json_data):
        try:
            r = requests.put(
                f"{self.base_url}{path}",
                json=json_data,
                headers=self.get_auth_headers(),
            )
            r.raise_for_status()
            return True, ""
        except Exception as e:
            return False, str(e)

    def _patch(self, path, json_data):
        try:
            r = requests.patch(
                f"{self.base_url}{path}",
                json=json_data,
                headers=self.get_auth_headers(),
            )
            r.raise_for_status()
            return True, ""
        except Exception as e:
            return False, str(e)

    def _delete(self, path):
        try:
            r = requests.delete(
                f"{self.base_url}{path}", headers=self.get_auth_headers()
            )
            r.raise_for_status()
            return True, ""
        except Exception as e:
            return False, str(e)

    # Existing methods
    def get_orders(self):
        return self._get("/orders")

    def create_client(self, imie, nazwisko, email, nr_telefonu, adres):
        pass

    def get_clients(self, scope=None):
        return self._get("/clients", params={"scope": scope} if scope else {})

    def get_users(self):
        return self._get("/users")

    def create_user(self, p):
        return self._post("/users", p)

    def update_user(self, uid, p):
        return self._put(f"/users/{uid}", p)

    def update_user_archive(self, uid, arch):
        return self._patch(f"/users/{uid}/archive", {"archived": arch})

    def update_client(self, cid, p):
        return self._put(f"/clients/{cid}", p)

    def create_order(self, p):
        return self._post("/orders", p)

    def update_order_details(self, oid, p):
        return self._put(f"/orders/{oid}", p)

    def update_order_status(self, oid, sid):
        return self._patch(f"/orders/{oid}/status", {"status_zlecenia": sid})

    def get_equipment_types(self):
        return self._get("/dictionaries/equipment-types")

    def get_statuses(self):
        return self._get("/dictionaries/statuses")

    def get_roles(self):
        return self._get("/roles")

    def get_parts(self):
        return self._get("/parts")

    def create_part(self, p):
        return self._post("/parts", p)

    def update_part(self, pid, p):
        return self._put(f"/parts/{pid}", p)

    def get_part_types(self):
        return self._get("/dictionaries/part-types")

    def get_parts_orders(self, user_id=None):
        return self._get(
            "/parts-orders", params={"user_id": user_id} if user_id else {}
        )

    def create_part_order(self, p):
        return self._post("/parts-orders", p)

    def approve_part_order(self, oid):
        return self._post(
            f"/parts-orders/{oid}/approve",
            {"zatwierdzajacy_id": self.user_data.get("id_uzytkownika")},
        )

    def reject_part_order(self, oid):
        return self._post(
            f"/parts-orders/{oid}/reject",
            {"zatwierdzajacy_id": self.user_data.get("id_uzytkownika")},
        )

    def change_part_order_status(self, oid, sn):
        return self._post(
            f"/parts-orders/{oid}/status",
            {
                "status_name": sn,
                "zatwierdzajacy_id": self.user_data.get("id_uzytkownika"),
            },
        )

    def get_order_used_parts(self, order_id):
        """Pobiera liste częsci uzytych w danym zleceniu."""
        return self._get(f"/orders/{order_id}/parts-used")

    def add_order_used_part(self, order_id, part_id, quantity, unit_price):
        """Dodaje zuzytą czesc do zlecenia."""
        payload = {"part_id": part_id, "quantity": quantity, "unit_price": unit_price}
        return self._post(f"/orders/{order_id}/parts-used", payload)

    def delete_order_used_part(self, order_id, used_part_id):
        """Usuwa pozycje zuzytej czesci (przywraca stan magazynowy)."""
        return self._delete(f"/orders/{order_id}/parts-used/{used_part_id}")


api = ApiClient()
