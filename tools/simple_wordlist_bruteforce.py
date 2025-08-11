def fake_login(password: str) -> bool:
        correct_password = "password123"
        return password.strip() == correct_password

tries = 0
with open("wordlist.txt") as f:
        for pwd in f:
            tries += 1
            if fake_login(pwd):
                print(f"[+] Password found after {tries} attempts: {pwd.strip()}")
                break
            else:
                print(f"[-] Tried: {pwd.strip()} - Failed")
        else:
            print("[!] No password matched.")