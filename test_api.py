import requests
import os
import time

def test_api():
    url = "http://localhost:8000/convert"
    input_file = "test_input.pdf"
    output_file = "api_test_output.pdf"
    
    if not os.path.exists(input_file):
        print(f"Error: {input_file} not found.")
        return

    # Wait for server to start
    print("Waiting for server...")
    for _ in range(10):
        try:
            requests.get("http://localhost:8000/")
            break
        except requests.exceptions.ConnectionError:
            time.sleep(1)
    else:
        print("Server failed to start.")
        return

    print(f"Sending {input_file} to {url}...")
    with open(input_file, "rb") as f:
        files = {"file": f}
        response = requests.post(url, files=files)
    
    if response.status_code == 200:
        with open(output_file, "wb") as f:
            f.write(response.content)
        print(f"Success! Saved response to {output_file}")
    else:
        print(f"Failed: {response.status_code} - {response.text}")

if __name__ == "__main__":
    test_api()
