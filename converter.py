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
        
        try:
            if font_name.lower() in ['helv', 'helvetica', 'times', 'courier']:
                self.font_cache[font_name] = font_name
                return font_name
            self.font_cache[font_name] = font_name
            return font_name
        except:
            self.font_cache[font_name] = 'helv'
            return 'helv'

    def _is_white(self, color):
        """Check if a color is white or close to white."""
        if not color:
            return False
        if isinstance(color, int):
            r = (color >> 16) & 0xFF
            g = (color >> 8) & 0xFF
            b = color & 0xFF
            return r > 240 and g > 240 and b > 240
        elif isinstance(color, (tuple, list)):
            if len(color) >= 3:
                if all(isinstance(c, float) for c in color):
                    return all(c > 0.9 for c in color)
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

    def _detect_table_regions(self, drawings, page_rect):
        """
        Detect table regions by analyzing rectangular grid patterns.
        Returns list of fitz.Rect objects representing table bounding boxes.
        """
        # Collect horizontal and vertical lines with their positions
        h_lines = []  # (y_position, x_start, x_end, rect)
        v_lines = []  # (x_position, y_start, y_end, rect)
        
        for path in drawings:
            # Skip very large paths (likely backgrounds)
            if path['rect'].width > page_rect.width * 0.9:
                continue
                
            # Analyze path items
            for item in path['items']:
                if item[0] == 'l':  # line
                    p1, p2 = item[1], item[2]
                    # Check if horizontal (within 2 points tolerance)
                    if abs(p1.y - p2.y) < 2:
                        y = (p1.y + p2.y) / 2
                        x_start = min(p1.x, p2.x)
                        x_end = max(p1.x, p2.x)
                        h_lines.append((y, x_start, x_end, path['rect']))
                    # Check if vertical
                    elif abs(p1.x - p2.x) < 2:
                        x = (p1.x + p2.x) / 2
                        y_start = min(p1.y, p2.y)
                        y_end = max(p1.y, p2.y)
                        v_lines.append((x, y_start, y_end, path['rect']))
        
        # Find table regions by clustering nearby lines
        table_regions = []
        MIN_H_LINES = 3  # Minimum horizontal lines
        MIN_V_LINES = 3  # Minimum vertical lines
        MIN_SIZE = 100   # Minimum dimension
        MAX_GAP = 50     # Maximum gap between lines to be considered part of same table
        
        if len(h_lines) < MIN_H_LINES or len(v_lines) < MIN_V_LINES:
            return []
        
        # Sort lines by position
        h_lines.sort(key=lambda x: x[0])  # Sort by y
        v_lines.sort(key=lambda x: x[0])  # Sort by x
        
        # Cluster horizontal lines
        h_clusters = []
        current_cluster = [h_lines[0]]
        for i in range(1, len(h_lines)):
            if h_lines[i][0] - current_cluster[-1][0] < MAX_GAP:
                current_cluster.append(h_lines[i])
            else:
                if len(current_cluster) >= MIN_H_LINES:
                    h_clusters.append(current_cluster)
                current_cluster = [h_lines[i]]
        if len(current_cluster) >= MIN_H_LINES:
            h_clusters.append(current_cluster)
        
        # Cluster vertical lines
        v_clusters = []
        current_cluster = [v_lines[0]]
        for i in range(1, len(v_lines)):
            if v_lines[i][0] - current_cluster[-1][0] < MAX_GAP:
                current_cluster.append(v_lines[i])
            else:
                if len(current_cluster) >= MIN_V_LINES:
                    v_clusters.append(current_cluster)
                current_cluster = [v_lines[i]]
        if len(current_cluster) >= MIN_V_LINES:
            v_clusters.append(current_cluster)
        
        # Find intersecting clusters (actual tables)
        for h_cluster in h_clusters:
            for v_cluster in v_clusters:
                # Calculate bounding boxes
                h_y_min = min(line[0] for line in h_cluster)
                h_y_max = max(line[0] for line in h_cluster)
                h_x_min = min(line[1] for line in h_cluster)
                h_x_max = max(line[2] for line in h_cluster)
                
                v_x_min = min(line[0] for line in v_cluster)
                v_x_max = max(line[0] for line in v_cluster)
                v_y_min = min(line[1] for line in v_cluster)
                v_y_max = max(line[2] for line in v_cluster)
                
                # Check if they overlap (indicating a table)
                x_overlap = not (h_x_max < v_x_min or v_x_max < h_x_min)
                y_overlap = not (h_y_max < v_y_min or v_y_max < h_y_min)
                
                if x_overlap and y_overlap:
                    # Create bounding box for this table
                    min_x = max(h_x_min, v_x_min)
                    max_x = min(h_x_max, v_x_max)
                    min_y = max(h_y_min, v_y_min)
                    max_y = min(h_y_max, v_y_max)
                    
                    table_rect = fitz.Rect(min_x, min_y, max_x, max_y)
                    
                    # Only add if large enough
                    if table_rect.width > MIN_SIZE and table_rect.height > MIN_SIZE:
                        table_regions.append(table_rect)
        
        return table_regions

    def _render_region_to_image(self, page, region_rect, zoom=2):
        """
        Render a specific region of the page to an inverted image.
        Returns image bytes.
        """
        # Create a matrix for high-res rendering
        mat = fitz.Matrix(zoom, zoom)
        
        # Render the specific region
        pix = page.get_pixmap(matrix=mat, clip=region_rect)
        
        # Invert pixels (white->black, black->white)
        pix_rect = fitz.IRect(0, 0, pix.width, pix.height)
        pix.invert_irect(pix_rect)
        
        return pix.tobytes()

    def _is_inside_table(self, path_rect, table_regions):
        """Check if a path rectangle is inside any table region."""
        for table_rect in table_regions:
            # Check if path is mostly inside table (>80% overlap)
            if table_rect.contains(path_rect) or \
               (table_rect.intersects(path_rect) and 
                self._overlap_ratio(path_rect, table_rect) > 0.8):
                return True
        return False

    def _overlap_ratio(self, rect1, rect2):
        """Calculate overlap ratio between two rectangles."""
        intersection = rect1 & rect2  # Intersection
        if intersection.is_empty:
            return 0.0
        return intersection.get_area() / rect1.get_area()

    def convert(self, input_path: str, output_path: str):
        """
        Converts a PDF to dark mode (Vector Approach).
        1. Capture content.
        2. Redact original (Fix Double Text).
        3. Draw Dark Background.
        4. Redraw Vectors (High Contrast).
        5. Redraw Images.
        6. Redraw Text.
        """
        doc = fitz.open(input_path)
        
        for page_num in range(len(doc)):
            page = doc[page_num]
            
            # --- Step 1: Capture Data ---
            drawings = page.get_drawings()
            
            # NEW: Detect table regions
            table_regions = self._detect_table_regions(drawings, page.rect)
            
            # NEW: Render table regions as ORIGINAL (non-inverted) images BEFORE redaction
            table_images = []
            for region in table_regions:
                try:
                    # Render at high resolution
                    mat = fitz.Matrix(2, 2)
                    pix = page.get_pixmap(matrix=mat, clip=region)
                    # DON'T invert - keep original colors
                    img_data = pix.tobytes()
                    table_images.append((region, img_data))
                except:
                    pass  # Skip if rendering fails
            
            image_data = []
            image_list = page.get_images(full=True)
            for img in image_list:
                xref = img[0]
                rects = page.get_image_rects(xref)
                for rect in rects:
                    image_data.append((xref, rect))
            
            large_rect = fitz.Rect(-1000, -1000, 5000, 5000)
            text_dict = page.get_text("dict", clip=large_rect)
            
            # --- Step 2: Auto-Expand Page Size ---
            max_x = page.rect.width
            max_y = page.rect.height
            
            blocks = text_dict["blocks"]
            for block in blocks:
                if block["type"] == 0:
                    for line in block["lines"]:
                        for span in line["spans"]:
                            if "bbox" in span:
                                bbox = span["bbox"]
                                max_x = max(max_x, bbox[2])
                                max_y = max(max_y, bbox[3])
            
            for path in drawings:
                rect = path['rect']
                max_x = max(max_x, rect.x1)
                max_y = max(max_y, rect.y1)
                
            safety_margin = 50
            new_width = max(max_x, page.rect.width) + safety_margin
            new_height = max(max_y, page.rect.height)
            new_rect = fitz.Rect(0, 0, new_width, new_height)
            
            # --- Step 3: Redact Original Content ---
            redact_rect = page.rect
            page.add_redact_annot(redact_rect)
            page.apply_redactions()
            
            # Resize
            page.set_mediabox(new_rect)
            page.set_cropbox(new_rect)
            
            # --- Step 4: Draw Background ---
            page.draw_rect(page.rect, color=None, fill=self.background_color, overlay=True)
            
            # NEW: Step 4.5: Overlay Table Images (Original Colors)
            for region, img_data in table_images:
                try:
                    page.insert_image(region, stream=img_data, overlay=True)
                except:
                    pass
            
            # --- Step 5: Redraw Vector Graphics ---
            shape = page.new_shape()
            
            for path in drawings:
                # NEW: Skip paths that are inside table regions
                if self._is_inside_table(path['rect'], table_regions):
                    continue
                
                # Skip massive white backgrounds
                if path['rect'].width > page.rect.width * 0.9 and \
                   path['rect'].height > page.rect.height * 0.9 and \
                   self._is_white(path['fill']):
                    continue
                
                stroke = path['color']
                fill = path['fill']
                
                # Check if this path is inside a table
                is_in_table = self._is_inside_table(path['rect'], table_regions)
                
                # Simple logic: only invert black/white
                if self._is_black(stroke):
                    stroke = self.text_color
                
                # Special handling for fills
                if self._is_white(fill):
                    # White fills become dark background
                    fill = self.background_color
                elif is_in_table and fill is not None:
                    # Inside tables: keep colored fills as-is for now
                    # This preserves table cell backgrounds
                    pass
                
                for item in path['items']:
                    if item[0] == 'l': 
                        shape.draw_line(item[1], item[2])
                    elif item[0] == 're': 
                        shape.draw_rect(item[1])
                    elif item[0] == 'c': 
                        shape.draw_bezier(item[1], item[2], item[3], item[4])
                    elif item[0] == 'qu':
                        shape.draw_quad(item[1])
                
                try:
                    dashes = path['dashes']
                    if dashes == '[] 0':
                        dashes = None
                    shape.finish(color=stroke, fill=fill, width=path['width'], 
                                 lineCap=path['lineCap'], lineJoin=path['lineJoin'], 
                                 dashes=dashes, closePath=path['closePath'])
                except:
                    continue
            
            shape.commit(overlay=True)
            
            # --- Step 6: Redraw Images ---
            for xref, rect in image_data:
                try:
                    page.insert_image(rect, xref=xref, overlay=True)
                except:
                    pass

            # --- Step 7: Redraw Text (Skip text inside tables) ---
            for block in blocks:
                if block["type"] == 0:
                    for line in block["lines"]:
                        for span in line["spans"]:
                            text = span["text"]
                            if not text or not text.strip():
                                continue
                            
                            # NEW: Skip text inside table regions
                            if "bbox" in span:
                                text_rect = fitz.Rect(span["bbox"])
                                if self._is_inside_table(text_rect, table_regions):
                                    continue  # Skip table text (it's in the image)
                                
                            input_origin = span["origin"]
                            # Ensure origin is a point tuple
                            origin = (input_origin[0], input_origin[1])
                            
                            font_size = span["size"]
                            font_name = span["font"]
                            font_to_use = self._check_font(font_name)
                            
                            try:
                                page.insert_text(
                                    point=origin,
                                    text=text,
                                    fontsize=font_size,
                                    fontname=font_to_use,
                                    color=self.text_color,
                                    render_mode=0,
                                    overlay=True
                                )
                            except:
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

        doc.save(output_path, garbage=3, deflate=True)
        doc.close()

if __name__ == "__main__":
    converter = PDFDarkThemeConverter()
    if os.path.exists("test_input.pdf"):
        converter.convert("test_input.pdf", "test_output.pdf")
        print("Conversion complete: test_output.pdf")
    else:
        print("test_input.pdf not found.")
