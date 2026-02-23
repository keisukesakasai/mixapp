"""
Load generator: Investor Agent へ投資関連の質問を送り続ける
"""
import os
import random
import time

import httpx

# Investor Agent 向けの質問リスト
QUESTIONS = [
    "今買うべき株を3つ教えて。",
    "長期保有におすすめの米国株は？",
    "配当重視でおすすめの銘柄を教えて。",
    "成長株でおすすめはある？",
    "日本株でバリュー株のおすすめは？",
    "今の相場で割安だと思うセクターは？",
    "高配当の米国ETFでおすすめは？",
    "テクノロジー株で長期保有したい銘柄は？",
    "景気敏感株とディフェンシブ株の違いを簡潔に教えて。",
    "インデックス投資と個別株、どちらを勧める？",
    "為替が円安のときにおすすめの投資は？",
    "配当再投資のメリットを一言で。",
    "今の金利環境でおすすめの資産配分は？",
    "S&P500に連動するETFを1つ教えて。",
]


def get_llm_url() -> str:
    url = os.environ.get("LLM_APP_URL", "http://investor-agent:8000")
    return url.rstrip("/")


def run_loop(interval_sec: float = 2.0):
    url_base = get_llm_url()
    ask_url = f"{url_base}/ask"
    print(f"Target: {ask_url} (Investor Agent, interval={interval_sec}s)", flush=True)
    with httpx.Client(timeout=60.0) as client:
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
                    answer = (body.get("answer") or "").replace("\n", " ")[:80]
                    print(f"[{n}] OK {elapsed:.2f}s | Q: {q[:35]} | A: {answer}...", flush=True)
                else:
                    print(f"[{n}] HTTP {r.status_code} {elapsed:.2f}s | Q: {q[:35]}", flush=True)
            except Exception as e:
                elapsed = time.perf_counter() - start
                print(f"[{n}] ERROR {elapsed:.2f}s | {e}", flush=True)
            time.sleep(interval_sec)


if __name__ == "__main__":
    interval = float(os.environ.get("INTERVAL_SEC", "2.0"))
    run_loop(interval_sec=interval)
