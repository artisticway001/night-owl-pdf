
import fitz

def check_pdf_background(path):
    doc = fitz.open(path)
    page = doc[0]
    
    # Check for drawings (rectangles)
    drawings = page.get_drawings()
    print(f"Total drawings: {len(drawings)}")
    
    black_rects = []
    for d in drawings:
        if d['fill'] == (0, 0, 0):
            black_rects.append(d)
            
    print(f"Black filled rects: {len(black_rects)}")
    if black_rects:
        print("First black rect:", black_rects[0])
        
    # Check text color
    text_dict = page.get_text("dict")
    blocks = text_dict["blocks"]
    white_text_count = 0
    total_spans = 0
    
    for block in blocks:
        if block["type"] == 0:
            for line in block["lines"]:
                for span in line["spans"]:
                    total_spans += 1
                    # color is an integer in sRGB
                    # White is 16777215 (0xFFFFFF) or sometimes (1,1,1) depending on normalization
                    # PyMuPDF dict usually returns sRGB int
                    if span["color"] == 16777215 or span["color"] == 0xFFFFFF:
                        white_text_count += 1
                        
    print(f"Total text spans: {total_spans}")
    print(f"White text spans: {white_text_count}")

if __name__ == "__main__":
    import os
    if os.path.exists("test_output.pdf"):
        print("Checking test_output.pdf...")
        check_pdf_background("test_output.pdf")
    else:
        print("test_output.pdf not found")
