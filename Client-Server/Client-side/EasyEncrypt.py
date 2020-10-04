from config import ENCRYPTION_KEY


def encrypt(s: str):
    crypt = ''
    for i in s:
        crypt += chr(ord(i) ^ ENCRYPTION_KEY)
    s = crypt

    return s

def encrypt_json(d: dict):
    for key, value in d.items():
        d[key] = encrypt(value)
    return d
