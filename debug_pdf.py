import fitz

def analyze_pdf(path):
    doc = fitz.open(path)
    page = doc[0]
    
    print(f"Page rect: {page.rect}")
    print(f"Page width: {page.rect.width}, height: {page.rect.height}")
    
    # Check text positions
    text_dict = page.get_text("dict")
    blocks = text_dict["blocks"]
    
    out_of_bounds = []
    total_spans = 0
    
    for block in blocks:
        if block["type"] == 0:
            for line in block["lines"]:
                for span in line["spans"]:
                    total_spans += 1
                    origin = span["origin"]
                    bbox = span["bbox"]
                    
                    # Check if text extends beyond page
                    if bbox[2] > page.rect.width or bbox[3] > page.rect.height:
                        out_of_bounds.append({
                            'text': span['text'][:30],
                            'bbox': bbox,
                            'origin': origin
                        })
    
    print(f"\nTotal spans: {total_spans}")
    print(f"Out of bounds spans: {len(out_of_bounds)}")
    
    if out_of_bounds:
        print("\nFirst few out-of-bounds spans:")
        for item in out_of_bounds[:5]:
            print(f"  Text: '{item['text']}'")
            print(f"  BBox: {item['bbox']}")
            print(f"  Origin: {item['origin']}")
            print()
    
    doc.close()

if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1:
        analyze_pdf(sys.argv[1])
    else:
        print("Usage: python debug_pdf.py <pdf_path>")
