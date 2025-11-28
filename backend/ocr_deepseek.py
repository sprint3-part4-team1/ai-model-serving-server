"""
DeepseekOCR for Menu Template Analysis
Optimized for RTX 4080 Super (16GB VRAM)
"""

import os
from PIL import Image
import torch
from transformers import AutoProcessor, AutoModelForVision2Seq
import json
from pathlib import Path


class DeepseekOCRProcessor:
    def __init__(self, use_flash_attention=True):
        """
        Initialize DeepseekOCR with optimal settings for 16GB VRAM

        Args:
            use_flash_attention: Use flash attention for better performance (requires CUDA)
        """
        self.use_flash_attention = use_flash_attention
        self.model = None
        self.processor = None

    def setup_model(self):
        """Setup DeepseekOCR model with optimal configuration for Windows + 4080 Super"""
        model_name = "deepseek-ai/deepseek-vl-1.3b-chat"

        print("Loading DeepseekOCR with HuggingFace (optimized for 16GB VRAM)...")
        print("Using mixed precision (float16) for efficiency...")

        # Load processor
        self.processor = AutoProcessor.from_pretrained(
            model_name,
            trust_remote_code=True
        )

        # Load model with optimal settings for 4080 Super
        load_kwargs = {
            "trust_remote_code": True,
            "torch_dtype": torch.float16,  # Half precision to save memory
            "device_map": "auto",  # Automatically distribute across GPU
            "low_cpu_mem_usage": True,  # Reduce CPU memory usage during loading
        }

        # Try to use flash attention if available (much faster)
        if self.use_flash_attention:
            try:
                load_kwargs["attn_implementation"] = "flash_attention_2"
                print("Attempting to use Flash Attention 2...")
            except Exception as e:
                print(f"Flash Attention not available: {e}")
                print("Using standard attention (slower but works)")

        self.model = AutoModelForVision2Seq.from_pretrained(
            model_name,
            **load_kwargs
        )

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

    def extract_menu_structure(self, image_path, output_json_path=None):
        """
        Extract text, images, and layout from menu template

        Args:
            image_path: Path to menu image
            output_json_path: Optional path to save extracted structure

        Returns:
            dict: Structured data with text boxes, image regions, layout info
        """
        image = Image.open(image_path).convert("RGB")

        # OCR prompt optimized for menu extraction
        prompt = """Analyze this menu template and extract:
1. All text content with exact bounding box coordinates
2. Image/photo regions with bounding boxes
3. Layout structure (sections, columns, alignment)
4. Font styles and sizes (relative)
5. Color scheme

Output in JSON format with this structure:
{
  "layout": {"type": "...", "columns": ...},
  "text_boxes": [{"text": "...", "bbox": [x1,y1,x2,y2], "style": "..."}],
  "image_regions": [{"type": "...", "bbox": [x1,y1,x2,y2]}],
  "color_palette": ["...", "..."]
}"""

        result = self._extract_with_hf(image, prompt)

        # Parse and structure the result
        structured_data = self._parse_ocr_result(result, image.size)

        if output_json_path:
            with open(output_json_path, 'w', encoding='utf-8') as f:
                json.dump(structured_data, f, indent=2, ensure_ascii=False)
            print(f"Structured data saved to: {output_json_path}")

        return structured_data

    def _extract_with_hf(self, image, prompt):
        """Extract using HuggingFace transformers"""
        inputs = self.processor(
            text=prompt,
            images=image,
            return_tensors="pt"
        ).to(self.model.device)

        with torch.no_grad():
            outputs = self.model.generate(
                **inputs,
                max_new_tokens=2048,
                do_sample=True,
                temperature=0.2,
                top_p=0.95
            )

        result = self.processor.batch_decode(
            outputs,
            skip_special_tokens=True
        )[0]

        return result

    def _parse_ocr_result(self, raw_result, image_size):
        """
        Parse OCR result and normalize coordinates

        Args:
            raw_result: Raw text output from model
            image_size: (width, height) of original image

        Returns:
            Structured and normalized data
        """
        width, height = image_size

        # Try to extract JSON from result
        try:
            # Find JSON block in response
            start_idx = raw_result.find('{')
            end_idx = raw_result.rfind('}') + 1

            if start_idx != -1 and end_idx > start_idx:
                json_str = raw_result[start_idx:end_idx]
                data = json.loads(json_str)
            else:
                data = {"raw_output": raw_result}
        except json.JSONDecodeError:
            data = {"raw_output": raw_result}

        # Normalize all bounding boxes to 0-1 range
        if "text_boxes" in data:
            for box in data["text_boxes"]:
                if "bbox" in box:
                    box["bbox_normalized"] = self._normalize_bbox(
                        box["bbox"], width, height
                    )

        if "image_regions" in data:
            for region in data["image_regions"]:
                if "bbox" in region:
                    region["bbox_normalized"] = self._normalize_bbox(
                        region["bbox"], width, height
                    )

        data["image_size"] = {"width": width, "height": height}

        return data

    def _normalize_bbox(self, bbox, width, height):
        """Normalize bbox coordinates to 0-1 range"""
        x1, y1, x2, y2 = bbox
        return [
            x1 / width,
            y1 / height,
            x2 / width,
            y2 / height
        ]

    def visualize_boxes(self, image_path, structured_data, output_path=None):
        """
        Visualize detected boxes on the image

        Args:
            image_path: Path to original image
            structured_data: Output from extract_menu_structure
            output_path: Where to save visualization
        """
        from PIL import ImageDraw, ImageFont

        image = Image.open(image_path).convert("RGB")
        draw = ImageDraw.Draw(image)
        width, height = image.size

        # Draw text boxes in green
        if "text_boxes" in structured_data:
            for box in structured_data["text_boxes"]:
                if "bbox_normalized" in box:
                    x1, y1, x2, y2 = box["bbox_normalized"]
                    coords = [
                        x1 * width, y1 * height,
                        x2 * width, y2 * height
                    ]
                    draw.rectangle(coords, outline="green", width=2)

                    # Draw text label
                    text = box.get("text", "")[:20]
                    draw.text((coords[0], coords[1]-15), text, fill="green")

        # Draw image regions in blue
        if "image_regions" in structured_data:
            for region in structured_data["image_regions"]:
                if "bbox_normalized" in region:
                    x1, y1, x2, y2 = region["bbox_normalized"]
                    coords = [
                        x1 * width, y1 * height,
                        x2 * width, y2 * height
                    ]
                    draw.rectangle(coords, outline="blue", width=3)
                    draw.text((coords[0], coords[1]-15), "IMAGE", fill="blue")

        if output_path:
            image.save(output_path)
            print(f"Visualization saved to: {output_path}")

        return image


def main():
    """Test DeepseekOCR on menu templates"""

    # Initialize processor with 4080 Super optimal settings
    processor = DeepseekOCRProcessor(
        use_flash_attention=True  # Use flash attention if available
    )

    print("Setting up DeepseekOCR...")
    processor.setup_model()

    # Test images
    test_images = [
        "목표 이미지.jpg",
        "목표 이미지-준영.jpg"
    ]

    results_dir = Path("ocr_results")
    results_dir.mkdir(exist_ok=True)

    for img_name in test_images:
        img_path = Path(img_name)
        if not img_path.exists():
            print(f"Skipping {img_name} - file not found")
            continue

        print(f"\n{'='*60}")
        print(f"Processing: {img_name}")
        print(f"{'='*60}")

        # Extract structure
        output_json = results_dir / f"{img_path.stem}_structure.json"
        structured_data = processor.extract_menu_structure(
            str(img_path),
            str(output_json)
        )

        # Visualize
        output_viz = results_dir / f"{img_path.stem}_boxes.jpg"
        processor.visualize_boxes(
            str(img_path),
            structured_data,
            str(output_viz)
        )

        print(f"\nResults:")
        print(f"  JSON: {output_json}")
        print(f"  Visualization: {output_viz}")


if __name__ == "__main__":
    main()
