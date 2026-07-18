import time
import requests

def test_batch():
    print("Sending batch prediction request for ['Si', 'GaAs', 'NaCl']...")
    response = requests.post(
        "http://localhost:8000/api/v1/predict/batch",
        json={"formulas": ["Si", "GaAs", "NaCl"]}
    )
    
    if response.status_code != 200:
        print(f"Error: {response.status_code} - {response.text}")
        return
        
    data = response.json()
    task_ids = data.get("task_ids", [])
    print(f"Received {len(task_ids)} task IDs.")
    
    completed = 0
    total = len(task_ids)
    
    while completed < total:
        time.sleep(2)
        completed = 0
        for tid in task_ids:
            status_res = requests.get(f"http://localhost:8000/api/v1/predict/status/{tid}")
            if status_res.status_code == 200:
                s_data = status_res.json()
                if s_data["status"] in ["SUCCESS", "FAILURE"]:
                    completed += 1
                    if s_data["status"] == "SUCCESS":
                        print(f"Task {tid}: {s_data['result']['formula']} -> {s_data['result']['predicted_band_gap_ev']} eV")
                    else:
                        print(f"Task {tid}: FAILED - {s_data.get('error')}")
            else:
                print(f"Error checking status for {tid}: {status_res.status_code}")
                
    print("Batch prediction test complete!")

if __name__ == "__main__":
    test_batch()
