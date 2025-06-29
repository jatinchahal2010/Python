import os
import json
import getpass
import bcrypt
from cryptography.hazmat.primitives.ciphers.aead import AESGCM

VAULT_FILE = "vault.bin"
NONCE_SIZE = 12
MASTER_PASS_COUNT = 5

def hash_password(pw):
    return bcrypt.hashpw(pw.encode(), bcrypt.gensalt())

def check_password(pw, hashed):
    return bcrypt.checkpw(pw.encode(), hashed)

def generate_key(master_passwords):
    # Derive a 32-byte AES key from concatenated master passwords (simple SHA256 here)
    import hashlib
    concat = "".join(master_passwords).encode()
    return hashlib.sha256(concat).digest()

def encrypt(data, key):
    aesgcm = AESGCM(key)
    nonce = os.urandom(NONCE_SIZE)
    ct = aesgcm.encrypt(nonce, data, None)
    return nonce + ct

def decrypt(enc_data, key):
    aesgcm = AESGCM(key)
    nonce = enc_data[:NONCE_SIZE]
    ct = enc_data[NONCE_SIZE:]
    return aesgcm.decrypt(nonce, ct, None)

def create_vault(master_passwords):
    key = generate_key(master_passwords)
    empty_data = json.dumps({"master_hashes": [hash_password(pw).decode() for pw in master_passwords], "vault": {}}).encode()
    encrypted = encrypt(empty_data, key)
    with open(VAULT_FILE, "wb") as f:
        f.write(encrypted)
    print("Vault created and encrypted.")

def load_vault(master_passwords):
    if not os.path.exists(VAULT_FILE):
        print("Vault file not found. Creating new vault.")
        create_vault(master_passwords)
    key = generate_key(master_passwords)
    with open(VAULT_FILE, "rb") as f:
        enc = f.read()
    try:
        dec = decrypt(enc, key)
        data = json.loads(dec)
        # verify master passwords hashes:
        for i, h in enumerate(data["master_hashes"]):
            if not check_password(master_passwords[i], h.encode()):
                raise ValueError("Master password incorrect.")
        return data, key
    except Exception as e:
        print("Failed to unlock vault:", e)
        return None, None

def save_vault(data, key):
    raw = json.dumps(data).encode()
    encrypted = encrypt(raw, key)
    with open(VAULT_FILE, "wb") as f:
        f.write(encrypted)

def input_master_passwords():
    print(f"Enter your {MASTER_PASS_COUNT} master passwords:")
    pwds = []
    for i in range(MASTER_PASS_COUNT):
        pw = getpass.getpass(f"Master password {i+1}: ")
        pwds.append(pw)
    return pwds

def add_entry(data):
    user = input("New username: ").strip()
    if user in data["vault"]:
        print("Username exists.")
        return
    pw = getpass.getpass("Password for this username: ")
    data["vault"][user] = pw
    print("Entry added.")

def edit_entry(data):
    user = input("Username to edit: ").strip()
    if user not in data["vault"]:
        print("Not found.")
        return
    pw = getpass.getpass("New password: ")
    data["vault"][user] = pw
    print("Entry updated.")

def change_master_passwords(data):
    print("Changing master passwords. Enter old passwords first.")
    old_pwds = input_master_passwords()
    # verify old passwords:
    for i, h in enumerate(data["master_hashes"]):
        if not check_password(old_pwds[i], h.encode()):
            print("Old master password incorrect. Abort.")
            return False
    print("Enter new master passwords:")
    new_pwds = input_master_passwords()
    data["master_hashes"] = [hash_password(pw).decode() for pw in new_pwds]
    print("Master passwords updated.")
    return new_pwds

def main():
    if not os.path.exists(VAULT_FILE):
        print("No vault found. Setup your 5 master passwords.")
        master_passwords = input_master_passwords()
        create_vault(master_passwords)
    else:
        master_passwords = input_master_passwords()

    data, key = load_vault(master_passwords)
    if data is None:
        print("Cannot unlock vault. Exiting.")
        return

    while True:
        print("\nOptions:")
        print("1 - Add new username/password")
        print("2 - Edit existing password")
        print("3 - Change master passwords")
        print("4 - List usernames")
        print("5 - View password for username")
        print("6 - Exit")
        choice = input("Choice: ").strip()

        if choice == "1":
            add_entry(data)
        elif choice == "2":
            edit_entry(data)
        elif choice == "3":
            new_pwds = change_master_passwords(data)
            if new_pwds:
                master_passwords = new_pwds
                key = generate_key(master_passwords)
        elif choice == "4":
            print("Usernames:")
            for u in data["vault"]:
                print(" -", u)
        elif choice == "5":
            u = input("Username to view password: ").strip()
            if u in data["vault"]:
                print(f"Password for {u}: {data['vault'][u]}")
            else:
                print("Not found.")
        elif choice == "6":
            save_vault(data, key)
            print("Vault saved. Exiting.")
            break
        else:
            print("Invalid choice.")
        save_vault(data, key)

if __name__ == "__main__":
    main()
