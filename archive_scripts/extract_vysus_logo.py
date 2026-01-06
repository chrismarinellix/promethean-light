"""
Extract Vysus logo from PDF by rendering specific pages at high resolution
"""
import fitz  # PyMuPDF
import os

def extract_logo_pages(pdf_path, output_dir):
    """Render logo pages at high resolution to capture the V mark"""

    os.makedirs(output_dir, exist_ok=True)

    doc = fitz.open(pdf_path)

    # Pages likely to contain logo: cover (1), logo section (typically 5-12)
    logo_pages = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12]

    for page_num in logo_pages:
        if page_num >= doc.page_count:
            continue

        page = doc[page_num]

        # Render at high resolution (3x zoom)
        mat = fitz.Matrix(3, 3)
        pix = page.get_pixmap(matrix=mat, alpha=True)

        output_path = os.path.join(output_dir, f"page_{page_num+1}_hires.png")
        pix.save(output_path)
        print(f"Saved: {output_path}")

        # Also try to get just top portion where logo usually is
        # Crop to top 20% of page
        rect = page.rect
        clip_rect = fitz.Rect(rect.x0, rect.y0, rect.x1, rect.y0 + rect.height * 0.25)
        pix_top = page.get_pixmap(matrix=mat, clip=clip_rect, alpha=True)

        output_path_top = os.path.join(output_dir, f"page_{page_num+1}_top.png")
        pix_top.save(output_path_top)
        print(f"Saved: {output_path_top}")

    doc.close()
    print("\nDone! Check output folder for rendered pages.")

if __name__ == "__main__":
    pdf_path = r"C:\Code\documents\Brand Guidelines\Vysus_Brand_Guidelines-min.pdf"
    output_dir = r"C:\Code\documents\Brand Guidelines\extracted_brand\logo_renders"

    extract_logo_pages(pdf_path, output_dir)
