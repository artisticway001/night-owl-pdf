from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter, landscape
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import inch
import os

def create_test_pdf(filename):
    c = canvas.Canvas(filename, pagesize=letter)
    width, height = letter

    # Page 1: Basic Text and Columns
    c.setFont("Helvetica-Bold", 24)
    c.drawString(100, 750, "PDF Dark Mode Test Document")
    
    c.setFont("Times-Roman", 12)
    text = "This is a test document to verify the dark mode conversion."
    c.drawString(100, 730, text)
    
    # Multi-column text simulation
    c.drawString(50, 650, "Column 1: Left side text.")
    c.drawString(50, 635, "More text on the left.")
    c.drawString(300, 650, "Column 2: Right side text.")
    c.drawString(300, 635, "More text on the right.")

    # Unicode and Math
    c.setFont("Helvetica", 12)
    c.drawString(100, 550, "Unicode: α β γ δ € £ ¥ © ®")
    c.drawString(100, 530, "Math: ∑ x² + y² = z²")

    # Vector Graphics (Rectangles, Circles)
    c.setStrokeColorRGB(1, 0, 0) # Red stroke
    c.setFillColorRGB(0, 1, 0)   # Green fill
    c.rect(100, 400, 100, 50, fill=1)
    
    c.setStrokeColorRGB(0, 0, 1) # Blue stroke
    c.setFillColorRGB(1, 1, 0)   # Yellow fill
    c.circle(300, 425, 25, fill=1)

    c.showPage()

    # Page 2: Landscape and Table (using low-level for simplicity or Platypus if needed)
    # Let's stick to canvas for control
    c.setPageSize(landscape(letter))
    c.setFont("Helvetica-Bold", 18)
    c.drawString(50, 550, "Page 2: Landscape Layout")
    
    # Table simulation
    x_start = 50
    y_start = 500
    row_height = 20
    col_width = 100
    
    data = [
        ["Header 1", "Header 2", "Header 3"],
        ["Row 1, Col 1", "Row 1, Col 2", "Row 1, Col 3"],
        ["Row 2, Col 1", "Row 2, Col 2", "Row 2, Col 3"],
    ]
    
    for row in data:
        for i, cell in enumerate(row):
            c.rect(x_start + i*col_width, y_start, col_width, row_height)
            c.drawString(x_start + i*col_width + 5, y_start + 5, cell)
        y_start -= row_height

    # Image placeholder (we can't easily embed a real image without a file)
    # We will draw a "fake" image using vector commands but label it as Image
    c.saveState()
    c.translate(400, 300)
    c.setFillColorRGB(0.5, 0.5, 0.5)
    c.rect(0, 0, 200, 150, fill=1)
    c.setFillColorRGB(1, 1, 1)
    c.drawString(50, 75, "Image Placeholder")
    c.restoreState()

    c.save()
    print(f"Created {filename}")

if __name__ == "__main__":
    create_test_pdf("test_input.pdf")
