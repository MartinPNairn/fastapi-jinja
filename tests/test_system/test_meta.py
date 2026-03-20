from fastapi import status


def test_root(client):
    test_client = client()
    response = test_client.get("/health")
    assert response.status_code == status.HTTP_200_OK

