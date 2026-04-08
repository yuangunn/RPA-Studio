from __future__ import annotations
from pathlib import Path
import numpy as np
from rpa_studio.actions.base import ActionHandler
from rpa_studio.models import ActionType, Step
from rpa_studio.engine.context import ExecutionContext


class ImageSearchHandler(ActionHandler):
    action_type = ActionType.IMAGE_SEARCH

    def execute(self, step: Step, context: ExecutionContext):
        import cv2
        import mss

        template_path = context.resolve(step.params.get("template_path", ""))
        confidence = float(step.params.get("confidence", 0.85))
        var_name = step.params.get("save_as", "이미지위치")
        context.add_log(f"이미지 찾기: {Path(template_path).name} (정확도 {confidence})")

        # Capture screen
        with mss.mss() as sct:
            monitor = sct.monitors[1]  # Primary monitor
            screenshot = np.array(sct.grab(monitor))
            screenshot = cv2.cvtColor(screenshot, cv2.COLOR_BGRA2BGR)

        # Load template
        if not Path(template_path).exists():
            raise FileNotFoundError(f"템플릿 이미지를 찾을 수 없어요: {template_path}")
        template = cv2.imread(template_path)
        if template is None:
            raise ValueError(f"이미지를 읽을 수 없어요: {template_path}")

        # Template matching
        result = cv2.matchTemplate(screenshot, template, cv2.TM_CCOEFF_NORMED)
        min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)

        if max_val >= confidence:
            h, w = template.shape[:2]
            center_x = max_loc[0] + w // 2
            center_y = max_loc[1] + h // 2
            match_info = {
                "found": True,
                "x": center_x,
                "y": center_y,
                "width": w,
                "height": h,
                "confidence": round(max_val, 3),
            }
            context.variables[var_name] = match_info
            context.add_log(f"✅ 이미지 발견: ({center_x}, {center_y}) 정확도 {max_val:.3f}")
            return match_info
        else:
            context.variables[var_name] = {"found": False}
            context.add_log(f"❌ 이미지를 찾지 못했어요 (최대 정확도: {max_val:.3f})")
            return {"found": False, "max_confidence": round(max_val, 3)}
