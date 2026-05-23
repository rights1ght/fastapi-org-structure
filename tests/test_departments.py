def test_cascade_deletes_everything(client, seeded_db):
    client.delete(f"/departments/{seeded_db['root']}?mode=cascade")
    assert client.get("/departments/").json() == []
    assert client.get("/employees/").json() == []


def test_reassign_parent_promotes_children(client, seeded_db):
    r = client.get("/departments/")
    depts_before = {d["id"]: d for d in r.json()}
    it_parent_before = depts_before[seeded_db["it"]]["parent_id"]
    assert it_parent_before == seeded_db["root"]

    client.delete(f"/departments/{seeded_db['root']}?mode=reassign_parent")

    r = client.get("/departments/")
    remaining = r.json()
    assert len(remaining) == 4
    assert seeded_db["root"] not in [d["id"] for d in remaining]

    for d in remaining:
        if d["id"] in (seeded_db["it"], seeded_db["hr"]):
            assert d["parent_id"] is None, f"{d['name']} should be root now"

    r = client.get("/employees/")
    emps = r.json()
    assert len(emps) == 4
    for emp in emps:
        assert emp["department_id"] != seeded_db["root"]


def test_reassign_another_moves_to_target(client, seeded_db):
    client.delete(
        f"/departments/{seeded_db['it']}?mode=reassign_another&target_id={seeded_db['hr']}"
    )

    r = client.get("/departments/")
    remaining = r.json()
    assert seeded_db["it"] not in [d["id"] for d in remaining]

    children_of_hr = [d for d in remaining if d["parent_id"] == seeded_db["hr"]]
    children_names = {d["name"] for d in children_of_hr}
    assert children_names == {"Backend", "Frontend"}

    r = client.get("/employees/")
    for emp in r.json():
        if emp["full_name"] == "Bob":
            assert emp["department_id"] == seeded_db["hr"]


def test_reassign_another_requires_target_id(client, seeded_db):
    r = client.delete(f"/departments/{seeded_db['it']}?mode=reassign_another")
    assert r.status_code == 400


def test_reassign_delete_children_removes_subtree(client, seeded_db):
    client.delete(f"/departments/{seeded_db['it']}?mode=reassign_delete_children")

    r = client.get("/departments/")
    remaining_ids = {d["id"] for d in r.json()}
    assert seeded_db["it"] not in remaining_ids
    assert seeded_db["backend"] not in remaining_ids
    assert seeded_db["root"] in remaining_ids
    assert seeded_db["hr"] in remaining_ids

    r = client.get("/employees/")
    emp_names = {e["full_name"] for e in r.json()}
    assert "Bob" in emp_names
    assert "Charlie" not in emp_names
    assert "Alice" in emp_names
    assert "Diana" in emp_names

    bob = [e for e in r.json() if e["full_name"] == "Bob"][0]
    assert bob["department_id"] == seeded_db["root"]


def test_404_on_nonexistent(client):
    r = client.delete("/departments/999?mode=cascade")
    assert r.status_code == 404
