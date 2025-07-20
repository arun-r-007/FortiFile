import os
from cryptography.fernet import Fernet
from cryptography.fernet import InvalidToken

import rsa

def generate_rsa_keys():
    if not os.path.exists('public.pem') or not os.path.exists('private.pem'):
        (public_key, private_key) = rsa.newkeys(2048) 
        with open('public.pem', 'wb') as pub_file:
            pub_file.write(public_key.save_pkcs1(format='PEM'))
        with open('private.pem', 'wb') as priv_file:
            priv_file.write(private_key.save_pkcs1(format='PEM'))
        print("RSA keys generated and saved.")
    else:
        print("RSA keys already exist. Load them using load_rsa_keys().")

def load_rsa_keys():
    try:
        with open('public.pem', 'rb') as pub_file:
            public_key = rsa.PublicKey.load_pkcs1(pub_file.read())
        with open('private.pem', 'rb') as priv_file:
            private_key = rsa.PrivateKey.load_pkcs1(priv_file.read())
        return public_key, private_key
    except FileNotFoundError as e:
        print(f"Error loading keys: {e}")
        raise


public_key, private_key = load_rsa_keys()


def encrypt_file(file_content):
    try:
        symmetric_key = Fernet.generate_key()
        cipher = Fernet(symmetric_key)

        encrypted_data = cipher.encrypt(file_content)

        encrypted_key = rsa.encrypt(symmetric_key, public_key)

        return encrypted_key + b'::' + encrypted_data
    except Exception as e:
        print(f"Error encrypting file: {e}")
        raise
    
def decrypt_file(encrypted_data):
    try:
        encrypted_key, encrypted_file_data = encrypted_data.split(b'::', 1)

        decrypted_key = rsa.decrypt(encrypted_key, private_key)

        cipher = Fernet(decrypted_key)
        decrypted_data = cipher.decrypt(encrypted_file_data)

        return decrypted_data
    except InvalidToken:
        print("Error decrypting file: Invalid token. The data might have been tampered with or corrupted.")
        raise
    except Exception as e:
        print(f"Error decrypting file: {e}")
        raise


if __name__ == '__main__':
    generate_rsa_keys() 
    encrypted_file = encrypt_file('path_to_your_file')  
    print(f"File encrypted: {encrypted_file}")

    decrypted_file = decrypt_file('path_to_your_file.enc')  
    print(f"File decrypted: {decrypted_file}")
