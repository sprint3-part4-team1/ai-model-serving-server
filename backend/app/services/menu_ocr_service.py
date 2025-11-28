from preprocessing.initialization import init
init()

import os
import asyncio
from tqdm import tqdm
from process.image_process import DeepseekOCRProcessor
from preprocessing.image_utils import load_image, draw_bounding_boxes
from preprocessing.engine_utils import stream_generate
from preprocessing.text_utils import re_match

def run_pipeline(input_path, output_path, prompt, crop_mode=True, save_results=True):
    """DeepSeek OCR 전체 파이프라인 실행"""
    os.makedirs(output_path, exist_ok=True)
    os.makedirs(f'{output_path}/images', exist_ok=True)

    # 이미지 로드
    image = load_image(input_path).convert('RGB')

    # 이미지 토큰화
    if '<image>' in prompt:
        image_features = DeepseekOCRProcessor().tokenize_with_images(images=[image], bos=True, eos=True, cropping=crop_mode)
    else:
        image_features = ''

    # OCR 실행
    result_out = asyncio.run(stream_generate(image_features, prompt))

    if save_results and '<image>' in prompt:
        print('='*15 + 'save results:' + '='*15)

        image_draw = image.copy()
        outputs = result_out

        # 원본 결과 저장
        with open(f'{output_path}/result_ori.mmd', 'w', encoding='utf-8') as afile:
            afile.write(outputs)

        # OCR 결과 파싱
        matches_ref, matches_images, matches_other = re_match(outputs)
        result = draw_bounding_boxes(image_draw, matches_ref, output_path)

        # 이미지 치환
        for idx, a_match_image in enumerate(tqdm(matches_images, desc="image")):
            outputs = outputs.replace(a_match_image, f'![](images/{idx}.jpg)\n')

        # 기타 치환
        for idx, a_match_other in enumerate(tqdm(matches_other, desc="other")):
            outputs = outputs.replace(a_match_other, '').replace('\\coloneqq', ':=').replace('\\eqqcolon', '=:')
        
        # 결과 저장
        with open(f'{output_path}/result.mmd', 'w', encoding='utf-8') as afile:
            afile.write(outputs)

        # line_type 처리 알림
        if 'line_type' in outputs:
            print('해당 outputs은 line_type이 포함되어 있습니다. 별도의 처리가 필요합니다!')

        # 최종 결과 이미지 저장
        result.save(f'{output_path}/result_with_boxes.jpg')

    return result_out

def repaint(input_path, schema_path, output_path):
    """
    기존 OCR 결과(schema_path)를 불러와서 좌표를 수정한 뒤 다시 그려 저장하는 함수
    """
    os.makedirs(output_path, exist_ok=True)
    os.makedirs(f'{output_path}/images', exist_ok=True)

    # 이미지 로드
    image = load_image(input_path).convert('RGB')

    # 기존 스키마 불러오기
    with open(schema_path, 'r', encoding='utf-8') as f:
        outputs = f.read()

    # OCR 결과 파싱
    matches_ref, matches_images, matches_other = re_match(outputs)

    # 다시 박스 그리기
    result = draw_bounding_boxes(image.copy(), matches_ref, output_path)

    # 결과 저장
    result.save(f'{output_path}/result_repaint.jpg')
    print(f"Repainted image saved to {output_path}/result_repaint.jpg")

    return result


