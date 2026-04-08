"""Element picker endpoint — waits for user click, then captures UI element."""
import threading
import asyncio
from fastapi import APIRouter
from rpa_studio.api.schemas import ElementPickerResult

router = APIRouter()

# Shared state for pick mode
_pick_result: ElementPickerResult | None = None
_pick_event = threading.Event()


@router.post("/element-picker/start")
async def start_pick_mode():
    """Start element pick mode.

    Waits for user to click somewhere, captures the UI element at that position.
    Returns the element info after click is detected.
    Timeout: 30 seconds.
    """
    global _pick_result
    _pick_result = None
    _pick_event.clear()

    def _listen_for_click():
        global _pick_result
        from pynput import mouse
        import ctypes
        import ctypes.wintypes

        def on_click(x, y, button, pressed):
            global _pick_result
            if pressed and button == mouse.Button.left:
                # Capture element at click position
                try:
                    from pywinauto import Desktop
                    desktop = Desktop(backend="uia")
                    element = desktop.from_point(x, y)
                    if element:
                        info = element.element_info
                        _pick_result = ElementPickerResult(
                            name=info.name or "",
                            control_type=info.control_type or "",
                            automation_id=info.automation_id or "",
                            class_name=info.class_name or "",
                        )
                    else:
                        _pick_result = ElementPickerResult(name="(요소 없음)")
                except Exception as e:
                    _pick_result = ElementPickerResult(name=f"오류: {e}")
                _pick_event.set()
                return False  # Stop listener

        with mouse.Listener(on_click=on_click) as listener:
            listener.join()

    # Run click listener in background thread
    thread = threading.Thread(target=_listen_for_click, daemon=True)
    thread.start()

    # Wait for click (async-friendly)
    loop = asyncio.get_event_loop()
    await loop.run_in_executor(None, lambda: _pick_event.wait(timeout=30))

    if _pick_result:
        return _pick_result
    return ElementPickerResult(name="(시간 초과 — 30초 안에 클릭하세요)")


@router.post("/element-picker/pick")
async def pick_element_at_cursor():
    """Instantly capture UI element at current cursor position."""
    import ctypes
    import ctypes.wintypes

    result = ElementPickerResult()
    try:
        from pywinauto import Desktop
        pos = ctypes.wintypes.POINT()
        ctypes.windll.user32.GetCursorPos(ctypes.byref(pos))
        desktop = Desktop(backend="uia")
        element = desktop.from_point(pos.x, pos.y)
        if element:
            info = element.element_info
            result = ElementPickerResult(
                name=info.name or "",
                control_type=info.control_type or "",
                automation_id=info.automation_id or "",
                class_name=info.class_name or "",
            )
    except Exception as e:
        result = ElementPickerResult(name=f"오류: {e}")
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
                    "left": rect.left, "top": rect.top,
                    "right": rect.right, "bottom": rect.bottom,
                    "width": rect.width(), "height": rect.height(),
                },
            }
        return {"name": "", "control_type": "", "error": "요소를 찾을 수 없어요"}
    except Exception as e:
        return {"error": str(e)}
