from pdf2image import convert_from_path
import pytesseract
from PIL import Image

def pdf_to_text(pdf_path: str) -> str:
    """
    스캔된 PDF 파일을 이미지로 변환하고 Tesseract로 텍스트 추출
    """
    try:
        # 1. PDF → 이미지 (300dpi)
        images = convert_from_path(pdf_path, dpi=300)

        # 2. 각 페이지에서 텍스트 추출
        full_text = ""
        for i, img in enumerate(images):
            text = pytesseract.image_to_string(img, lang="kor")
            full_text += f"\n\n----- [페이지 {i+1}] -----\n{text}"

        return full_text.strip()

    except Exception as e:
        raise RuntimeError(f"OCR 실패: {e}")
