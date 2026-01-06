"""
Extract brand elements (images, fonts, colors) from Vysus Brand Guidelines PDF
"""
import fitz  # PyMuPDF
import os
import json
from collections import Counter

def extract_brand_elements(pdf_path, output_dir):
    """Extract images, fonts, and colors from PDF"""

    os.makedirs(output_dir, exist_ok=True)

    doc = fitz.open(pdf_path)

    extracted_data = {
        "fonts": [],
        "colors": [],
        "images": [],
        "text_samples": []
    }

    all_fonts = []
    all_colors = []

    print(f"Processing {doc.page_count} pages...")

    for page_num in range(doc.page_count):
        page = doc[page_num]

        # Extract images
        image_list = page.get_images(full=True)
        for img_idx, img in enumerate(image_list):
            xref = img[0]
            try:
                base_image = doc.extract_image(xref)
                image_bytes = base_image["image"]
                image_ext = base_image["ext"]
                image_filename = f"brand_image_p{page_num+1}_{img_idx+1}.{image_ext}"
                image_path = os.path.join(output_dir, image_filename)

                with open(image_path, "wb") as img_file:
                    img_file.write(image_bytes)

                extracted_data["images"].append({
                    "page": page_num + 1,
                    "filename": image_filename,
                    "size": len(image_bytes),
                    "format": image_ext
                })
                print(f"  Extracted: {image_filename}")
            except Exception as e:
                print(f"  Could not extract image {img_idx} from page {page_num+1}: {e}")

        # Extract text blocks with font info
        blocks = page.get_text("dict")["blocks"]
        for block in blocks:
            if "lines" in block:
                for line in block["lines"]:
                    for span in line["spans"]:
                        font_name = span.get("font", "Unknown")
                        font_size = span.get("size", 0)
                        color_int = span.get("color", 0)
                        text = span.get("text", "").strip()

                        # Convert color int to hex
                        if isinstance(color_int, int):
                            r = (color_int >> 16) & 255
                            g = (color_int >> 8) & 255
                            b = color_int & 255
                            color_hex = f"#{r:02x}{g:02x}{b:02x}"
                        else:
                            color_hex = "#000000"

                        all_fonts.append(font_name)
                        all_colors.append(color_hex)

                        # Capture text samples for key brand elements
                        if text and len(text) > 2:
                            extracted_data["text_samples"].append({
                                "text": text[:100],
                                "font": font_name,
                                "size": round(font_size, 1),
                                "color": color_hex,
                                "page": page_num + 1
                            })

    # Get unique fonts with counts
    font_counts = Counter(all_fonts)
    extracted_data["fonts"] = [
        {"name": font, "count": count}
        for font, count in font_counts.most_common(20)
    ]

    # Get unique colors with counts
    color_counts = Counter(all_colors)
    extracted_data["colors"] = [
        {"hex": color, "count": count}
        for color, count in color_counts.most_common(30)
    ]

    doc.close()

    # Save extraction report
    report_path = os.path.join(output_dir, "brand_extraction_report.json")
    with open(report_path, "w") as f:
        json.dump(extracted_data, f, indent=2)

    print(f"\nExtraction complete!")
    print(f"  Images extracted: {len(extracted_data['images'])}")
    print(f"  Unique fonts found: {len(extracted_data['fonts'])}")
    print(f"  Unique colors found: {len(extracted_data['colors'])}")
    print(f"  Report saved to: {report_path}")

    return extracted_data


if __name__ == "__main__":
    pdf_path = r"C:\Code\documents\Brand Guidelines\Vysus_Brand_Guidelines-min.pdf"
    output_dir = r"C:\Code\documents\Brand Guidelines\extracted_brand"

    data = extract_brand_elements(pdf_path, output_dir)

    # Print summary
    print("\n" + "="*50)
    print("BRAND TYPOGRAPHY SUMMARY")
    print("="*50)
    print("\nTop Fonts:")
    for font in data["fonts"][:10]:
        print(f"  - {font['name']}: {font['count']} uses")

    print("\nPrimary Colors:")
    for color in data["colors"][:15]:
        print(f"  - {color['hex']}: {color['count']} uses")
