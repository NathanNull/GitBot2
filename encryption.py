from cryptography.fernet import Fernet

def encrypt(token:str) -> tuple[str, str]:
    key = Fernet.generate_key()
    token = bytes(token,"utf-8")

    encrypted = Fernet(key).encrypt(token)

    return key, encrypted

def decrypt(encrypted:str, key:str) -> str:
    key = bytes(key,"utf-8")
    token_bytes = Fernet(key).decrypt(bytes(encrypted,"utf-8"))
    return str(token_bytes)[2:-1]