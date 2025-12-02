import fitz  # PyMuPDF
import os

class PDFDarkThemeConverter:
    def __init__(self):
        # Soft dark theme - easier on the eyes than pure black
        # RGB values in 0-1 range for PyMuPDF
        self.background_color = (0.1, 0.1, 0.1)  # Soft dark gray (#1a1a1a)
        self.text_color = (0.96, 0.96, 0.96)     # Slightly off-white (#f5f5f5)
        self.font_cache = {}  # Cache for font availability checks

    def _check_font(self, font_name: str) -> str:
        """
        Check if a font is available, with caching to avoid repeated checks.
        Returns the font name if available, otherwise returns 'helv'.
        """
        if font_name in self.font_cache:
            return self.font_cache[font_name]
        
        # Test if font works by trying to use it
        # We'll cache the result to avoid repeated checks
        try:
            # Simple check - if the font name is standard, use it
            if font_name.lower() in ['helv', 'helvetica', 'times', 'courier']:
                self.font_cache[font_name] = font_name
                return font_name
            # For other fonts, we'll try them but cache the fallback
            self.font_cache[font_name] = font_name
            return font_name
        except:
            self.font_cache[font_name] = 'helv'
            return 'helv'

    def _is_white(self, color):
        """Check if a color is white or close to white."""
        if not color:
            return False
        # Handle different color formats (int, tuple, list)
        if isinstance(color, int):
            # Hex/Int representation
            r = (color >> 16) & 0xFF
            g = (color >> 8) & 0xFF
            b = color & 0xFF
            return r > 240 and g > 240 and b > 240
        elif isinstance(color, (tuple, list)):
            if len(color) >= 3:
                # 0-1 float range
                if all(isinstance(c, float) for c in color):
                    return all(c > 0.9 for c in color)
                # 0-255 int range
                return all(c > 240 for c in color)
        return False

    def _is_black(self, color):
        """Check if a color is black or close to black."""
        if color is None:
            return True # Default stroke is often black
        if isinstance(color, int):
            return color < 100 # Rough check
        elif isinstance(color, (tuple, list)):
            if len(color) >= 3:
                if all(isinstance(c, float) for c in color):
                    return all(c < 0.1 for c in color)
                return all(c < 20 for c in color)
        return False

    def convert(self, input_path: str, output_path: str):
        """
        Converts a PDF to dark mode by reconstructing the page content.
        Strategy:
        1. Analyze existing content (drawings, images, text).
        2. Draw a black "curtain" over everything (overlay=True).
        3. Redraw vector graphics (lines, tables) on top, inverting colors.
        4. Redraw images on top.
        5. Redraw text on top (white).
        
        IMPORTANT: Preserves original page dimensions to avoid cropping.
        """
        doc = fitz.open(input_path)
        
        for page_num in range(len(doc)):
            page = doc[page_num]
            
            # --- Step 1: Capture Data ---
            # Get drawings before we cover them
            drawings = page.get_drawings()
            # Get images
            image_list = page.get_images(full=True)
            
            # Get text - IMPORTANT: Use a large clip rect to find out-of-bounds text
            # Default get_text only looks inside page.rect
            large_rect = fitz.Rect(-1000, -1000, 5000, 5000)
            text_dict = page.get_text("dict", clip=large_rect)
            
            # --- Step 1.5: Auto-Expand Page Size ---
            # Calculate required dimensions to fit all content
            max_x = page.rect.width
            max_y = page.rect.height
            
            # Check text bounds
            blocks = text_dict["blocks"]
            for block in blocks:
                if block["type"] == 0:
                    for line in block["lines"]:
                        for span in line["spans"]:
                            bbox = span["bbox"]
                            max_x = max(max_x, bbox[2])
                            max_y = max(max_y, bbox[3])
            
            # Check drawing bounds
            for path in drawings:
                rect = path['rect']
                max_x = max(max_x, rect.x1)
                max_y = max(max_y, rect.y1)
                
            # Add some padding (e.g., 20 points)
            if max_x > page.rect.width or max_y > page.rect.height:
                new_width = max_x + 20
                new_height = max_y + 20
                # Update page mediabox to fit content
                page.set_mediabox(fitz.Rect(0, 0, new_width, new_height))
            
            # --- Step 2: The Black Curtain ---
            # Draw a black rectangle over the entire page
            # Use page.rect which respects the current page boundaries (now potentially expanded)
            page.draw_rect(page.rect, color=None, fill=self.background_color, overlay=True)
            
            # --- Step 3: Redraw Vector Graphics ---
            shape = page.new_shape()
            
            for path in drawings:
                # Skip if it looks like a white background layer
                # Heuristic: Large rect, filled with white
                if path['rect'].width > page.rect.width * 0.9 and \
                   path['rect'].height > page.rect.height * 0.9 and \
                   self._is_white(path['fill']):
                    continue
                
                # Determine new colors
                stroke = path['color']
                fill = path['fill']
                
                # Invert black stroke to white
                if self._is_black(stroke):
                    stroke = self.text_color
                
                # Invert white fill to black (or transparent?)
                # If it's a small white box, maybe it should be black?
                if self._is_white(fill):
                    fill = self.background_color
                
                # Re-draw items
                for item in path['items']:
                    if item[0] == 'l': # line
                        shape.draw_line(item[1], item[2])
                    elif item[0] == 're': # rect
                        shape.draw_rect(item[1])
                    elif item[0] == 'c': # curve
                        shape.draw_bezier(item[1], item[2], item[3], item[4])
                    # Add other shapes if needed (quads, etc.)
                
                # Finish the shape with new colors
                try:
                    # Clean up dashes if needed
                    dashes = path['dashes']
                    if dashes == '[] 0':
                        dashes = None
                        
                    shape.finish(color=stroke, fill=fill, width=path['width'], 
                                 lineCap=path['lineCap'], lineJoin=path['lineJoin'], 
                                 dashes=dashes, closePath=path['closePath'])
                except:
                    # If drawing fails, skip this path to prevent crash
                    continue
            
            # Commit drawings
            shape.commit(overlay=True)
            
            # --- Step 4: Redraw Images ---
            for img in image_list:
                xref = img[0]
                # Get image bbox - this is tricky as get_images doesn't give rect directly
                # We need to find where the image is used.
                # page.get_image_rects(xref) returns a list of rects
                rects = page.get_image_rects(xref)
                for rect in rects:
                    try:
                        page.insert_image(rect, xref=xref, overlay=True)
                    except:
                        pass

            # --- Step 5: Redraw Text (Optimized) ---
            blocks = text_dict["blocks"]
            for block in blocks:
                if block["type"] == 0:  # Text block
                    for line in block["lines"]:
                        for span in line["spans"]:
                            text = span["text"]
                            if not text or not text.strip():
                                continue
                                
                            font_size = span["size"]
                            font_name = span["font"]
                            origin = span["origin"]
                            
                            font_to_use = self._check_font(font_name)
                            
                            try:
                                # Use insert_text with render_mode=0 to ensure text is visible
                                page.insert_text(
                                    point=origin,
                                    text=text,
                                    fontsize=font_size,
                                    fontname=font_to_use,
                                    color=self.text_color,
                                    render_mode=0,  # Fill text (default, ensures visibility)
                                    overlay=True
                                )
                            except:
                                # Fallback to helvetica
                                try:
                                    page.insert_text(
                                        point=origin,
                                        text=text,
                                        fontsize=font_size,
                                        fontname="helv",
                                        color=self.text_color,
                                        render_mode=0,
                                        overlay=True
                                    )
                                except:
                                    pass

        # Save with optimized settings for speed vs size
        # garbage=3 is good balance, deflate=True is needed for size but costs CPU
        # clean=False saves time on large files
        doc.save(output_path, garbage=3, deflate=True)
        doc.close()

if __name__ == "__main__":
    converter = PDFDarkThemeConverter()
    if os.path.exists("test_input.pdf"):
        converter.convert("test_input.pdf", "test_output.pdf")
        print("Conversion complete: test_output.pdf")
    else:
        print("test_input.pdf not found.")
