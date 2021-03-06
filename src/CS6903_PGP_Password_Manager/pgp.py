import requests


def get_key(key_id):
    return requests.get(f"https://keys.openpgp.org/vks/v1/by-keyid/{key_id}").content


def encrypt(gpg_obj, plaintext, key_id, key_server, passphrase):
    import_result = gpg_obj.recv_keys(key_server, key_id)
    encrypted_data = gpg_obj.encrypt(plaintext, key_id, always_trust=True, passphrase=passphrase)

    return encrypted_data


def decrypt(gpg_obj, ciphertext, passphrase):
    decrypted_data = gpg_obj.decrypt(ciphertext, always_trust=True, passphrase=passphrase)

    return decrypted_data
