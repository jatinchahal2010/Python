def encrypt(text, key):
    encrypted_text = []
    key_length = len(key)
    
    for i in range(len(text)):
        shift = ord(key[i % key_length])  # Get ASCII value of key character
        encrypted_text.append(chr((ord(text[i]) + shift) % 256))  # Encrypt
    
    return "".join(encrypted_text)  # Return as a string

def decrypt(text, key):
    decrypted_text = []
    key_length = len(key)
    
    for i in range(len(text)):
        shift = ord(key[i % key_length])  # Get ASCII value of key character
        decrypted_text.append(chr((ord(text[i]) - shift) % 256))  # Decrypt
    
    return "".join(decrypted_text)  # Return as a string

def main():
    print("Choose an option:")
    print("1. Encrypt Data")
    print("2. Decrypt Data")
    
    choice = input("Enter choice (1/2): ")
    key = input("Enter a word as a key: ")
    
    if choice == '1':
        text = input("Enter the text to encrypt: ")
        encrypted = encrypt(text, key)
        print("Encrypted Text:", encrypted)  # Display properly
    elif choice == '2':
        encrypted_text = input("Enter the text to decrypt: ")
        decrypted = decrypt(encrypted_text, key)
        print("Decrypted Text:", decrypted)
    else:
        print("Invalid choice!")

if __name__ == "__main__":
    main()
