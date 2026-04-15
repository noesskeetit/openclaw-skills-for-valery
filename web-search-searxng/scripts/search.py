#!/usr/bin/env python3
"""Search the internet via SearXNG.

On first invocation, if the SearXNG service is unreachable, this script will
automatically `docker compose up -d` the service from the skill's root
directory, wait for it to become healthy, and retry the query.

Use --no-auto-start to skip auto-bootstrap (useful in CI or when docker is
intentionally unavailable).
"""
import argparse
import json
import os
import shutil
import subprocess
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path
from urllib.parse import urlparse


SKILL_ROOT = Path(__file__).resolve().parent.parent


def _die(message, **extra):
    payload = {"error": message}
    payload.update(extra)
    print(json.dumps(payload, ensure_ascii=False), file=sys.stderr)
    sys.exit(1)


def _bypass_proxy_for_local(base_url):
    host = urlparse(base_url).hostname
    if host in ("localhost", "127.0.0.1", "searxng"):
        os.environ["no_proxy"] = os.environ.get("no_proxy", "") + f",{host}"


def _is_service_up(base_url, timeout=2):
    """Quick health probe — returns True if /healthz responds 200."""
    healthz = f"{base_url.rstrip('/')}/healthz"
    try:
        with urllib.request.urlopen(healthz, timeout=timeout) as resp:
            return resp.status == 200
    except Exception:
        return False


def _docker_available():
    if shutil.which("docker") is None:
        return False
    try:
        r = subprocess.run(
            ["docker", "info"],
            capture_output=True, timeout=5,
        )
        return r.returncode == 0
    except Exception:
        return False


def _bootstrap_service(base_url, wait_timeout=60):
    """Run `docker compose up -d` from SKILL_ROOT and wait for /healthz."""
    if not _docker_available():
        _die(
            "SearXNG is not running and docker is unavailable. "
            "Install/start Docker, or use the 'web-search-tavily' skill instead.",
            hint="docker daemon not reachable",
            skill_root=str(SKILL_ROOT),
        )

    compose_file = SKILL_ROOT / "docker-compose.yml"
    if not compose_file.exists():
        _die(
            f"docker-compose.yml not found at {compose_file}",
            skill_root=str(SKILL_ROOT),
        )

    try:
        result = subprocess.run(
            ["docker", "compose", "up", "-d"],
            cwd=str(SKILL_ROOT),
            capture_output=True,
            text=True,
            timeout=120,
        )
    except subprocess.TimeoutExpired:
        _die("`docker compose up -d` timed out after 120s")
    except Exception as e:
        _die(f"Failed to invoke docker compose: {e}")

    if result.returncode != 0:
        _die(
            "docker compose up -d failed",
            stderr=result.stderr.strip()[-500:],
            stdout=result.stdout.strip()[-500:],
        )

    # Poll /healthz every 2s up to wait_timeout.
    deadline = time.time() + wait_timeout
    while time.time() < deadline:
        if _is_service_up(base_url, timeout=2):
            return
        time.sleep(2)

    _die(
        f"SearXNG did not become healthy within {wait_timeout}s after docker compose up -d",
        hint="Try `docker compose logs` in the skill directory to diagnose.",
        skill_root=str(SKILL_ROOT),
    )


def _do_request(base_url, query, categories, language):
    params = {
        "q": query,
        "format": "json",
        "categories": categories,
    }
    if language != "auto":
        params["language"] = language

    url = f"{base_url}/search?{urllib.parse.urlencode(params)}"
    req = urllib.request.Request(url, headers={
        "User-Agent": "Mozilla/5.0 (compatible; OpenClaw/1.0)",
        "Accept": "application/json",
    })
    with urllib.request.urlopen(req, timeout=20) as resp:
        return json.loads(resp.read().decode())


def search(query, max_results=5, categories="general", language="auto", auto_start=True):
    base_url = os.environ.get("SEARXNG_URL", "http://localhost:8080").rstrip("/")
    _bypass_proxy_for_local(base_url)

    try:
        data = _do_request(base_url, query, categories, language)
    except urllib.error.URLError as e:
        # Connection refused / DNS / timeout — try to auto-bootstrap.
        reason = getattr(e, "reason", e)
        if not auto_start:
            _die(
                f"Cannot reach SearXNG at {base_url}: {reason}",
                hint="Auto-start disabled via --no-auto-start. Run `docker compose up -d` in the skill directory.",
            )
        # Only bootstrap for localhost-ish endpoints; remote URLs are the
        # operator's problem.
        host = urlparse(base_url).hostname
        if host not in ("localhost", "127.0.0.1"):
            _die(f"Cannot reach SearXNG at {base_url}: {reason}")

        _bootstrap_service(base_url)
        # Retry once after bootstrap.
        try:
            data = _do_request(base_url, query, categories, language)
        except urllib.error.URLError as e2:
            _die(f"SearXNG unreachable even after bootstrap: {getattr(e2, 'reason', e2)}")

    results = []
    for item in data.get("results", [])[:max_results]:
        results.append({
            "title": item.get("title", ""),
            "url": item.get("url", ""),
            "snippet": item.get("content", ""),
            "source": item.get("engine", ""),
        })

    return results


def main():
    parser = argparse.ArgumentParser(description="Search the internet via SearXNG")
    parser.add_argument("query", help="Search query")
    parser.add_argument("--max-results", type=int, default=5, help="Max results (default: 5)")
    parser.add_argument("--categories", default="general",
                        choices=["general", "news", "science", "images", "videos", "it"],
                        help="Search category (default: general)")
    parser.add_argument("--language", default="auto", help="Language code, e.g. ru, en (default: auto)")
    parser.add_argument("--no-auto-start", action="store_true",
                        help="Do not auto-start SearXNG via docker compose if unreachable.")
    args = parser.parse_args()

    results = search(
        args.query,
        args.max_results,
        args.categories,
        args.language,
        auto_start=not args.no_auto_start,
    )
    print(json.dumps(results, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
