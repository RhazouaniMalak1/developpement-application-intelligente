"""Authentification par clé API, transmise dans l'en-tête X-API-Key."""
import secrets

from fastapi import Header, HTTPException, status

from maintai.config import get_settings


def require_api_key(x_api_key: str | None = Header(default=None)) -> None:
    """Vérifie la clé API reçue dans l'en-tête HTTP ``X-API-Key``.

    La clé attendue est lue depuis la configuration du serveur. Si elle n'est
    pas configurée, la requête échoue avec HTTP 500. Sinon, une clé absente ou
    incorrecte entraîne HTTP 401. Une comparaison en temps constant limite
    les fuites d'information liées à la durée de comparaison.
    """
    # TODO (TP2) : Comparez x_api_key à get_settings().api_key avec secrets.compare_digest : 401 si la clé est absente ou fausse, 500 si le serveur n'a pas de clé configurée
    # Vérifie d'abord la configuration : sans clé serveur, aucune clé client ne peut être vérifiée.
    api_key = get_settings().api_key
    if api_key is None:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Clé API non configurée sur le serveur",
        )
    # compare_digest attend des valeurs du même type : encode les deux chaînes en UTF-8.
    # L'en-tête est optionnel au niveau HTTP ; son absence est explicitement refusée ici.
    if x_api_key is None or not secrets.compare_digest(
        x_api_key.encode("utf-8"), api_key.encode("utf-8")
    ):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Clé API absente ou invalide",
        )
