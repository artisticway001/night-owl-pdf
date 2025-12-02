
from converter import PDFDarkThemeConverter
import os

def test_converter():
    converter = PDFDarkThemeConverter()
    
    # Create a dummy input if not exists
    if not os.path.exists("test_input.pdf"):
        import fitz
        doc = fitz.open()
        page = doc.new_page()
        page.draw_rect(page.rect, fill=(1, 1, 1)) # White BG
        page.insert_text((100, 100), "Test Text", color=(0, 0, 0))
        doc.save("test_input.pdf")
        doc.close()
        
    try:
        converter.convert("test_input.pdf", "test_output_v2.pdf")
        print("Conversion complete: test_output_v2.pdf")
    except Exception as e:
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_converter()
