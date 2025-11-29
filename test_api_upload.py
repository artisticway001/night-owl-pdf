import requests
import os

# Create a dummy PDF if it doesn't exist
def create_dummy_pdf():
    try:
        import fitz
        doc = fitz.open()
        page = doc.new_page()
        page.insert_text((50, 50), "Hello World! This is a test PDF.", fontsize=20)
        doc.save("test_upload.pdf")
        doc.close()
        print("Created test_upload.pdf")
    except ImportError:
        print("PyMuPDF not installed, cannot create dummy PDF.")
        return False
    return True

def test_upload():
    if not os.path.exists("test_upload.pdf"):
        if not create_dummy_pdf():
            return

    url = "http://localhost:8000/convert"
    files = {'file': open('test_upload.pdf', 'rb')}
    
    print(f"Sending request to {url}...")
    try:
        response = requests.post(url, files=files)
        print(f"Status Code: {response.status_code}")
        if response.status_code == 200:
            with open("downloaded_dark.pdf", "wb") as f:
                f.write(response.content)
            print("Success! Saved downloaded_dark.pdf")
        else:
            print(f"Error: {response.text}")
    except Exception as e:
        print(f"Exception: {e}")

if __name__ == "__main__":
    test_upload()
