"""
Trace the Vysus logo from a tightly cropped image
"""
import cv2
import numpy as np
import fitz

def extract_and_trace_logo():
    """Extract just the marque from the PDF and trace it"""

    # First, render just the logo area very precisely
    pdf_path = r"C:\Code\documents\Brand Guidelines\Vysus_Brand_Guidelines-min.pdf"
    output_dir = r"C:\Code\documents\Brand Guidelines\extracted_brand\logo_renders"

    doc = fitz.open(pdf_path)
    page = doc[10]  # Page 11

    # Page is 1920x1080
    # The marque is roughly at:
    # - Left edge around x=700 (36% of 1920)
    # - Top around y=480 (44% of 1080)
    # - Width around 180px
    # - Height around 240px

    rect = page.rect
    logo_rect = fitz.Rect(
        680,   # left
        460,   # top
        920,   # right
        720    # bottom
    )

    # Very high resolution
    mat = fitz.Matrix(10, 10)
    pix = page.get_pixmap(matrix=mat, clip=logo_rect, alpha=False)

    logo_path = f"{output_dir}/vysus_marque_tight.png"
    pix.save(logo_path)
    print(f"Saved tight crop: {logo_path}")

    doc.close()

    # Now trace it
    img = cv2.imread(logo_path)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    # Threshold
    _, binary = cv2.threshold(gray, 50, 255, cv2.THRESH_BINARY_INV)

    # Find contours
    contours, _ = cv2.findContours(binary, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    print(f"\nFound {len(contours)} contours")

    # Get large contours only (the two logo parts)
    large_contours = []
    for c in contours:
        area = cv2.contourArea(c)
        if area > 5000:  # Filter noise
            x, y, w, h = cv2.boundingRect(c)
            print(f"  Contour: area={area:.0f}, bounds=({x},{y},{w},{h})")
            large_contours.append(c)

    if len(large_contours) < 2:
        print("Did not find both logo parts!")
        return

    # Sort left to right
    large_contours.sort(key=lambda c: cv2.boundingRect(c)[0])

    # Get total bounds
    all_points = np.vstack(large_contours)
    x_min, y_min, total_w, total_h = cv2.boundingRect(all_points)
    print(f"\nTotal bounds: ({x_min}, {y_min}) size ({total_w}, {total_h})")

    # Scale to fit in 100x100 viewBox with proper aspect ratio
    aspect = total_w / total_h
    if aspect > 1:
        scale = 100 / total_w
        view_w = 100
        view_h = 100 / aspect
    else:
        scale = 100 / total_h
        view_h = 100
        view_w = 100 * aspect

    print(f"Scale: {scale:.4f}, viewBox: 0 0 {view_w:.1f} {view_h:.1f}")

    print("\n" + "="*70)
    print("SVG PATHS FOR HTML:")
    print("="*70)

    for idx, contour in enumerate(large_contours):
        # Approximate with different precision levels
        for eps_factor in [0.005, 0.01, 0.02]:
            epsilon = eps_factor * cv2.arcLength(contour, True)
            approx = cv2.approxPolyDP(contour, epsilon, True)

            path_d = "M"
            for j, point in enumerate(approx):
                px = (point[0][0] - x_min) * scale
                py = (point[0][1] - y_min) * scale
                if j == 0:
                    path_d += f"{px:.1f} {py:.1f}"
                else:
                    path_d += f" L{px:.1f} {py:.1f}"
            path_d += " Z"

            print(f"\nContour {idx+1} (eps={eps_factor}, {len(approx)} pts):")
            print(path_d)

    # Best version - use eps=0.01
    print("\n" + "="*70)
    print("RECOMMENDED SVG CODE:")
    print("="*70)

    paths = []
    for contour in large_contours:
        epsilon = 0.01 * cv2.arcLength(contour, True)
        approx = cv2.approxPolyDP(contour, epsilon, True)

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

    print(f'\n<svg viewBox="0 0 {view_w:.0f} {view_h:.0f}" xmlns="http://www.w3.org/2000/svg">')
    for path in paths:
        print(f'  <path d="{path}" fill="currentColor"/>')
    print('</svg>')


if __name__ == "__main__":
    extract_and_trace_logo()
