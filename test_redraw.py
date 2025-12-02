
import fitz

def create_test_pdf():
    doc = fitz.open()
    page = doc.new_page()
    
    # Draw a white background rect
    page.draw_rect(page.rect, fill=(1, 1, 1), color=None)
    
    # Draw a black table border
    shape = page.new_shape()
    shape.draw_rect(fitz.Rect(50, 50, 300, 200))
    shape.finish(color=(0, 0, 0), width=2)
    
    # Draw some text
    page.insert_text((60, 80), "Hello World", color=(0, 0, 0))
    
    doc.save("redraw_test_input.pdf")
    doc.close()

def test_redraw():
    doc = fitz.open("redraw_test_input.pdf")
    page = doc[0]
    
    # 1. Get Data
    paths = page.get_drawings()
    
    # 2. Draw Black Curtain
    page.draw_rect(page.rect, fill=(0, 0, 0), overlay=True)
    
    # 3. Redraw Paths
    shape = page.new_shape()
    
    for path in paths:
        # Check if it's a white background
        if path['fill'] == (1, 1, 1) and path['rect'] == page.rect:
            print("Skipping white background")
            continue
            
        # Invert colors
        stroke = path['color']
        if stroke == (0, 0, 0):
            stroke = (1, 1, 1)
            
        # Re-create items
        for item in path['items']:
            if item[0] == 'l': # line
                shape.draw_line(item[1], item[2])
            elif item[0] == 're': # rect
                shape.draw_rect(item[1])
            elif item[0] == 'c': # curve
                shape.draw_bezier(item[1], item[2], item[3], item[4])
        
        shape.finish(color=stroke, width=path['width'], fill=None) # Simplified fill handling
        
    shape.commit(overlay=True)
    
    # 4. Redraw Text (Simplified)
    page.insert_text((60, 80), "Hello World Redrawn", color=(1, 1, 1), overlay=True)
    
    doc.save("redraw_test_output.pdf")
    print("Saved redraw_test_output.pdf")

if __name__ == "__main__":
    create_test_pdf()
    test_redraw()
