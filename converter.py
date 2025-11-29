import fitz  # PyMuPDF
import os

class PDFDarkThemeConverter:
    def __init__(self):
        self.background_color = (0, 0, 0)  # Black
        self.text_color = (1, 1, 1)        # White

    def convert(self, input_path: str, output_path: str):
        """
        Converts a PDF to dark mode.
        """
        doc = fitz.open(input_path)
        
        for page_num in range(len(doc)):
            page = doc[page_num]
            
            # 1. Paint black rectangle in background
            # overlay=False ensures it is drawn behind existing content.
            # However, if the page has a white background, this might be hidden.
            # Many PDFs don't have a background, so this works.
            # If there is an opaque white background, we might need to remove it or draw over it?
            # The requirement says: "Paint a black rectangle covering the entire page."
            # and "Extract all text spans and repaint them in white".
            # If we paint ON TOP (overlay=True) with black, we cover everything (images too).
            # If we paint BEHIND (overlay=False), we might be blocked by existing white bg.
            
            # Let's try drawing a black rectangle on top, but then we need to handle images.
            # Requirement: "Detect all images and leave them untouched."
            # If we draw black on top, images are covered.
            
            # Strategy:
            # 1. Analyze page for images.
            # 2. Draw black rectangle (overlay=False) - hope for transparent background.
            # 3. If that doesn't work (white bg), we might need to draw black on top but exclude images?
            #    Or draw black on top, then redraw images on top?
            #    Redrawing images is hard because we need to extract them exactly.
            
            # Let's stick to the "Extract text and repaint" part.
            # If we repaint text, we are essentially drawing new text on top.
            
            # Revised Strategy based on "Extract all text spans and repaint them":
            # 1. Draw black rectangle on top (overlay=True) to cover everything (text, white bg).
            #    WAIT! This covers images too.
            #    We need to NOT cover images.
            
            # How to "not cover images"?
            # We can't easily "subtract" regions from the rectangle in PyMuPDF draw_rect.
            
            # Alternative:
            # 1. Set page background to black? (Not really a PDF concept usually).
            # 2. Iterate through all objects. If it's a path/rect that is white, turn it black?
            
            # Let's look at the requirement again:
            # "a) Paint a black rectangle covering the entire page."
            # "b) Extract all text spans and repaint them in white..."
            # "c) Detect all images and leave them untouched."
            
            # If (a) covers the page, (c) is impossible unless we redraw images.
            # Maybe (a) implies "background" layer.
            
            # Let's try:
            # 1. Draw black rect with overlay=False.
            # 2. Change text color to white.
            #    How to change text color?
            #    We can use "redactions" to remove old text and then insert new text.
            #    Or just draw white text ON TOP of old text.
            #    If old text is black and background is black, old text is invisible.
            #    Then we draw white text on top.
            
            # What if the PDF has a white rectangle as background?
            # Then our black rect (overlay=False) is hidden.
            # We might need to find and remove large white rectangles?
            
            # For now, let's assume standard PDF with transparent/no background.
            # We will draw black rect (overlay=False).
            # We will draw white text (overlay=True).
            
            # Step 1: Background
            page.draw_rect(page.rect, color=None, fill=self.background_color, overlay=False)
            
            # Step 2: Text
            # We use "rawdict" to get individual characters. This preserves exact positioning
            # even if we fall back to a different font (like Helvetica) that has different metrics.
            # This prevents text from running off the page (the "cropping" issue).
            text_dict = page.get_text("rawdict")
            
            blocks = text_dict["blocks"]
            for block in blocks:
                if block["type"] == 0:  # Text block
                    for line in block["lines"]:
                        for span in line["spans"]:
                            # We still need font info from the span
                            font_size = span["size"]
                            font_name = span["font"]
                            
                            # Iterate over characters in the span
                            for char in span["chars"]:
                                c = char["c"]
                                origin = char["origin"]
                                
                                # Skip spaces if they don't have visual content, 
                                # but sometimes we need them? 
                                # Actually, drawing a space " " in white is invisible anyway.
                                # But let's draw everything to be safe.
                                if c.strip() == "":
                                    continue

                                try:
                                    page.insert_text(
                                        point=origin,
                                        text=c,
                                        fontsize=font_size,
                                        fontname=font_name,
                                        color=self.text_color,
                                        overlay=True
                                    )
                                except Exception:
                                    # Fallback to helv if font not found
                                    # We suppress the print to avoid log spam for every character
                                    page.insert_text(
                                        point=origin,
                                        text=c,
                                        fontsize=font_size,
                                        fontname="helv",
                                        color=self.text_color,
                                        overlay=True
                                    )

        doc.save(output_path)
        doc.close()

if __name__ == "__main__":
    converter = PDFDarkThemeConverter()
    if os.path.exists("test_input.pdf"):
        converter.convert("test_input.pdf", "test_output.pdf")
        print("Conversion complete: test_output.pdf")
    else:
        print("test_input.pdf not found.")
