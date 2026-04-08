"""Element picker endpoint — captures UI element at cursor position."""
from fastapi import APIRouter
from rpa_studio.api.schemas import ElementPickerResult

router = APIRouter()


@router.post("/element-picker/pick")
async def pick_element_at_cursor():
    """Capture UI element info at current cursor position.

    The frontend should call this while the user hovers over the target element.
    Uses pywinauto to identify the element under the cursor.
    """
    import ctypes
    import ctypes.wintypes

    result = ElementPickerResult()

    try:
        from pywinauto import Desktop

        # Get cursor position
        pos = ctypes.wintypes.POINT()
        ctypes.windll.user32.GetCursorPos(ctypes.byref(pos))
        x, y = pos.x, pos.y

        desktop = Desktop(backend="uia")
        element = desktop.from_point(x, y)

        if element:
            info = element.element_info
            result = ElementPickerResult(
                name=info.name or "",
                control_type=info.control_type or "",
                automation_id=info.automation_id or "",
                class_name=info.class_name or "",
            )
    except Exception as e:
        result = ElementPickerResult(name=f"오류: {str(e)}")

    return result


@router.get("/element-picker/at/{x}/{y}")
async def get_element_at_position(x: int, y: int):
    """Get UI element info at specific screen coordinates."""
    try:
        from pywinauto import Desktop

        desktop = Desktop(backend="uia")
        element = desktop.from_point(x, y)

        if element:
            info = element.element_info
            rect = element.rectangle()
            return {
                "name": info.name or "",
                "control_type": info.control_type or "",
                "automation_id": info.automation_id or "",
                "class_name": info.class_name or "",
                "rect": {
                    "left": rect.left,
                    "top": rect.top,
                    "right": rect.right,
                    "bottom": rect.bottom,
                    "width": rect.width(),
                    "height": rect.height(),
                },
            }
        return {"name": "", "control_type": "", "error": "요소를 찾을 수 없어요"}
    except Exception as e:
        return {"error": str(e)}
