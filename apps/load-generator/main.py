"""
Load generator: LLM アプリへ適当な質問を送り続ける
"""
import os
import random
import time

import httpx

# 負荷用の質問リスト（ループで使い回す）
QUESTIONS = [
    "1+1は？",
    "今日の天気について一言で。",
    "りんごを英語で言うと？",
    "日本の首都は？",
    "Hello を日本語に訳して。",
    "円周率の小数点以下2桁は？",
    "富士山の高さはおおよそ何m？",
    "俳句を一句作って。",
    "プログラミングで変数とは？",
    "おすすめの挨拶を一つ教えて。",
]


def get_llm_url() -> str:
    url = os.environ.get("LLM_APP_URL", "http://llm-app:8000")
    return url.rstrip("/")


def run_loop(interval_sec: float = 2.0):
    url_base = get_llm_url()
    ask_url = f"{url_base}/ask"
    print(f"Target: {ask_url} (interval={interval_sec}s)", flush=True)
    with httpx.Client(timeout=30.0) as client:
        n = 0
        while True:
            n += 1
            q = random.choice(QUESTIONS)
            start = time.perf_counter()
            try:
                r = client.post(ask_url, json={"question": q})
                elapsed = time.perf_counter() - start
                if r.is_success:
                    body = r.json()
                    answer = (body.get("answer") or "")[:80]
                    print(f"[{n}] OK {elapsed:.2f}s | Q: {q[:40]} | A: {answer}...", flush=True)
                else:
                    print(f"[{n}] HTTP {r.status_code} {elapsed:.2f}s | Q: {q[:40]}", flush=True)
            except Exception as e:
                elapsed = time.perf_counter() - start
                print(f"[{n}] ERROR {elapsed:.2f}s | {e}", flush=True)
            time.sleep(interval_sec)


if __name__ == "__main__":
    interval = float(os.environ.get("INTERVAL_SEC", "2.0"))
    run_loop(interval_sec=interval)
