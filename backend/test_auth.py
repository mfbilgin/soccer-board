import requests
import time

BASE_URL = "http://127.0.0.1:8000"

def test():
    print("Testing Registration...")
    reg_data = {
        "username": "player1",
        "email": "player1@example.com",
        "password": "supersecretpassword123"
    }
    r = requests.post(f"{BASE_URL}/api/auth/register", json=reg_data)
    print("Register Status:", r.status_code)
    try:
        print("Register Response:", r.json())
    except:
        pass
    
    # Eğer daha önce eklenmişse 400 döner, sorun değil.

    print("\nTesting Login...")
    login_data = {
        "username": "player1",
        "password": "supersecretpassword123"
    }
    # OAuth2 beklediği için form-data olarak gönderiyoruz
    r = requests.post(f"{BASE_URL}/api/auth/login", data=login_data)
    print("Login Status:", r.status_code)
    try:
        token = r.json().get("access_token")
        print("Login Token Received")
    except:
        token = None

    if token:
        print("\nTesting /me (Protected Route)...")
        headers = {"Authorization": f"Bearer {token}"}
        r = requests.get(f"{BASE_URL}/api/auth/me", headers=headers)
        print("Me Status:", r.status_code)
        try:
            print("Me Response:", r.json())
        except:
            pass

if __name__ == "__main__":
    time.sleep(2) # Sunucunun tam açılmasını bekle
    test()
