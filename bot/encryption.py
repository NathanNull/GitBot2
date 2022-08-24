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

if __name__ == "__main__":
    if input("Decrypt? ")[0].lower() == "y":
        e = input("Enter token to decrypt: ")
        k = input("Enter key to use: ")
        print(f"Decrypted: {decrypt(e, k)}")
    else:
        k, e = encrypt(input("Enter token to encrypt: "))
        print(f"Key: {k}")
        print(f"Encrypted: {e}")