from cryptography.fernet import Fernet

key = Fernet.generate_key()
token = bytes(input("Enter the token to encrypt:\n"),"utf-8")

encrypted = Fernet(key).encrypt(token)

print(key, "\n", encrypted)