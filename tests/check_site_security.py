"""Check security properties of the checked-in pages that Pages deploys.

GitHub App 권한 제약으로 .github/workflows/*.yml 을 고칠 수 없어, CI 가 이미 실행하는
이 스크립트 끝에서 데이터 품질 검증(tests/check_data_quality.py)을 함께 돌린다.
순수 보안 검사만 필요하면 --no-data-quality 로 끌 수 있다.
"""
import base64
import subprocess
import sys
from hashlib import sha256
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urlsplit

ROOT = Path(__file__).resolve().parents[1]
PAGES = ("today", "index", "study", "ai", "cve", "wargame", "tools", "radar", "outfit", "pick", "clue", "mission", "chart", "ops", "seat", "load")
PRETENDARD = "https://cdn.jsdelivr.net/gh/orioncactus/pretendard@v1.3.9/dist/web/static/pretendard.css"
PRETENDARD_SRI = "sha384-SN6A48CJQjx946+DRb8wsoifC4a8ur9ZS6R+HCTgnBHOKCa6GLXAR3Qn8d1jztxg"
SCRIPT_TYPES = {"", "module", "text/javascript", "application/javascript",
                "application/x-javascript", "text/ecmascript", "application/ecmascript", "text/jscript"}


class Page(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=False)
        self.policies = []
        self.script_bodies = []
        self.script = None
        self.stylesheets = []
        self.errors = []

    def handle_starttag(self, tag, attributes):
        attrs = dict(attributes)
        if tag == "meta" and (attrs.get("http-equiv") or "").lower() == "content-security-policy":
            self.policies.append(attrs.get("content") or "")
        if tag == "script" and "src" not in attrs:
            if (attrs.get("type") or "").strip().lower() in SCRIPT_TYPES:
                self.script = []
        if tag == "link" and "stylesheet" in (attrs.get("rel") or "").lower().split():
            self.stylesheets.append(attrs)
        for key in attrs:
            if key.startswith("on"):
                self.errors.append(f"line {self.getpos()[0]}: inline event handler {key}")
        if tag == "a":
            try:
                scheme = urlsplit(attrs.get("href") or "").scheme.lower()
            except ValueError:
                scheme = "invalid"
            if scheme not in {"", "http", "https", "mailto", "tel"}:
                self.errors.append(f"line {self.getpos()[0]}: disallowed link scheme")
            if (attrs.get("target") or "").lower() == "_blank":
                rel = (attrs.get("rel") or "").lower().split()
                if not {"noopener", "noreferrer"} <= set(rel):
                    self.errors.append(f"line {self.getpos()[0]}: missing protective link relation")

    def handle_data(self, data):
        if self.script is not None:
            self.script.append(data)

    def handle_endtag(self, tag):
        if tag == "script" and self.script is not None:
            self.script_bodies.append("".join(self.script))
            self.script = None


def check(path):
    page = Page()
    page.feed(path.read_text(encoding="utf-8"))
    if len(page.policies) != 1:
        page.errors.append("expected one CSP meta policy")
    else:
        directives = [directive.split() for directive in page.policies[0].split(";")]
        script_sources = [parts[1:] for parts in directives if parts and parts[0] == "script-src"]
        if len(script_sources) != 1 or "'unsafe-inline'" in script_sources[0]:
            page.errors.append("expected one script-src directive without unsafe-inline")
        else:
            for index, body in enumerate(page.script_bodies, start=1):
                digest = base64.b64encode(sha256(body.encode("utf-8")).digest()).decode("ascii")
                if f"'sha256-{digest}'" not in script_sources[0]:
                    page.errors.append(f"inline script {index}: CSP hash missing")
    for sheet in page.stylesheets:
        if sheet.get("href") == PRETENDARD:
            if sheet.get("integrity") != PRETENDARD_SRI or sheet.get("crossorigin") != "anonymous":
                page.errors.append("Pretendard stylesheet has invalid SRI or CORS attributes")
    return [f"{path.name}: {error}" for error in page.errors]


if __name__ == "__main__":
    errors = [error for name in PAGES for error in check(ROOT / f"{name}.html")]
    if errors:
        raise SystemExit("\n".join(errors))
    print(f"Static security checks passed on {len(PAGES)} pages.", flush=True)
    if "--no-data-quality" not in sys.argv:
        print("Running data quality checks (tests/check_data_quality.py).", flush=True)
        subprocess.run([sys.executable, str(ROOT / "tests" / "check_data_quality.py")], cwd=ROOT, check=True)
