
import fitz
from converter import PDFDarkThemeConverter
import os

def create_oob_pdf():
    doc = fitz.open()
    page = doc.new_page() # Default A4 (595 x 842)
    
    print(f"Original page size: {page.rect}")
    
    # Draw text inside bounds
    page.insert_text((50, 50), "Inside Bounds", color=(0, 0, 0))
    
    # Draw text WAY outside bounds (at x=700)
    # Note: insert_text might not show it if we view it, but the object exists
    page.insert_text((700, 100), "I AM OUTSIDE THE PAGE!", color=(0, 0, 0))
    
    doc.save("test_expand_input.pdf")
    
    # Debug: Check if get_text sees it
    page = doc[0]
    text = page.get_text("dict")
    print("Blocks found:", len(text["blocks"]))
    for b in text["blocks"]:
        if b["type"] == 0:
            for l in b["lines"]:
                for s in l["spans"]:
                    print(f"Span: '{s['text']}' at {s['bbox']}")
    
    doc.close()

def test_expansion():
    converter = PDFDarkThemeConverter()
    converter.convert("test_expand_input.pdf", "test_expand_output.pdf")
    
    # Check output size
    doc = fitz.open("test_expand_output.pdf")
    page = doc[0]
    print(f"New page size: {page.rect}")
    
    if page.rect.width > 600:
        print("SUCCESS: Page expanded!")
    else:
        print("FAILURE: Page did not expand.")
    doc.close()

if __name__ == "__main__":
    create_oob_pdf()
    test_expansion()
