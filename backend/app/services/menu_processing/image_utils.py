from PIL import Image, ImageOps, ImageDraw, ImageFont
import numpy as np

def load_image(image_path):
    try:
        image = Image.open(image_path)        
        corrected_image = ImageOps.exif_transpose(image)
        return corrected_image        
    except Exception as e:
        print(f"error: {e}")
        try:
            return Image.open(image_path)
        except:
            return None

def normalize_to_pixel(bbox_list, image_width, image_height):
    """
    DeepSeek-OCR 스키마 좌표(0~999 범위)를 실제 이미지 픽셀 좌표로 변환
    """
    pixel_bboxes = []
    for bbox in bbox_list:
        x1, y1, x2, y2 = bbox
        px1 = int(x1 / 999 * image_width)
        py1 = int(y1 / 999 * image_height)
        px2 = int(x2 / 999 * image_width)
        py2 = int(y2 / 999 * image_height)
        pixel_bboxes.append([px1, py1, px2, py2])
    return pixel_bboxes

def extract_coordinates_and_label(ref_text, image_width, image_height):
    try:
        label_type = ref_text[1]
        cor_list = eval(ref_text[2])
        # ✅ 좌표 변환 적용
        cor_list = normalize_to_pixel(cor_list, image_width, image_height)
        return (label_type, cor_list)
    except Exception as e:
        print(e)
        return None

def draw_bounding_boxes(image, refs, output_path=None):
    image_width, image_height = image.size
    img_draw = image.copy()
    draw = ImageDraw.Draw(img_draw)

    overlay = Image.new('RGBA', img_draw.size, (0, 0, 0, 0))
    draw2 = ImageDraw.Draw(overlay)
    font = ImageFont.load_default()

    img_idx = 0
    for ref in refs:
        try:
            result = extract_coordinates_and_label(ref, image_width, image_height)
            if result:
                label_type, points_list = result
                color = (np.random.randint(0, 200), np.random.randint(0, 200), np.random.randint(0, 255))
                color_a = color + (20, )

                for points in points_list:
                    x1, y1, x2, y2 = points

                    if label_type == 'image' and output_path:
                        try:
                            cropped = image.crop((x1, y1, x2, y2))
                            cropped.save(f"{output_path}/images/{img_idx}.jpg")
                        except Exception as e:
                            print(e)
                        img_idx += 1

                    try:
                        if label_type == 'title':
                            draw.rectangle([x1, y1, x2, y2], outline=color, width=4)
                            draw2.rectangle([x1, y1, x2, y2], fill=color_a, outline=(0, 0, 0, 0), width=1)
                        else:
                            draw.rectangle([x1, y1, x2, y2], outline=color, width=2)
                            draw2.rectangle([x1, y1, x2, y2], fill=color_a, outline=(0, 0, 0, 0), width=1)

                        text_x = x1
                        text_y = max(0, y1 - 15)
                        text_bbox = draw.textbbox((0, 0), label_type, font=font)
                        text_width = text_bbox[2] - text_bbox[0]
                        text_height = text_bbox[3] - text_bbox[1]
                        draw.rectangle([text_x, text_y, text_x + text_width, text_y + text_height],
                                       fill=(255, 255, 255, 30))
                        draw.text((text_x, text_y), label_type, font=font, fill=color)
                    except:
                        pass
        except:
            continue

    img_draw.paste(overlay, (0, 0), overlay)
    return img_draw
