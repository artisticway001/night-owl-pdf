import fitz

def deep_analyze_pdf(path):
    """Analyze PDF structure in detail to understand cropping issue"""
    doc = fitz.open(path)
    page = doc[0]
    
    print("=" * 60)
    print("PDF PAGE ANALYSIS")
    print("=" * 60)
    
    # Check all box types
    print(f"\nMediaBox: {page.mediabox}")
    print(f"CropBox:  {page.cropbox}")
    print(f"page.rect: {page.rect}")
    
    # Check rotation
    print(f"\nRotation: {page.rotation}")
    
    # Analyze text bounding boxes
    text_dict = page.get_text("dict")
    blocks = text_dict["blocks"]
    
    print(f"\n--- TEXT ANALYSIS ---")
    max_x = 0
    max_y = 0
    min_x = float('inf')
    min_y = float('inf')
    
    sample_spans = []
    
    for block in blocks:
        if block["type"] == 0:
            for line in block["lines"]:
                for span in line["spans"]:
                    bbox = span["bbox"]
                    max_x = max(max_x, bbox[2])
                    max_y = max(max_y, bbox[3])
                    min_x = min(min_x, bbox[0])
                    min_y = min(min_y, bbox[1])
                    
                    # Collect samples from right edge
                    if bbox[2] > page.rect.width * 0.8:
                        sample_spans.append({
                            'text': span['text'][:40],
                            'bbox': bbox,
                            'origin': span['origin']
                        })
    
    print(f"Text bounding box:")
    print(f"  X: {min_x:.2f} to {max_x:.2f} (page width: {page.rect.width:.2f})")
    print(f"  Y: {min_y:.2f} to {max_y:.2f} (page height: {page.rect.height:.2f})")
    
    if max_x > page.rect.width:
        print(f"\n⚠️  WARNING: Text extends {max_x - page.rect.width:.2f} points beyond page width!")
    
    if sample_spans:
        print(f"\nSample spans near right edge:")
        for s in sample_spans[:3]:
            print(f"  '{s['text']}'")
            print(f"    BBox: {s['bbox']}")
            print(f"    Origin: {s['origin']}")
    
    doc.close()

if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1:
        deep_analyze_pdf(sys.argv[1])
    else:
        # Try common test files
        import os
        for f in ["test_input.pdf", "test_output.pdf", "integration_output.pdf"]:
            if os.path.exists(f):
                print(f"\nAnalyzing: {f}")
                deep_analyze_pdf(f)
                print()
