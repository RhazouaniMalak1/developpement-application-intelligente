import pytest

HEADERS = {"X-API-Key": "test-key"}  # la clé des tests (conftest.py)
VALID = {
    "temperature_c": 60.0,
    "vibration_mm_s": 2.0,
    "load_pct": 50.0,
    "runtime_hours": 5000,
}

CAS_REFUSES = [
    ("champ manquant", "/v1/predict", {k: v for k, v in VALID.items() if k != "vibration_mm_s"}, 422),
    ("valeur absurde", "/v1/predict", {**VALID, "temperature_c": 500}, 422),
    ("texte au lieu d'un nombre", "/v1/predict", {**VALID, "vibration_mm_s": "imane"}, 422),
    ("champ en trop", "/v1/predict", {**VALID, "weight": 50}, 422),
    ("mauvaise route", "/tp2", VALID, 404),
]


@pytest.mark.parametrize("description, url, corps, attendu", CAS_REFUSES)
def test_requete_refusee(client, description, url, corps, attendu):
    assert client.post(url, json=corps, headers=HEADERS).status_code == attendu