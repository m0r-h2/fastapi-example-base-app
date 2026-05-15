import pytest


BASE_URL = "/api/v1/departments"


@pytest.mark.asyncio
async def test_create_root_department(client):

    response = await client.post(
        f"{BASE_URL}/",
        json={
            "name": "Backend",
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["name"] == "Backend"
    assert data["parent_id"] is None


@pytest.mark.asyncio
async def test_create_child_department(client):

    parent_response = await client.post(
        f"{BASE_URL}/",
        json={
            "name": "IT",
        },
    )

    parent_id = parent_response.json()["id"]

    response = await client.post(
        f"{BASE_URL}/",
        json={
            "name": "Frontend",
            "parent_id": parent_id,
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["name"] == "Frontend"
    assert data["parent_id"] == parent_id

@pytest.mark.asyncio
async def test_create_department_with_invalid_parent(client):

    response = await client.post(
        f"{BASE_URL}/",
        json={
            "name": "Backend",
            "parent_id": 99999,
        },
    )

    assert response.status_code == 404


@pytest.mark.asyncio
async def test_duplicate_department_name_inside_same_parent(client):

    await client.post(
        f"{BASE_URL}/",
        json={
            "name": "DevOps",
        },
    )

    response = await client.post(
        f"{BASE_URL}/",
        json={
            "name": "DevOps",
        },
    )

    assert response.status_code == 409


@pytest.mark.asyncio
async def test_same_department_name_in_different_parents(client):

    parent_1 = await client.post(
        f"{BASE_URL}/",
        json={
            "name": "Parent 1",
        },
    )

    parent_2 = await client.post(
        f"{BASE_URL}/",
        json={
            "name": "Parent 2",
        },
    )

    parent_1_id = parent_1.json()["id"]
    parent_2_id = parent_2.json()["id"]

    response_1 = await client.post(
        f"{BASE_URL}/",
        json={
            "name": "Backend",
            "parent_id": parent_1_id,
        },
    )

    response_2 = await client.post(
        f"{BASE_URL}/",
        json={
            "name": "Backend",
            "parent_id": parent_2_id,
        },
    )

    assert response_1.status_code == 200
    assert response_2.status_code == 200


@pytest.mark.asyncio
async def test_create_employee(client):

    department = await client.post(
        f"{BASE_URL}/",
        json={
            "name": "QA",
        },
    )

    department_id = department.json()["id"]

    response = await client.post(
        f"{BASE_URL}/{department_id}/employees/",
        json={
            "full_name": "John Doe",
            "position": "QA Engineer",
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["full_name"] == "John Doe"
    assert data["position"] == "QA Engineer"
    assert data["department_id"] == department_id


@pytest.mark.asyncio
async def test_create_employee_in_non_existing_department(client):

    response = await client.post(
        f"{BASE_URL}/99999/employees/",
        json={
            "full_name": "John Doe",
            "position": "Developer",
        },
    )

    assert response.status_code == 404


@pytest.mark.asyncio
async def test_get_department_tree(client):

    root = await client.post(
        f"{BASE_URL}/",
        json={
            "name": "IT",
        },
    )

    root_id = root.json()["id"]

    await client.post(
        f"{BASE_URL}/",
        json={
            "name": "Backend",
            "parent_id": root_id,
        },
    )

    response = await client.get(
        f"{BASE_URL}/{root_id}?depth=2"
    )

    assert response.status_code == 200

    data = response.json()

    assert data["department"]["id"] == root_id
    assert len(data["children"]) == 1



@pytest.mark.asyncio
async def test_get_department_with_employees(client):

    department = await client.post(
        f"{BASE_URL}/",
        json={
            "name": "Analytics",
        },
    )

    department_id = department.json()["id"]

    await client.post(
        f"{BASE_URL}/{department_id}/employees/",
        json={
            "full_name": "Alice",
            "position": "Analyst",
        },
    )

    response = await client.get(
        f"{BASE_URL}/{department_id}?include_employees=true"
    )

    assert response.status_code == 200

    data = response.json()

    assert len(data["employees"]) == 1

@pytest.mark.asyncio
async def test_update_department_name(client):

    department = await client.post(
        f"{BASE_URL}/",
        json={
            "name": "Old Name",
        },
    )

    department_id = department.json()["id"]

    response = await client.patch(
        f"{BASE_URL}/{department_id}",
        json={
            "name": "New Name",
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["name"] == "New Name"


@pytest.mark.asyncio
async def test_move_department(client):

    parent_1 = await client.post(
        f"{BASE_URL}/",
        json={
            "name": "Parent A",
        },
    )

    parent_2 = await client.post(
        f"{BASE_URL}/",
        json={
            "name": "Parent B",
        },
    )
    child = await client.post(
        f"{BASE_URL}/",
        json={
            "name": "Child",
            "parent_id": parent_1.json()["id"],
        },
    )

    child_id = child.json()["id"]

    response = await client.patch(
        f"{BASE_URL}/{child_id}",
        json={
            "parent_id": parent_2.json()["id"],
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["parent_id"] == parent_2.json()["id"]


@pytest.mark.asyncio
async def test_department_cannot_become_itself_parent(client):

    department = await client.post(
        f"{BASE_URL}/",
        json={
            "name": "Self",
        },
    )

    department_id = department.json()["id"]

    response = await client.patch(
        f"{BASE_URL}/{department_id}",
        json={
            "parent_id": department_id,
        },
    )

    assert response.status_code == 409

@pytest.mark.asyncio
async def test_cycle_detection(client):

    root = await client.post(
        f"{BASE_URL}/",
        json={
            "name": "Root",
        },
    )

    root_id = root.json()["id"]

    child = await client.post(
        f"{BASE_URL}/",
        json={
            "name": "Child",
            "parent_id": root_id,
        },
    )

    child_id = child.json()["id"]

    response = await client.patch(
        f"{BASE_URL}/{root_id}",
        json={
            "parent_id": child_id,
        },
    )

    assert response.status_code == 409


@pytest.mark.asyncio
async def test_delete_department_cascade(client):

    department = await client.post(
        f"{BASE_URL}/",
        json={
            "name": "Delete Me",
        },
    )

    department_id = department.json()["id"]

    response = await client.delete(
        f"{BASE_URL}/{department_id}?mode=cascade"
    )

    assert response.status_code == 204

@pytest.mark.asyncio
async def test_delete_department_reassign(client):

    source = await client.post(
        f"{BASE_URL}/",
        json={
            "name": "Source",
        },
    )

    target = await client.post(
        f"{BASE_URL}/",
        json={
            "name": "Target",
        },
    )

    source_id = source.json()["id"]
    target_id = target.json()["id"]

    await client.post(
        f"{BASE_URL}/{source_id}/employees/",
        json={
            "full_name": "John Doe",
            "position": "Developer",
        },
    )

    response = await client.delete(
        f"{BASE_URL}/{source_id}"
        f"?mode=reassign"
        f"&reassign_to_department_id={target_id}"
    )

    assert response.status_code == 204


@pytest.mark.asyncio
async def test_delete_department_with_invalid_mode(client):

    department = await client.post(
        f"{BASE_URL}/",
        json={
            "name": "Test Department",
        },
    )

    department_id = department.json()["id"]

    response = await client.delete(
        f"{BASE_URL}/{department_id}?mode=invalid"
    )

    assert response.status_code == 400