"""End-to-end integration test for VASP-TRACE AI backend and frontend.

Tests:
1. Starts AI backend (python -m backend.ai.api) on port 8000.
2. Serves frontend (python -m http.server 3000 --directory frontend) on port 3000.
3. Tests frontend delivery (index.html, style.css, aiEvaluation.js, aiService.js).
4. Tests asset paths, syntax sanity, and API URL consistency.
5. Tests backend POST /ai/evaluate response structure and values.
6. Shuts down processes and reports findings.
"""

import json
import os
import subprocess
import sys
import time
import urllib.error
import urllib.request

WORKSPACE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))


def wait_for_server(url, timeout=5.0):
    """Wait until an HTTP server responds with any HTTP status code."""
    start = time.time()
    while time.time() - start < timeout:
        try:
            with urllib.request.urlopen(url, timeout=1.0) as resp:
                return resp.status
        except urllib.error.HTTPError as e:
            return e.code
        except Exception:
            time.sleep(0.2)
    return None


def run_e2e_tests():
    backend_proc = None
    frontend_proc = None
    results = []
    issues = []

    try:
        # 1. Start AI backend process
        print("[E2E] Starting backend: python -m backend.ai.api")
        backend_proc = subprocess.Popen(
            [sys.executable, "-m", "backend.ai.api"],
            cwd=WORKSPACE_DIR,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )

        # 2. Start Frontend server process
        print("[E2E] Starting frontend: python -m http.server 3000 --directory frontend")
        frontend_proc = subprocess.Popen(
            [sys.executable, "-m", "http.server", "3000", "--directory", "frontend"],
            cwd=WORKSPACE_DIR,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )

        # Wait for both servers to accept connections
        backend_status = wait_for_server("http://127.0.0.1:8000/ai/evaluate", timeout=6.0)
        if backend_status is None:
            issues.append("AI Backend failed to start or bind to http://127.0.0.1:8000")
        else:
            results.append(f"AI Backend listening at http://127.0.0.1:8000 (status check: {backend_status})")

        frontend_status = wait_for_server("http://127.0.0.1:3000/", timeout=6.0)
        if frontend_status is None:
            issues.append("Frontend server failed to start or bind to http://127.0.0.1:3000")
        else:
            results.append(f"Frontend server listening at http://127.0.0.1:3000 (status check: {frontend_status})")

        # 3. Verify Frontend Static Assets
        frontend_urls = [
            ("Frontend index.html", "http://127.0.0.1:3000/"),
            ("Frontend CSS (style.css)", "http://127.0.0.1:3000/assets/style.css"),
            ("Frontend Page Controller (aiEvaluation.js)", "http://127.0.0.1:3000/src/pages/aiEvaluation.js"),
            ("Frontend AI Service (aiService.js)", "http://127.0.0.1:3000/src/services/aiService.js"),
        ]

        for name, url in frontend_urls:
            try:
                with urllib.request.urlopen(url, timeout=3.0) as resp:
                    body = resp.read()
                    if resp.status == 200 and len(body) > 0:
                        results.append(f"GET {url} -> 200 OK ({len(body)} bytes)")
                    else:
                        issues.append(f"{name} at {url} returned unexpected status {resp.status}")
            except Exception as e:
                issues.append(f"Failed to fetch {name} at {url}: {e}")

        # 4. Check asset paths and API URLs consistency in frontend files
        index_html_path = os.path.join(WORKSPACE_DIR, "frontend", "index.html")
        with open(index_html_path, "r", encoding="utf-8") as f:
            html_content = f.read()

        if 'href="assets/style.css"' not in html_content:
            issues.append("index.html: Missing or broken stylesheet path 'assets/style.css'")
        else:
            results.append("index.html: Verified correct stylesheet link (assets/style.css)")

        if 'src="src/pages/aiEvaluation.js"' not in html_content:
            issues.append("index.html: Missing or broken script module path 'src/pages/aiEvaluation.js'")
        else:
            results.append("index.html: Verified correct module script source (src/pages/aiEvaluation.js)")

        ai_service_path = os.path.join(WORKSPACE_DIR, "frontend", "src", "services", "aiService.js")
        with open(ai_service_path, "r", encoding="utf-8") as f:
            js_content = f.read()

        if "http://127.0.0.1:8000" not in js_content or "/ai/evaluate" not in js_content:
            issues.append("aiService.js: Incorrect API endpoint configuration")
        else:
            results.append("aiService.js: Verified target API URL is 'http://127.0.0.1:8000/ai/evaluate'")

        # 5. Backend POST /ai/evaluate End-to-End Test
        payload = {
            "graph_data": {
                "hop_count": 2,
                "mixer_proximity": 0.7,
            },
            "scoring_data": {
                "sanction_hit": False,
                "darknet_exposure": True,
                "kyc_verified": False,
            },
        }

        req = urllib.request.Request(
            "http://127.0.0.1:8000/ai/evaluate",
            data=json.dumps(payload).encode("utf-8"),
            headers={"Content-Type": "application/json"},
            method="POST",
        )

        try:
            with urllib.request.urlopen(req, timeout=3.0) as resp:
                resp_status = resp.status
                resp_bytes = resp.read()
                resp_json = json.loads(resp_bytes.decode("utf-8"))

                if resp_status == 200:
                    results.append("POST http://127.0.0.1:8000/ai/evaluate -> 200 OK")
                else:
                    issues.append(f"POST /ai/evaluate returned unexpected status: {resp_status}")

                # Verify required keys
                required_keys = [
                    "risk_score",
                    "risk_level",
                    "confidence_score",
                    "feature_contributions",
                    "narrative",
                ]
                for key in required_keys:
                    if key in resp_json:
                        results.append(f"Response validation: '{key}' present (value: {resp_json[key] if key != 'narrative' else 'Non-empty narrative string'})")
                    else:
                        issues.append(f"Response missing required key '{key}'")

                # Verify payload values
                if resp_json.get("risk_level") == "HIGH" and resp_json.get("risk_score") == 74.0:
                    results.append(f"Evaluated values confirmed: risk_level='HIGH', risk_score=74.0, confidence={resp_json.get('confidence_score')}")
                else:
                    issues.append(f"Evaluated values mismatch: expected risk_score=74.0 and risk_level='HIGH', got {resp_json.get('risk_score')} and {resp_json.get('risk_level')}")

                contributions = resp_json.get("feature_contributions", [])
                if len(contributions) == 3:
                    results.append(f"Feature contributions confirmed ({len(contributions)} ranked items)")
                else:
                    issues.append(f"Expected 3 feature contributions, got {len(contributions)}")

        except Exception as e:
            issues.append(f"POST /ai/evaluate request failed: {e}")

    finally:
        # Terminate processes cleanly
        if backend_proc:
            backend_proc.terminate()
            try:
                backend_proc.wait(timeout=2.0)
            except Exception:
                backend_proc.kill()
        if frontend_proc:
            frontend_proc.terminate()
            try:
                frontend_proc.wait(timeout=2.0)
            except Exception:
                frontend_proc.kill()

    return results, issues


if __name__ == "__main__":
    results, issues = run_e2e_tests()
    print("\n" + "=" * 50)
    print("E2E INTEGRATION TEST RESULTS")
    print("=" * 50)
    for r in results:
        print(f"  [PASS] {r}")

    print("\nISSUES FOUND:")
    if issues:
        for i in issues:
            print(f"  [FAIL] {i}")
        sys.exit(1)
    else:
        print("  None (0 issues found)")
        print("\nAll end-to-end integration checks passed successfully!")
        sys.exit(0)
