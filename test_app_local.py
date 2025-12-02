
from fastapi.testclient import TestClient
from app import app
import os

client = TestClient(app)

def test_convert_endpoint():
    # Ensure we have a test file
    if not os.path.exists("test_input.pdf"):
        import fitz
        doc = fitz.open()
        page = doc.new_page()
        page.insert_text((50, 50), "Integration Test PDF")
        doc.save("test_input.pdf")
        doc.close()
        
    print("Testing /convert endpoint...")
    with open("test_input.pdf", "rb") as f:
        response = client.post("/convert", files={"file": ("test_input.pdf", f, "application/pdf")})
        
    if response.status_code == 200:
        print("Success! Status code 200")
        with open("integration_test_output.pdf", "wb") as f_out:
            f_out.write(response.content)
        print("Saved integration_test_output.pdf")
        
        # Verify output is a valid PDF
        import fitz
        try:
            doc = fitz.open("integration_test_output.pdf")
            print(f"Output PDF valid. Pages: {len(doc)}")
            doc.close()
        except Exception as e:
            print(f"Output PDF invalid: {e}")
            
    else:
        print(f"Failed: {response.status_code}")
        print(response.text)

if __name__ == "__main__":
    test_convert_endpoint()
