from fastapi import status


def test_api_health(client):
    test_client = client()
    response = test_client.get("/health")
    assert response.status_code == status.HTTP_200_OK
    assert response.json()["status"] == "Ok"
