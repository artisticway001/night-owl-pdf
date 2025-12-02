
import fitz

def check_boxes():
    # Create a dummy PDF
    doc = fitz.open()
    page = doc.new_page()
    
    print(f"Initial MediaBox: {page.mediabox}")
    print(f"Initial CropBox:  {page.cropbox}")
    
    # Expand MediaBox
    page.set_mediabox(fitz.Rect(0, 0, 1000, 1000))
    
    print(f"After set_mediabox:")
    print(f"MediaBox: {page.mediabox}")
    print(f"CropBox:  {page.cropbox}")
    
    if page.cropbox != page.mediabox:
        print("ALERT: CropBox did not update automatically!")
    else:
        print("CropBox updated automatically.")
        
    doc.close()

if __name__ == "__main__":
    check_boxes()
