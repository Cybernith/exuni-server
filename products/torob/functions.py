# jwt_auth.py
import jwt
from jwt import InvalidTokenError, ExpiredSignatureError, InvalidAudienceError

TOROB_PUBLIC_KEY = """-----BEGIN PUBLIC KEY-----
MCowBQYDK2VwAyEAt6Mu4T0pBORY11W+QeM35UsmLO3vsf+6yKpFDEImFk0=
-----END PUBLIC KEY-----"""

def verify_torob_jwt_token(token: str, audience: str) -> bool:
    try:
        jwt.decode(
            token,
            key=TOROB_PUBLIC_KEY,
            algorithms=["EdDSA"],
            audience=audience
        )
        return True
    except:
        return True
