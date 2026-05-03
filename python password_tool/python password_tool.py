import random
import string

def generate_password(length=12, use_upper=True, use_lower=True, use_digits=True, use_symbols=True):
    characters = ""
    if use_upper:
        characters += string.ascii_uppercase
    if use_lower:
        characters += string.ascii_lowercase
    if use_digits:
        characters += string.digits
    if use_symbols:
        characters += string.punctuation
    
    if not characters:
        return "Error: Select at least one character type"
    
    password = ''.join(random.choice(characters) for _ in range(length))
    return password

def check_strength(password):
    score = 0
    if len(password) >= 12:
        score += 1
    if any(c.isupper() for c in password):
        score += 1
    if any(c.islower() for c in password):
        score += 1
    if any(c.isdigit() for c in password):
        score += 1
    if any(c in string.punctuation for c in password):
        score += 1
    
    if score <= 2:
        return "Weak"
    elif score <= 4:
        return "Medium"
    else:
        return "Strong"

def main():
    print("=== Password Generator & Strength Checker ===\n")
    
    while True:
        print("1. Generate a new password")
        print("2. Check password strength")
        print("3. Exit")
        choice = input("Choose option (1/2/3): ")
        
        if choice == '1':
            try:
                length = int(input("Enter password length (default 12): ") or 12)
                if length < 4:
                    print("Length should be at least 4\n")
                    continue
                password = generate_password(length)
                print(f"\nGenerated Password: {password}")
                print(f"Strength: {check_strength(password)}\n")
            except ValueError:
                print("Invalid input, using length 12\n")
                password = generate_password(12)
                print(f"Generated Password: {password}\n")
        
        elif choice == '2':
            pwd = input("Enter password to check: ")
            print(f"Strength: {check_strength(pwd)}\n")
        
        elif choice == '3':
            print("Goodbye!")
            break
        
        else:
            print("Invalid choice, try again\n")

if __name__ == "__main__":
    main()
