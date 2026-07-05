import requests


def test_ollama_ping():
    base_url = "http://localhost:11434"

    try:
        response = requests.get(f"{base_url}/api/version", timeout=2)
        is_success = response.status_code == 200
        response_data = response.json()
    except Exception as error:
        is_success = False
        response_data = str(error)

    assert is_success is True
    assert isinstance(response_data, dict)
    assert "version" in response_data


"""
def test_ollama_can_generate():
    response = requests.post(
        "http://localhost:11434/api/generate",
        json={
            "model": "gemma4:e2b",
            "prompt": "Hello",
            "stream": False,
        },
        timeout=200,
    )

    assert response.status_code == 200
    assert "response" in response.json()
"""
