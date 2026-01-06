"""
Extract a close-up of just the Vysus marque/logo from page 11
"""
import fitz
import os

def extract_logo_closeup(pdf_path, output_dir):
    """Render just the logo area at very high resolution"""

    os.makedirs(output_dir, exist_ok=True)

    doc = fitz.open(pdf_path)

    # Page 11 (index 10) has the marque
    page = doc[10]

    # Get page dimensions
    rect = page.rect
    print(f"Page size: {rect.width} x {rect.height}")

    # The marque appears in the center-right area of the page
    # Based on the layout, it's roughly in the middle third horizontally
    # and middle third vertically

    # Crop to just the logo area (approximate based on page 11 layout)
    # Logo is in right half, middle section
    logo_rect = fitz.Rect(
        rect.width * 0.45,  # left - start at 45% from left
        rect.height * 0.25,  # top - start at 25% from top
        rect.width * 0.75,   # right - end at 75% from left
        rect.height * 0.65   # bottom - end at 65% from top
    )

    # Render at very high resolution (6x)
    mat = fitz.Matrix(6, 6)
    pix = page.get_pixmap(matrix=mat, clip=logo_rect, alpha=False)

    output_path = os.path.join(output_dir, "vysus_marque_closeup.png")
    pix.save(output_path)
    print(f"Saved: {output_path}")

    # Also get the full logo with wordmark from page 12
    page12 = doc[11]

    # The wordmarque is in the center of page 12
    wordmark_rect = fitz.Rect(
        rect.width * 0.35,
        rect.height * 0.35,
        rect.width * 0.85,
        rect.height * 0.55
    )

    pix2 = page12.get_pixmap(matrix=mat, clip=wordmark_rect, alpha=False)
    output_path2 = os.path.join(output_dir, "vysus_wordmark_closeup.png")
    pix2.save(output_path2)
    print(f"Saved: {output_path2}")

    doc.close()

if __name__ == "__main__":
    pdf_path = r"C:\Code\documents\Brand Guidelines\Vysus_Brand_Guidelines-min.pdf"
    output_dir = r"C:\Code\documents\Brand Guidelines\extracted_brand\logo_renders"

    extract_logo_closeup(pdf_path, output_dir)
