import requests
import time

BASE_URL = "http://127.0.0.1:8000"

def test():
    print("--- TESTING TYPE 1 (Team x Team) ---")
    r1 = requests.get(f"{BASE_URL}/api/game/tictactoe/grid?type=1")
    if r1.status_code == 200:
        grid1 = r1.json()
        print("Generated Type 1 Grid ID:", grid1["grid_id"])
        print("Rows:", [r["name"] for r in grid1["rows"]])
        print("Cols:", [c["name"] for c in grid1["cols"]])
        
        # Test an invalid guess
        guess1 = {
            "grid_id": grid1["grid_id"],
            "row_id": grid1["rows"][0]["id"],
            "col_id": grid1["cols"][0]["id"],
            "guess_id": 999999, # Invalid player
            "type": 1
        }
        res1 = requests.post(f"{BASE_URL}/api/game/tictactoe/guess", json=guess1)
        print("Guess Result (Should be false):", res1.json())
    else:
        print("Failed to generate Type 1 Grid:", r1.text)


    print("\n--- TESTING TYPE 2 (Player x Player) ---")
    r2 = requests.get(f"{BASE_URL}/api/game/tictactoe/grid?type=2")
    if r2.status_code == 200:
        grid2 = r2.json()
        print("Generated Type 2 Grid ID:", grid2["grid_id"])
        print("Rows:", [r["name"] for r in grid2["rows"]])
        print("Cols:", [c["name"] for c in grid2["cols"]])
        
        # Test an invalid guess
        guess2 = {
            "grid_id": grid2["grid_id"],
            "row_id": grid2["rows"][0]["id"],
            "col_id": grid2["cols"][0]["id"],
            "guess_id": 999999, # Invalid team
            "type": 2
        }
        res2 = requests.post(f"{BASE_URL}/api/game/tictactoe/guess", json=guess2)
        print("Guess Result (Should be false):", res2.json())
    else:
        print("Failed to generate Type 2 Grid:", r2.text)

if __name__ == "__main__":
    time.sleep(2)
    test()
