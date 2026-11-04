import pytest

HEADERS = {
    "X-API-Key": "test-key"
}  # la clé des tests (conftest.py) ; inutile en TP1, nécessaire en

VALID = {
    "temperature_c": 60.0,
    "vibration_mm_s": 2.0,
    "load_pct": 50.0,
    "runtime_hours": 5000,
}
CAS_REFUSES = [
    # (description, url, corps, code attendu)
    ("champ manquant", "/v1/predict", "sans_temperature", 422),
    ("valeur absurde", "/v1/predict", {**VALID, "temperature_c": -50}, 422),
    ("texte", "/v1/predict", {**VALID, "temperature_c": "tp"}, 422),
    ("champ en trop", "/v1/predict", {**VALID, "nom": "tp"}, 422),
    ("mauvaise route", "/v1/route-inexistante", VALID, 404),
]


@pytest.mark.parametrize("description, url, corps, attendu", CAS_REFUSES)
def test_requete_refusee(client, description, url, corps, attendu):
    assert client.post(url, json=corps, headers=HEADERS).status_code == attendu
