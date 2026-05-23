def test_create_employee(client, seeded_db):
    r = client.post(
        "/employees/",
        json={"full_name": "Eve", "position": "Designer", "department_id": seeded_db["it"]},
    )
    assert r.status_code == 201
    data = r.json()
    assert data["full_name"] == "Eve"
    assert data["position"] == "Designer"
    assert data["department_id"] == seeded_db["it"]


def test_create_employee_invalid_department(client):
    r = client.post(
        "/employees/",
        json={"full_name": "Ghost", "position": "Dev", "department_id": 999},
    )
    assert r.status_code == 400


def test_list_employees(client, seeded_db):
    r = client.get("/employees/")
    assert r.status_code == 200
    data = r.json()
    assert len(data) == 4


def test_list_employees_filter_by_department(client, seeded_db):
    r = client.get(f"/employees/?department_id={seeded_db['it']}")
    assert r.status_code == 200
    data = r.json()
    names = {e["full_name"] for e in data}
    assert names == {"Bob"}


def test_get_employee(client, seeded_db):
    r = client.get("/employees/")
    emp_id = r.json()[0]["id"]
    r = client.get(f"/employees/{emp_id}")
    assert r.status_code == 200


def test_get_employee_404(client):
    r = client.get("/employees/999")
    assert r.status_code == 404


def test_update_employee(client, seeded_db):
    r = client.get("/employees/")
    emp_id = r.json()[0]["id"]
    r = client.put(
        f"/employees/{emp_id}",
        json={"full_name": "Updated"},
    )
    assert r.status_code == 200
    assert r.json()["full_name"] == "Updated"


def test_delete_employee(client, seeded_db):
    r = client.get("/employees/")
    emp_id = r.json()[0]["id"]
    r = client.delete(f"/employees/{emp_id}")
    assert r.status_code == 204
