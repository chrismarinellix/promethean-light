"""
Trace the Vysus logo from the extracted PNG and convert to SVG path
"""
import cv2
import numpy as np
from PIL import Image
import svgwrite

def trace_logo_to_svg(image_path, output_svg_path):
    """
    Trace the black shapes in the logo image and convert to SVG paths
    """
    # Load image
    img = cv2.imread(image_path)
    if img is None:
        print(f"Could not load image: {image_path}")
        return

    # Convert to grayscale
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    # Threshold to get binary image (black shapes on white background)
    # The logo is black (#1d1d1b) on white, so we invert
    _, binary = cv2.threshold(gray, 50, 255, cv2.THRESH_BINARY_INV)

    # Find contours
    contours, hierarchy = cv2.findContours(binary, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    print(f"Found {len(contours)} contours")

    # Get image dimensions
    height, width = binary.shape
    print(f"Image size: {width} x {height}")

    # Filter to significant contours (the two logo parts)
    significant_contours = []
    for i, contour in enumerate(contours):
        area = cv2.contourArea(contour)
        if area > 1000:  # Filter small noise
            x, y, w, h = cv2.boundingRect(contour)
            print(f"Contour {i}: area={area}, bounds=({x},{y},{w},{h})")
            significant_contours.append(contour)

    if not significant_contours:
        print("No significant contours found")
        return

    # Find bounding box of all significant contours
    all_points = np.vstack(significant_contours)
    x_min, y_min, total_w, total_h = cv2.boundingRect(all_points)

    print(f"\nTotal logo bounds: ({x_min}, {y_min}) to ({x_min+total_w}, {y_min+total_h})")

    # Create SVG
    # Normalize to 100x100 viewBox
    scale = 100 / max(total_w, total_h)

    svg_paths = []

    for contour in significant_contours:
        # Simplify contour
        epsilon = 0.002 * cv2.arcLength(contour, True)
        approx = cv2.approxPolyDP(contour, epsilon, True)

        # Convert to SVG path
        path_d = "M"
        for j, point in enumerate(approx):
            px = (point[0][0] - x_min) * scale
            py = (point[0][1] - y_min) * scale
            if j == 0:
                path_d += f"{px:.1f} {py:.1f}"
            else:
                path_d += f" L{px:.1f} {py:.1f}"
        path_d += " Z"
        svg_paths.append(path_d)

    # Write SVG file
    dwg = svgwrite.Drawing(output_svg_path, size=('100px', '100px'), viewBox='0 0 100 100')
    for path_d in svg_paths:
        dwg.add(dwg.path(d=path_d, fill='black'))
    dwg.save()

    print(f"\nSVG saved to: {output_svg_path}")

    # Also print the path data for direct use in HTML
    print("\n" + "="*60)
    print("SVG PATH DATA (copy this into HTML):")
    print("="*60)
    for i, path_d in enumerate(svg_paths):
        print(f"\nPath {i+1}:")
        print(path_d)

    return svg_paths


def trace_logo_precise(image_path):
    """
    More precise tracing with curve fitting
    """
    img = cv2.imread(image_path)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    _, binary = cv2.threshold(gray, 50, 255, cv2.THRESH_BINARY_INV)

    contours, _ = cv2.findContours(binary, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)

    # Get only large contours
    large_contours = [c for c in contours if cv2.contourArea(c) > 1000]
    large_contours.sort(key=lambda c: cv2.boundingRect(c)[0])  # Sort left to right

    print(f"\nFound {len(large_contours)} logo parts")

    # Get total bounds
    all_points = np.vstack(large_contours)
    x_min, y_min, total_w, total_h = cv2.boundingRect(all_points)

    # Normalize scale
    scale = 100 / max(total_w, total_h)

    print("\n" + "="*60)
    print("PRECISE SVG PATHS:")
    print("="*60)

    for idx, contour in enumerate(large_contours):
        # Get bounding rect for this shape
        x, y, w, h = cv2.boundingRect(contour)
        print(f"\nShape {idx+1}: position ({x-x_min}, {y-y_min}), size ({w}, {h})")

        # Use different approximation levels
        for eps_factor in [0.001, 0.002, 0.005]:
            epsilon = eps_factor * cv2.arcLength(contour, True)
            approx = cv2.approxPolyDP(contour, epsilon, True)

            path_d = "M"
            for j, point in enumerate(approx):
                px = (point[0][0] - x_min) * scale
                py = (point[0][1] - y_min) * scale
                if j == 0:
                    path_d += f"{px:.2f} {py:.2f}"
                else:
                    path_d += f" L{px:.2f} {py:.2f}"
            path_d += " Z"

            print(f"  eps={eps_factor} ({len(approx)} points): {path_d[:80]}...")


if __name__ == "__main__":
    image_path = r"C:\Code\documents\Brand Guidelines\extracted_brand\logo_renders\vysus_marque_closeup.png"
    output_svg = r"C:\Code\documents\Brand Guidelines\extracted_brand\vysus_marque.svg"

    paths = trace_logo_to_svg(image_path, output_svg)

    print("\n\n")
    trace_logo_precise(image_path)
