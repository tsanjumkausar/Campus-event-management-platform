from app import create_app
def test_health():
    app = create_app("sqlite:///:memory:")
    client = app.test_client()
    assert client.get("/health").status_code == 200
