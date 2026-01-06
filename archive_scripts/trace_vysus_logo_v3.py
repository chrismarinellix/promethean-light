"""
Trace the Vysus logo - using the existing closeup image that shows the marque
"""
import cv2
import numpy as np

def trace_from_existing_closeup():
    """Trace from the existing closeup that clearly shows the logo"""

    # Use the existing closeup image which clearly shows the marque
    logo_path = r"C:\Code\documents\Brand Guidelines\extracted_brand\logo_renders\vysus_marque_closeup.png"

    img = cv2.imread(logo_path)
    if img is None:
        print("Could not load image")
        return

    height, width = img.shape[:2]
    print(f"Image size: {width} x {height}")

    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    # The logo is black on white - threshold to find black areas
    # Use a higher threshold since the logo is very dark
    _, binary = cv2.threshold(gray, 100, 255, cv2.THRESH_BINARY_INV)

    # Save binary for inspection
    cv2.imwrite(r"C:\Code\documents\Brand Guidelines\extracted_brand\logo_renders\binary_debug.png", binary)

    # Find contours
    contours, hierarchy = cv2.findContours(binary, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    print(f"Found {len(contours)} contours total")

    # Filter to large contours and sort by area
    contour_info = []
    for i, c in enumerate(contours):
        area = cv2.contourArea(c)
        x, y, w, h = cv2.boundingRect(c)
        contour_info.append((i, area, x, y, w, h, c))

    # Sort by area descending
    contour_info.sort(key=lambda x: x[1], reverse=True)

    print("\nTop 10 contours by area:")
    for i, (idx, area, x, y, w, h, c) in enumerate(contour_info[:10]):
        print(f"  {i+1}. area={area:.0f}, pos=({x},{y}), size=({w}x{h})")

    # The two logo parts should be the largest contours in the middle-left of the image
    # Filter by position - logo is in left half, middle vertically
    logo_contours = []
    for idx, area, x, y, w, h, c in contour_info:
        # Must be significant size
        if area < 10000:
            continue
        # Must be in middle area (not at very top where text labels are)
        if y < height * 0.2:
            continue
        # Must be reasonably sized (not too small)
        if w < 50 or h < 50:
            continue

        print(f"  Selected: area={area:.0f}, pos=({x},{y}), size=({w}x{h})")
        logo_contours.append(c)

        if len(logo_contours) >= 2:
            break

    if len(logo_contours) < 2:
        print(f"\nOnly found {len(logo_contours)} logo parts, need 2")
        # Show what we got
        debug_img = img.copy()
        cv2.drawContours(debug_img, logo_contours, -1, (0, 255, 0), 3)
        cv2.imwrite(r"C:\Code\documents\Brand Guidelines\extracted_brand\logo_renders\contours_debug.png", debug_img)
        return

    # Sort left to right
    logo_contours.sort(key=lambda c: cv2.boundingRect(c)[0])

    # Get total bounds
    all_points = np.vstack(logo_contours)
    x_min, y_min, total_w, total_h = cv2.boundingRect(all_points)
    print(f"\nTotal logo bounds: ({x_min}, {y_min}) size ({total_w} x {total_h})")

    # Scale to 100 units wide
    scale = 100 / total_w
    view_h = total_h * scale

    print(f"ViewBox: 0 0 100 {view_h:.1f}")

    print("\n" + "="*70)
    print("SVG PATHS:")
    print("="*70)

    paths = []
    for idx, contour in enumerate(logo_contours):
        # Use moderate simplification
        epsilon = 0.008 * cv2.arcLength(contour, True)
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

        print(f"\nPath {idx+1} ({len(approx)} points):")
        print(path_d)
        paths.append(path_d)

    print("\n" + "="*70)
    print("FULL SVG CODE FOR HTML:")
    print("="*70)
    print(f'''
<svg class="marque" viewBox="0 0 100 {view_h:.0f}" xmlns="http://www.w3.org/2000/svg">
  <path d="{paths[0]}" fill="currentColor"/>
  <path d="{paths[1]}" fill="currentColor"/>
</svg>
''')

    # Save debug image with contours
    debug_img = img.copy()
    cv2.drawContours(debug_img, logo_contours, -1, (0, 255, 0), 3)
    cv2.imwrite(r"C:\Code\documents\Brand Guidelines\extracted_brand\logo_renders\contours_debug.png", debug_img)
    print("\nSaved debug image with contours highlighted")


if __name__ == "__main__":
    trace_from_existing_closeup()
