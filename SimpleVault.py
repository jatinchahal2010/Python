import os
import json
import getpass
import hashlib

VAULT_FILE = "vault.bin"
MASTER_PASS_COUNT = 5
SALT_SIZE = 16

def hash_password(pw, salt=None):
    if not salt:
        salt = os.urandom(SALT_SIZE)
    hashed = hashlib.sha256(salt + pw.encode()).digest()
    return salt.hex() + ":" + hashed.hex()

def check_password(pw, stored):
    salt_hex, hashed_hex = stored.split(":")
    salt = bytes.fromhex(salt_hex)
    hashed = hashlib.sha256(salt + pw.encode()).digest().hex()
    return hashed == hashed_hex

def generate_key(master_passwords):
    combined = "".join(master_passwords).encode()
    return hashlib.sha256(combined).digest()

def xor_encrypt(data: bytes, key: bytes) -> bytes:
    return bytes([b ^ key[i % len(key)] for i, b in enumerate(data)])

def encrypt(data: bytes, key: bytes) -> bytes:
    return xor_encrypt(data, key)

def decrypt(enc_data: bytes, key: bytes) -> bytes:
    return xor_encrypt(enc_data, key)

def create_vault(master_passwords):
    key = generate_key(master_passwords)
    master_hashes = [hash_password(pw) for pw in master_passwords]
    empty_data = json.dumps({"master_hashes": master_hashes, "vault": {}}).encode()
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
        data = json.loads(dec.decode())
        for i, h in enumerate(data["master_hashes"]):
            if not check_password(master_passwords[i], h):
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
    return [getpass.getpass(f"Master password {i+1}: ") for i in range(MASTER_PASS_COUNT)]

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
    for i, h in enumerate(data["master_hashes"]):
        if not check_password(old_pwds[i], h):
            print("Old master password incorrect. Abort.")
            return False
    print("Enter new master passwords:")
    new_pwds = input_master_passwords()
    data["master_hashes"] = [hash_password(pw) for pw in new_pwds]
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
