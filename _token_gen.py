from ast import Bytes
from cryptography.fernet import Fernet

key = Fernet.generate_key()
token = Bytes(input("Enter the token to encrypt:\n"))

encrypted = Fernet(key).encrypt(token)

print(key, "\n", encrypted)