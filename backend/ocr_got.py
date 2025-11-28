"""
GOT-OCR 2.0 for Menu Template Analysis
More accurate OCR with better bounding box detection
Optimized for RTX 4080 Super (16GB VRAM)
"""

import os
from PIL import Image, ImageDraw, ImageFont
import torch
from transformers import AutoModel, AutoTokenizer
import json
from pathlib import Path
import cv2
import numpy as np


class GOT_OCRProcessor:
    def __init__(self):
        """
        Initialize GOT-OCR 2.0 with optimal settings for 16GB VRAM
        """
        self.model = None
        self.tokenizer = None

    def setup_model(self):
        """Setup GOT-OCR model"""
        model_name = "stepfun-ai/GOT-OCR2_0"

        print("Loading GOT-OCR 2.0 (optimized for 16GB VRAM)...")
        print("Using mixed precision (float16) for efficiency...")

        try:
            # Load tokenizer
            self.tokenizer = AutoTokenizer.from_pretrained(
                model_name,
                trust_remote_code=True
            )

            # Load model with optimal settings
            self.model = AutoModel.from_pretrained(
                model_name,
                trust_remote_code=True,
                torch_dtype=torch.float16,
                device_map="auto",
                low_cpu_mem_usage=True
            ).eval()

            # Check VRAM usage
            if torch.cuda.is_available():
                allocated = torch.cuda.memory_allocated() / 1024**3
                reserved = torch.cuda.memory_reserved() / 1024**3
                print(f"\nGPU Memory Usage:")
                print(f"  Allocated: {allocated:.2f} GB")
                print(f"  Reserved: {reserved:.2f} GB")
                print(f"  Available: {16 - reserved:.2f} GB remaining")

            print("Model loaded successfully!\n")
            return True

        except Exception as e:
            print(f"Error loading GOT-OCR: {e}")
            print("\nFalling back to PaddleOCR with custom refinement...")
            return False

    def extract_menu_structure_got(self, image_path, output_json_path=None):
        """
        Extract text and layout using GOT-OCR 2.0

        Args:
            image_path: Path to menu image
            output_json_path: Optional path to save extracted structure

        Returns:
            dict: Structured data with text boxes, layout info
        """
        if self.model is None:
            print("Model not loaded. Call setup_model() first.")
            return None

        # Get image size
        image_pil = Image.open(image_path).convert("RGB")
        width, height = image_pil.size

        # GOT-OCR 2.0 expects image path, not PIL Image
        print("\n[1/3] Running OCR with bbox detection...")
        result_ocr = self.model.chat(
            self.tokenizer,
            image_path,  # Pass path, not PIL Image
            ocr_type='ocr',  # Standard OCR
            render=False,
            gradio_input=False
        )

        print("[2/3] Running formatted OCR...")
        result_format = self.model.chat(
            self.tokenizer,
            image_path,  # Pass path, not PIL Image
            ocr_type='format',  # Formatted output
            render=False,
            gradio_input=False
        )

        # Parse results
        structured_data = {
            "image_size": {"width": width, "height": height},
            "ocr_result": result_ocr,
            "formatted_result": result_format,
            "text_boxes": [],
            "layout": {}
        }

        print(f"[3/3] Parsing results...")
        print(f"\nOCR Result length: {len(result_ocr)} chars")
        print(f"Format Result length: {len(result_format)} chars")

        if output_json_path:
            with open(output_json_path, 'w', encoding='utf-8') as f:
                json.dump(structured_data, f, indent=2, ensure_ascii=False)
            print(f"Structured data saved to: {output_json_path}")

        # Also save raw text
        raw_text_path = str(output_json_path).replace('.json', '_raw.txt')
        with open(raw_text_path, 'w', encoding='utf-8') as f:
            f.write("=== OCR Result ===\n")
            f.write(result_ocr)
            f.write("\n\n=== Formatted Result ===\n")
            f.write(result_format)
        print(f"Raw text saved to: {raw_text_path}")

        return structured_data

    def _parse_got_result(self, raw_result, image_size):
        """Parse GOT-OCR result"""
        width, height = image_size

        # GOT-OCR returns structured text, we need to extract boxes
        data = {
            "raw_output": raw_result,
            "image_size": {"width": width, "height": height},
            "text_boxes": []
        }

        return data


class PaddleOCRRefined:
    """
    PaddleOCR with custom refinements for better bounding box accuracy
    """
    def __init__(self):
        self.ocr = None

    def setup_model(self):
        """Setup PaddleOCR with optimal settings"""
        try:
            from paddleocr import PaddleOCR

            print("Loading PaddleOCR with custom refinements...")

            # Initialize with optimal parameters for menu detection
            self.ocr = PaddleOCR(
                use_textline_orientation=True,  # Detect rotated text
                lang='en',  # English + Korean multi-language support
                text_det_thresh=0.3,  # Lower threshold for better detection
                text_det_box_thresh=0.5,  # Box threshold
                text_det_unclip_ratio=1.6,  # Expand detected boxes
                text_det_limit_side_len=1280  # Process high-res images
            )

            print("PaddleOCR loaded successfully!\n")
            return True

        except Exception as e:
            print(f"Error loading PaddleOCR: {e}")
            return False

    def extract_menu_structure(self, image_path, output_json_path=None):
        """
        Extract text, images, and layout from menu with refined detection

        Args:
            image_path: Path to menu image
            output_json_path: Optional path to save extracted structure

        Returns:
            dict: Structured data with text boxes, image regions, layout info
        """
        # Read image with proper encoding for Korean filenames
        # Use numpy to read file first, then decode with cv2
        with open(image_path, 'rb') as f:
            file_bytes = np.frombuffer(f.read(), dtype=np.uint8)
            image = cv2.imdecode(file_bytes, cv2.IMREAD_COLOR)

        if image is None:
            print(f"Error: Could not read image {image_path}")
            return None

        image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        height, width = image.shape[:2]

        # Run OCR on the image array (not path, to avoid encoding issues)
        result = self.ocr.predict(image)

        # Extract text boxes from OCRResult object
        text_boxes = []
        if result and len(result) > 0:
            ocr_result = result[0]  # Get first result

            # New PaddleOCR API returns OCRResult object
            rec_texts = ocr_result.get('rec_texts', [])
            rec_scores = ocr_result.get('rec_scores', [])
            rec_polys = ocr_result.get('rec_polys', [])

            for i, (text, score, poly) in enumerate(zip(rec_texts, rec_scores, rec_polys)):
                if not text or len(poly) == 0:
                    continue

                # Convert polygon to list if numpy array
                if hasattr(poly, 'tolist'):
                    poly = poly.tolist()

                # Convert to bbox format [x1, y1, x2, y2]
                x_coords = [p[0] for p in poly]
                y_coords = [p[1] for p in poly]
                bbox = [min(x_coords), min(y_coords), max(x_coords), max(y_coords)]

                # Normalize coordinates
                bbox_norm = [
                    bbox[0] / width,
                    bbox[1] / height,
                    bbox[2] / width,
                    bbox[3] / height
                ]

                text_boxes.append({
                    "text": text,
                    "bbox": bbox,
                    "bbox_normalized": bbox_norm,
                    "confidence": float(score),
                    "polygon": poly  # Keep original polygon for accurate positioning
                })

        # Detect image regions (areas without text)
        image_regions = self._detect_image_regions(image, text_boxes, width, height)

        # Analyze layout structure
        layout = self._analyze_layout(text_boxes, image_regions, width, height)

        structured_data = {
            "image_size": {"width": width, "height": height},
            "layout": layout,
            "text_boxes": text_boxes,
            "image_regions": image_regions,
            "total_text_boxes": len(text_boxes),
            "total_image_regions": len(image_regions)
        }

        if output_json_path:
            with open(output_json_path, 'w', encoding='utf-8') as f:
                json.dump(structured_data, f, indent=2, ensure_ascii=False)
            print(f"Structured data saved to: {output_json_path}")

        return structured_data

    def _detect_image_regions(self, image, text_boxes, width, height):
        """
        Detect image/photo regions by finding large areas without text
        """
        # Create mask of text areas
        mask = np.zeros((height, width), dtype=np.uint8)

        for text_box in text_boxes:
            polygon = text_box["polygon"]
            pts = np.array(polygon, dtype=np.int32)
            cv2.fillPoly(mask, [pts], 255)

        # Invert mask to get non-text areas
        non_text_mask = cv2.bitwise_not(mask)

        # Find contours of large regions
        contours, _ = cv2.findContours(non_text_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        image_regions = []
        min_region_area = (width * height) * 0.02  # At least 2% of image

        for contour in contours:
            area = cv2.contourArea(contour)

            if area > min_region_area:
                x, y, w, h = cv2.boundingRect(contour)

                # Check if region likely contains an image (aspect ratio, size, etc.)
                aspect_ratio = w / h if h > 0 else 0

                if 0.5 < aspect_ratio < 2.5:  # Reasonable aspect ratio
                    bbox = [x, y, x + w, y + h]
                    bbox_norm = [
                        x / width,
                        y / height,
                        (x + w) / width,
                        (y + h) / height
                    ]

                    image_regions.append({
                        "type": "potential_image",
                        "bbox": bbox,
                        "bbox_normalized": bbox_norm,
                        "area": area,
                        "aspect_ratio": aspect_ratio
                    })

        return image_regions

    def _analyze_layout(self, text_boxes, image_regions, width, height):
        """Analyze overall layout structure"""

        # Detect columns by clustering x-coordinates
        if text_boxes:
            x_centers = [(box["bbox"][0] + box["bbox"][2]) / 2 for box in text_boxes]
            x_centers.sort()

            # Simple column detection: check for gaps in x distribution
            gaps = []
            for i in range(len(x_centers) - 1):
                gap = x_centers[i + 1] - x_centers[i]
                if gap > width * 0.1:  # Gap > 10% of width
                    gaps.append((x_centers[i], x_centers[i + 1]))

            num_columns = len(gaps) + 1
        else:
            num_columns = 1

        return {
            "estimated_columns": num_columns,
            "layout_type": "multi_column" if num_columns > 1 else "single_column"
        }

    def visualize_boxes(self, image_path, structured_data, output_path=None):
        """
        Visualize detected boxes on the image

        Args:
            image_path: Path to original image
            structured_data: Output from extract_menu_structure
            output_path: Where to save visualization
        """
        image = Image.open(image_path).convert("RGB")
        draw = ImageDraw.Draw(image)
        width, height = image.size

        # Draw text boxes in green
        for box in structured_data.get("text_boxes", []):
            if "bbox" in box:
                coords = box["bbox"]
                draw.rectangle(coords, outline="green", width=2)

                # Draw text label
                text = box.get("text", "")[:15]
                draw.text((coords[0], max(0, coords[1]-15)), text, fill="green")

        # Draw image regions in blue
        for region in structured_data.get("image_regions", []):
            if "bbox" in region:
                coords = region["bbox"]
                draw.rectangle(coords, outline="blue", width=3)
                draw.text((coords[0]+5, coords[1]+5), "IMAGE", fill="blue")

        if output_path:
            image.save(output_path)
            print(f"Visualization saved to: {output_path}")

        return image


def main():
    """Test OCR on menu templates"""

    # Try GOT-OCR first, fallback to PaddleOCR
    print("="*60)
    print("Initializing OCR System")
    print("="*60)

    use_got = True  # Enable GOT-OCR 2.0
    if use_got:
        processor = GOT_OCRProcessor()
        if processor.setup_model():
            print("Using GOT-OCR 2.0")
        else:
            use_got = False

    if not use_got:
        processor = PaddleOCRRefined()
        if not processor.setup_model():
            print("Failed to load any OCR system!")
            return
        print("Using PaddleOCR with refinements")

    # Test images - use Path for proper encoding
    # Use parent directory since script runs from backend/
    test_images = [
        Path("..") / "목표 이미지.jpg",
        Path("..") / "목표 이미지-준영.jpg"
    ]

    results_dir = Path("ocr_results")
    results_dir.mkdir(exist_ok=True)

    for img_path in test_images:
        if not img_path.exists():
            print(f"Skipping {img_path} - file not found")
            continue

        print(f"\n{'='*60}")
        print(f"Processing: {img_path.name}")
        print(f"{'='*60}")

        # Extract structure
        output_json = results_dir / f"{img_path.stem}_structure.json"
        if use_got:
            structured_data = processor.extract_menu_structure_got(
                str(img_path),
                str(output_json)
            )
        else:
            structured_data = processor.extract_menu_structure(
                str(img_path),
                str(output_json)
            )

            # Visualize (only for PaddleOCR)
            output_viz = results_dir / f"{img_path.stem}_boxes.jpg"
            processor.visualize_boxes(
                str(img_path),
                structured_data,
                str(output_viz)
            )

        print(f"\nResults:")
        print(f"  JSON: {output_json}")
        print(f"  Visualization: {output_viz}")
        print(f"  Text boxes detected: {structured_data.get('total_text_boxes', 0)}")
        print(f"  Image regions detected: {structured_data.get('total_image_regions', 0)}")


if __name__ == "__main__":
    main()
