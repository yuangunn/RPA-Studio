from __future__ import annotations
import numpy as np
from rpa_studio.actions.base import ActionHandler
from rpa_studio.models import ActionType, Step
from rpa_studio.engine.context import ExecutionContext


class OCRReadHandler(ActionHandler):
    action_type = ActionType.OCR_READ

    def execute(self, step: Step, context: ExecutionContext):
        import mss
        import cv2

        region = step.params.get("region", None)  # (x, y, w, h) or None for full screen
        lang = step.params.get("lang", "kor+eng")
        var_name = step.params.get("save_as", "읽은텍스트")
        context.add_log(f"텍스트 읽기 (OCR): 언어={lang}")

        # Capture screen or region
        with mss.mss() as sct:
            if region:
                monitor = {"left": region[0], "top": region[1],
                          "width": region[2], "height": region[3]}
            else:
                monitor = sct.monitors[1]
            screenshot = np.array(sct.grab(monitor))
            screenshot = cv2.cvtColor(screenshot, cv2.COLOR_BGRA2BGR)

        # Try pytesseract
        try:
            import pytesseract
            from PIL import Image
            pil_image = Image.fromarray(cv2.cvtColor(screenshot, cv2.COLOR_BGR2RGB))
            text = pytesseract.image_to_string(pil_image, lang=lang).strip()
            context.variables[var_name] = text
            preview = text[:50] + "..." if len(text) > 50 else text
            context.add_log(f"✅ OCR 결과: {preview}")
            return {"text": text}
        except Exception as e:
            msg = str(e)
            if "tesseract" in msg.lower():
                context.add_log("❌ Tesseract OCR이 설치되지 않았어요. https://github.com/tesseract-ocr/tesseract 에서 설치해주세요.")
            else:
                context.add_log(f"❌ OCR 실패: {msg}")
            context.variables[var_name] = ""
            return {"text": "", "error": msg}
