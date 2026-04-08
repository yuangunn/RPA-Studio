"""Web automation actions using Playwright.

Manages a browser instance in ExecutionContext so multiple web steps
can operate on the same browser/page within a single execution.
"""
from __future__ import annotations
from rpa_studio.actions.base import ActionHandler
from rpa_studio.models import ActionType, Step
from rpa_studio.engine.context import ExecutionContext


def _get_browser(context: ExecutionContext):
    """Get or create a Playwright browser + page from ExecutionContext."""
    if "_pw_page" in context.variables and context.variables["_pw_page"]:
        return context.variables["_pw_page"]

    from playwright.sync_api import sync_playwright

    pw = sync_playwright().start()
    context.variables["_pw_instance"] = pw

    browser = pw.chromium.launch(headless=False)
    context.variables["_pw_browser"] = browser

    page = browser.new_page()
    context.variables["_pw_page"] = page

    return page


def _close_browser(context: ExecutionContext):
    """Close Playwright browser and cleanup."""
    browser = context.variables.pop("_pw_browser", None)
    pw = context.variables.pop("_pw_instance", None)
    context.variables.pop("_pw_page", None)

    if browser:
        try:
            browser.close()
        except Exception:
            pass
    if pw:
        try:
            pw.stop()
        except Exception:
            pass


class WebOpenHandler(ActionHandler):
    action_type = ActionType.WEB_OPEN

    def execute(self, step: Step, context: ExecutionContext):
        url = context.resolve(step.params.get("url", "about:blank"))
        headless = step.params.get("headless", False)
        context.add_log(f"웹 브라우저 시작: {url}")

        from playwright.sync_api import sync_playwright

        # Close existing if any
        _close_browser(context)

        pw = sync_playwright().start()
        context.variables["_pw_instance"] = pw

        browser = pw.chromium.launch(headless=headless)
        context.variables["_pw_browser"] = browser

        page = browser.new_page()
        context.variables["_pw_page"] = page

        if url and url != "about:blank":
            page.goto(url, wait_until="domcontentloaded")

        return {"url": url}


class WebNavigateHandler(ActionHandler):
    action_type = ActionType.WEB_NAVIGATE

    def execute(self, step: Step, context: ExecutionContext):
        url = context.resolve(step.params.get("url", ""))
        if not url:
            raise RuntimeError("이동할 웹 주소가 비어있어요.")
        context.add_log(f"웹 페이지 이동: {url}")

        page = _get_browser(context)
        page.goto(url, wait_until="domcontentloaded")
        return {"url": url, "title": page.title()}


class WebClickHandler(ActionHandler):
    action_type = ActionType.WEB_CLICK

    def execute(self, step: Step, context: ExecutionContext):
        selector = context.resolve(step.params.get("selector", ""))
        text = context.resolve(step.params.get("text", ""))
        context.add_log(f"웹 요소 클릭: {selector or text}")

        page = _get_browser(context)

        if selector:
            page.click(selector, timeout=10000)
        elif text:
            page.get_by_text(text).click(timeout=10000)
        else:
            raise RuntimeError("클릭할 요소의 선택자 또는 텍스트를 입력해주세요.")

        return {"clicked": selector or text}


class WebTypeHandler(ActionHandler):
    action_type = ActionType.WEB_TYPE

    def execute(self, step: Step, context: ExecutionContext):
        selector = context.resolve(step.params.get("selector", ""))
        text = context.resolve(step.params.get("text", ""))
        placeholder = context.resolve(step.params.get("placeholder", ""))
        clear = step.params.get("clear", True)
        context.add_log(f"웹 텍스트 입력: {text[:20]}...")

        page = _get_browser(context)

        if selector:
            if clear:
                page.fill(selector, text, timeout=10000)
            else:
                page.type(selector, text, timeout=10000)
        elif placeholder:
            page.get_by_placeholder(placeholder).fill(text, timeout=10000)
        else:
            raise RuntimeError("입력할 요소의 선택자 또는 placeholder를 입력해주세요.")

        return {"typed": text}


class WebExtractHandler(ActionHandler):
    action_type = ActionType.WEB_EXTRACT

    def execute(self, step: Step, context: ExecutionContext):
        selector = context.resolve(step.params.get("selector", ""))
        attribute = step.params.get("attribute", "textContent")
        save_as = step.params.get("save_as", "웹텍스트")
        context.add_log(f"웹 텍스트 추출: {selector}")

        page = _get_browser(context)

        if not selector:
            raise RuntimeError("추출할 요소의 선택자를 입력해주세요.")

        element = page.query_selector(selector)
        if not element:
            raise RuntimeError(f"요소를 찾을 수 없어요: {selector}")

        if attribute == "textContent":
            value = element.text_content() or ""
        elif attribute == "innerText":
            value = element.inner_text()
        elif attribute == "value":
            value = element.input_value()
        else:
            value = element.get_attribute(attribute) or ""

        context.variables[save_as] = value.strip()
        context.add_log(f"추출 결과: {value[:50]}...")
        return {"value": value, "save_as": save_as}


class WebWaitHandler(ActionHandler):
    action_type = ActionType.WEB_WAIT

    def execute(self, step: Step, context: ExecutionContext):
        selector = context.resolve(step.params.get("selector", ""))
        state = step.params.get("state", "visible")
        timeout = int(step.params.get("timeout", 10)) * 1000
        context.add_log(f"웹 요소 대기: {selector} ({state})")

        page = _get_browser(context)

        if not selector:
            raise RuntimeError("대기할 요소의 선택자를 입력해주세요.")

        page.wait_for_selector(selector, state=state, timeout=timeout)
        return {"selector": selector, "state": state}


class WebCloseHandler(ActionHandler):
    action_type = ActionType.WEB_CLOSE

    def execute(self, step: Step, context: ExecutionContext):
        context.add_log("웹 브라우저 닫기")
        _close_browser(context)
        return {"closed": True}
