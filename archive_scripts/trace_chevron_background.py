"""
Trace the Vysus chevron background pattern from the brand guidelines
"""
import cv2
import numpy as np
import fitz

def extract_and_trace_chevrons():
    """Extract the chevron shapes from page 4 background"""

    pdf_path = r"C:\Code\documents\Brand Guidelines\Vysus_Brand_Guidelines-min.pdf"
    output_dir = r"C:\Code\documents\Brand Guidelines\extracted_brand\logo_renders"

    # Use the extracted background image directly
    # Page 4 has the clearest chevron pattern
    img_path = r"C:\Code\documents\Brand Guidelines\extracted_brand\brand_image_p4_1.png"

    img = cv2.imread(img_path)
    if img is None:
        print(f"Could not load {img_path}")
        return

    height, width = img.shape[:2]
    print(f"Image size: {width} x {height}")

    # Convert to HSV to detect the dark chevron shapes
    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)

    # The chevrons are darker teal areas
    # Look for dark regions (low value in HSV)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    # Save grayscale for inspection
    cv2.imwrite(f"{output_dir}/chevron_gray.png", gray)

    # The dark chevrons are roughly < 80 in grayscale
    # Try multiple thresholds
    for thresh_val in [60, 70, 80, 90]:
        _, binary = cv2.threshold(gray, thresh_val, 255, cv2.THRESH_BINARY_INV)
        cv2.imwrite(f"{output_dir}/chevron_binary_{thresh_val}.png", binary)

        contours, _ = cv2.findContours(binary, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        # Filter large contours
        large = [c for c in contours if cv2.contourArea(c) > 10000]
        print(f"\nThreshold {thresh_val}: Found {len(large)} large contours")

        for i, c in enumerate(large):
            area = cv2.contourArea(c)
            x, y, w, h = cv2.boundingRect(c)
            print(f"  {i+1}. area={area:.0f}, pos=({x},{y}), size=({w}x{h})")

    # Use threshold 70 which should capture the dark chevrons
    _, binary = cv2.threshold(gray, 70, 255, cv2.THRESH_BINARY_INV)
    contours, _ = cv2.findContours(binary, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    large_contours = [c for c in contours if cv2.contourArea(c) > 10000]

    if not large_contours:
        print("No chevron shapes found!")
        return

    # Sort by x position (left to right)
    large_contours.sort(key=lambda c: cv2.boundingRect(c)[0])

    print(f"\n{'='*70}")
    print("TRACING CHEVRON SHAPES")
    print('='*70)

    # Scale to viewBox 0 0 100 (height proportional)
    scale_x = 100 / width
    scale_y = 100 * (height / width) / height  # Keep aspect ratio based on width=100
    view_h = height * scale_x

    print(f"ViewBox: 0 0 100 {view_h:.1f}")

    paths = []
    for idx, contour in enumerate(large_contours):
        # Simplify
        epsilon = 0.005 * cv2.arcLength(contour, True)
        approx = cv2.approxPolyDP(contour, epsilon, True)

        path_d = "M"
        for j, point in enumerate(approx):
            px = point[0][0] * scale_x
            py = point[0][1] * scale_x  # Use same scale for both to maintain aspect
            if j == 0:
                path_d += f"{px:.1f} {py:.1f}"
            else:
                path_d += f" L{px:.1f} {py:.1f}"
        path_d += " Z"

        print(f"\nChevron {idx+1} ({len(approx)} points):")
        print(path_d)
        paths.append(path_d)

    # Draw contours on image for verification
    debug_img = img.copy()
    cv2.drawContours(debug_img, large_contours, -1, (0, 0, 255), 3)
    cv2.imwrite(f"{output_dir}/chevron_contours.png", debug_img)

    print(f"\n{'='*70}")
    print("SVG CODE FOR CSS BACKGROUND:")
    print('='*70)

    # Generate inline SVG
    svg = f'''<svg viewBox="0 0 100 {view_h:.1f}" xmlns="http://www.w3.org/2000/svg" preserveAspectRatio="xMidYMid slice">
  <defs>
    <linearGradient id="bgGrad" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#00E3A9"/>
      <stop offset="50%" stop-color="#008a6e"/>
      <stop offset="100%" stop-color="#005454"/>
    </linearGradient>
  </defs>
  <rect width="100%" height="100%" fill="url(#bgGrad)"/>'''

    for i, path in enumerate(paths):
        svg += f'\n  <path d="{path}" fill="#003535" opacity="0.6"/>'

    svg += '\n</svg>'

    print(svg)

    # Save SVG file
    with open(f"{output_dir}/chevron_background.svg", 'w') as f:
        f.write(svg)
    print(f"\nSaved to: {output_dir}/chevron_background.svg")


if __name__ == "__main__":
    extract_and_trace_chevrons()
