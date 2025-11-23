"""
Debug script to check PaddleOCR API response format
"""

from paddleocr import PaddleOCR
import cv2
import numpy as np
from pathlib import Path
import json

# Initialize PaddleOCR
print("Initializing PaddleOCR...")
ocr = PaddleOCR(
    use_textline_orientation=True,
    lang='en',
    text_det_thresh=0.3,
    text_det_box_thresh=0.5,
    text_det_unclip_ratio=1.6,
    text_det_limit_side_len=1280
)

# Load test image
img_path = Path("목표 이미지.jpg")
print(f"\nLoading image: {img_path}")

# Read with proper encoding
with open(img_path, 'rb') as f:
    file_bytes = np.frombuffer(f.read(), dtype=np.uint8)
    image = cv2.imdecode(file_bytes, cv2.IMREAD_COLOR)

print(f"Image shape: {image.shape}")

# Run OCR
print("\nRunning OCR...")
result = ocr.predict(image)

# Debug: Print result structure
print(f"\nResult type: {type(result)}")
print(f"Result length: {len(result) if isinstance(result, (list, tuple)) else 'N/A'}")

if isinstance(result, (list, tuple)) and len(result) > 0:
    print(f"\nFirst element type: {type(result[0])}")

    if isinstance(result[0], dict):
        print("\nResult is a dict. Keys:")
        print(result[0].keys())
        print("\nFirst item:")
        print(json.dumps(result[0], indent=2, ensure_ascii=False))
    elif isinstance(result[0], (list, tuple)):
        print(f"\nFirst element is a list/tuple of length: {len(result[0])}")
        if len(result[0]) > 0:
            print(f"First item type: {type(result[0][0])}")
            if isinstance(result[0][0], dict):
                print("\nFirst detection:")
                print(json.dumps(result[0][0], indent=2, ensure_ascii=False))

print(f"\n\nFull result (first 3 items):")
if isinstance(result, (list, tuple)):
    for i, item in enumerate(result[:3]):
        print(f"\nItem {i}:")
        if isinstance(item, dict):
            print(json.dumps(item, indent=2, ensure_ascii=False))
        else:
            print(f"  Type: {type(item)}")
            print(f"  Value: {item}")
