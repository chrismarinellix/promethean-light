# PDF Logo Tracer

Extract logos, icons, and shapes from PDF files and convert them to SVG paths using image tracing.

## Trigger
Use when user asks to:
- "extract logo from PDF"
- "trace logo to SVG"
- "convert PDF image to SVG"
- "get vector logo from PDF"

## Process

### Step 1: Render PDF page at high resolution
```python
import fitz  # PyMuPDF
import cv2
import numpy as np

def render_pdf_page(pdf_path, page_num, output_path, zoom=6):
    """Render a PDF page at high resolution"""
    doc = fitz.open(pdf_path)
    page = doc[page_num]
    mat = fitz.Matrix(zoom, zoom)
    pix = page.get_pixmap(matrix=mat, alpha=False)
    pix.save(output_path)
    doc.close()
    return output_path
```

### Step 2: Optional - Crop to specific area
```python
def render_pdf_crop(pdf_path, page_num, output_path, crop_rect, zoom=10):
    """Render a cropped area of PDF page"""
    doc = fitz.open(pdf_path)
    page = doc[page_num]
    # crop_rect is fitz.Rect(left, top, right, bottom)
    mat = fitz.Matrix(zoom, zoom)
    pix = page.get_pixmap(matrix=mat, clip=crop_rect, alpha=False)
    pix.save(output_path)
    doc.close()
    return output_path
```

### Step 3: Trace image to SVG paths
```python
def trace_logo_to_svg(image_path, min_area=5000, threshold=100):
    """
    Trace shapes from image and convert to SVG paths

    Args:
        image_path: Path to PNG image
        min_area: Minimum contour area to include (filters noise)
        threshold: Binary threshold (0-255) for detecting dark shapes

    Returns:
        dict with 'viewbox' and 'paths' keys
    """
    img = cv2.imread(image_path)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    # Threshold to binary (assumes dark logo on light background)
    _, binary = cv2.threshold(gray, threshold, 255, cv2.THRESH_BINARY_INV)

    # Find contours
    contours, _ = cv2.findContours(binary, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    # Filter by area and position
    height, width = binary.shape
    logo_contours = []

    for c in contours:
        area = cv2.contourArea(c)
        if area < min_area:
            continue
        x, y, w, h = cv2.boundingRect(c)
        # Skip very small shapes
        if w < 50 or h < 50:
            continue
        logo_contours.append(c)

    if not logo_contours:
        return None

    # Sort left to right
    logo_contours.sort(key=lambda c: cv2.boundingRect(c)[0])

    # Get total bounds
    all_points = np.vstack(logo_contours)
    x_min, y_min, total_w, total_h = cv2.boundingRect(all_points)

    # Scale to 100 units wide
    scale = 100 / total_w
    view_h = total_h * scale

    # Generate SVG paths
    paths = []
    for contour in logo_contours:
        # Simplify contour
        epsilon = 0.008 * cv2.arcLength(contour, True)
        approx = cv2.approxPolyDP(contour, epsilon, True)

        # Build path string
        path_d = "M"
        for j, point in enumerate(approx):
            px = (point[0][0] - x_min) * scale
            py = (point[0][1] - y_min) * scale
            if j == 0:
                path_d += f"{px:.1f} {py:.1f}"
            else:
                path_d += f" L{px:.1f} {py:.1f}"
        path_d += " Z"
        paths.append(path_d)

    return {
        'viewbox': f"0 0 100 {view_h:.0f}",
        'paths': paths
    }
```

### Step 4: Generate SVG code
```python
def generate_svg_html(trace_result, css_class="logo"):
    """Generate SVG HTML from trace result"""
    if not trace_result:
        return None

    svg = f'<svg class="{css_class}" viewBox="{trace_result["viewbox"]}" xmlns="http://www.w3.org/2000/svg">\n'
    for path in trace_result['paths']:
        svg += f'  <path d="{path}" fill="currentColor"/>\n'
    svg += '</svg>'
    return svg
```

## Complete Example Script

```python
"""
Complete logo extraction and tracing script
"""
import fitz
import cv2
import numpy as np
import os

def extract_and_trace_logo(pdf_path, page_num, output_dir,
                           crop_rect=None, zoom=10,
                           min_area=5000, threshold=100):
    """
    Extract logo from PDF and trace to SVG

    Args:
        pdf_path: Path to PDF file
        page_num: Page number (0-indexed)
        output_dir: Directory for output files
        crop_rect: Optional (left, top, right, bottom) tuple to crop
        zoom: Render zoom level (higher = more detail)
        min_area: Minimum contour area
        threshold: Binary threshold for detection

    Returns:
        SVG code string
    """
    os.makedirs(output_dir, exist_ok=True)

    # Render PDF
    doc = fitz.open(pdf_path)
    page = doc[page_num]

    mat = fitz.Matrix(zoom, zoom)
    if crop_rect:
        clip = fitz.Rect(*crop_rect)
        pix = page.get_pixmap(matrix=mat, clip=clip, alpha=False)
    else:
        pix = page.get_pixmap(matrix=mat, alpha=False)

    img_path = os.path.join(output_dir, "logo_render.png")
    pix.save(img_path)
    doc.close()

    # Trace
    img = cv2.imread(img_path)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    _, binary = cv2.threshold(gray, threshold, 255, cv2.THRESH_BINARY_INV)

    contours, _ = cv2.findContours(binary, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    # Filter contours
    logo_contours = [c for c in contours
                     if cv2.contourArea(c) >= min_area
                     and cv2.boundingRect(c)[2] >= 50
                     and cv2.boundingRect(c)[3] >= 50]

    if not logo_contours:
        print("No logo shapes found")
        return None

    logo_contours.sort(key=lambda c: cv2.boundingRect(c)[0])

    all_points = np.vstack(logo_contours)
    x_min, y_min, total_w, total_h = cv2.boundingRect(all_points)

    scale = 100 / total_w
    view_h = total_h * scale

    # Generate SVG
    svg = f'<svg viewBox="0 0 100 {view_h:.0f}" xmlns="http://www.w3.org/2000/svg">\n'

    for contour in logo_contours:
        epsilon = 0.008 * cv2.arcLength(contour, True)
        approx = cv2.approxPolyDP(contour, epsilon, True)

        path_d = "M"
        for j, point in enumerate(approx):
            px = (point[0][0] - x_min) * scale
            py = (point[0][1] - y_min) * scale
            path_d += f"{px:.1f} {py:.1f}" if j == 0 else f" L{px:.1f} {py:.1f}"
        path_d += " Z"

        svg += f'  <path d="{path_d}" fill="currentColor"/>\n'

    svg += '</svg>'

    # Save SVG file
    svg_path = os.path.join(output_dir, "logo.svg")
    with open(svg_path, 'w') as f:
        f.write(svg)

    print(f"SVG saved to: {svg_path}")
    return svg


# Usage example:
if __name__ == "__main__":
    svg = extract_and_trace_logo(
        pdf_path=r"path/to/document.pdf",
        page_num=10,  # 0-indexed
        output_dir=r"path/to/output",
        zoom=10,
        min_area=10000,
        threshold=100
    )
    print(svg)
```

## Required Dependencies
```
pip install PyMuPDF opencv-python numpy
```

## Tips
- **zoom**: Higher values (10-15) give more detail but larger images
- **threshold**: Adjust if logo isn't being detected (lower for lighter logos)
- **min_area**: Increase to filter out small noise, decrease to capture small details
- **epsilon factor**: In `approxPolyDP`, use 0.005 for more detail, 0.02 for simpler paths
- For **light logos on dark backgrounds**, use `cv2.THRESH_BINARY` instead of `cv2.THRESH_BINARY_INV`
