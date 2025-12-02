
import subprocess
import time
import requests
import os
import sys
import signal

def run_test():
    # Start the server
    print("Starting server...")
    server_process = subprocess.Popen(
        [sys.executable, "-m", "uvicorn", "app:app", "--port", "8000"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )
    
    try:
        # Wait for server to start
        url = "http://localhost:8000"
        server_ready = False
        for i in range(10):
            try:
                requests.get(f"{url}/health")
                server_ready = True
                print("Server is ready!")
                break
            except:
                time.sleep(1)
                print(f"Waiting for server... ({i+1}/10)")
        
        if not server_ready:
            print("Server failed to start.")
            stdout, stderr = server_process.communicate()
            print("Server Output:", stdout.decode())
            print("Server Error:", stderr.decode())
            return

        # Run the test
        print("Running conversion test...")
        input_file = "test_input.pdf"
        if not os.path.exists(input_file):
            # Create dummy pdf
            import fitz
            doc = fitz.open()
            page = doc.new_page()
            page.insert_text((50, 50), "Integration Test")
            doc.save(input_file)
            doc.close()

        with open(input_file, "rb") as f:
            response = requests.post(f"{url}/convert", files={"file": f})
            
        if response.status_code == 200:
            print("Success! Conversion returned 200 OK")
            with open("integration_output.pdf", "wb") as f_out:
                f_out.write(response.content)
            print("Saved integration_output.pdf")
        else:
            print(f"Test Failed: {response.status_code}")
            print(response.text)
            
    finally:
        # Kill server
        print("Stopping server...")
        server_process.terminate()
        try:
            server_process.wait(timeout=5)
        except:
            server_process.kill()

if __name__ == "__main__":
    run_test()
