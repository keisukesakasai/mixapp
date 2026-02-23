"""
Load generator: Investor Agent へ投資関連の質問を送り続ける（セッション単位でスタックされる）
"""
import os
import random
import time
import uuid

import httpx

# Investor Agent 向けの質問リスト（銘柄・セクター・戦略・マクロ・リスク・制度など多様に）
QUESTIONS = [
    # 銘柄・ETF
    "今買うべき株を3つ教えて。",
    "長期保有におすすめの米国株は？",
    "配当重視でおすすめの銘柄を教えて。",
    "成長株でおすすめはある？",
    "日本株でバリュー株のおすすめは？",
    "高配当の米国ETFでおすすめは？",
    "テクノロジー株で長期保有したい銘柄は？",
    "S&P500に連動するETFを1つ教えて。",
    "全世界株に投資できるETFでおすすめは？",
    "金価格に連動するETFの銘柄コードを教えて。",
    "配当 aristocrat として有名な米国株を3つ挙げて。",
    "日本株で小型成長株のおすすめは？",
    "REITで分散投資したい場合のおすすめは？",
    # セクター・相場観
    "今の相場で割安だと思うセクターは？",
    "景気後半でアウトパフォームしやすいセクターは？",
    "金利上昇局面で有利なセクターと不利なセクターを教えて。",
    "AI関連株で長期で有望なセクターは？",
    "ヘルスケア株を長期保有するメリットを教えて。",
    "エネルギー株をポートフォリオに入れる意義は？",
    "ディフェンシブ株の具体例と特徴を簡潔に。",
    "景気敏感株とディフェンシブ株の違いを簡潔に教えて。",
    # 資産配分・ポートフォリオ
    "今の金利環境でおすすめの資産配分は？",
    "インデックス投資と個別株、どちらを勧める？",
    "60:40の株式・債券配分は今でも有効？",
    "若い人が株式の割合を高くする理由を教えて。",
    "リバランスはどのくらいの頻度でやるのがよい？",
    "円建て資産と外貨建て資産の理想的な割合の目安は？",
    "債券の役割をポートフォリオの観点で説明して。",
    "コア・サテライト戦略の考え方を簡潔に教えて。",
    # 為替・金利・マクロ
    "為替が円安のときにおすすめの投資は？",
    "円高になったときに株価がどう動きやすいか教えて。",
    "金利が上がると株価はなぜ押し下げられやすい？",
    "インフレヘッジとして株式と債券どちらが向いている？",
    "スタグフレーション時のおすすめ資産は？",
    "FRBの利下げが始まったらどんな資産が有利になりそう？",
    "ドルコスト平均法のメリットとデメリットを教えて。",
    # 戦略・考え方
    "配当再投資のメリットを一言で。",
    "バリュー投資とグロース投資の違いを教えて。",
    "PERが高い銘柄を買うリスクは？",
    "損切りは何%くらいで設定するのが一般的？",
    "塩漬け株を解消するための考え方を教えて。",
    "つみたて投資で失敗しないコツは？",
    "高配当株に集中するリスクを教えて。",
    "テクニカル分析とファンダメンタル分析、初心者にはどちらから？",
    "モメンタム投資の基本的な考え方を教えて。",
    # 制度・税務（日本）
    "NISAとiDeCo、どちらを優先すべき？",
    "つみたて投資枠と成長投資枠の使い分けのコツは？",
    "iDeCoで運用するなら株式と債券の割合の目安は？",
    "特定口座の源泉徴収ありと申告、どちらがおすすめ？",
    "配当金の課税について簡潔に教えて。",
    "退職金を投資に回す場合の注意点は？",
    # リスク・心理
    "暴落時にすべきこと・避けることを教えて。",
    "損失を拡大させないためのルールの例を教えて。",
    "投資でよくある心理的バイアスを1つ挙げて対策を。",
    "ボラティリティの高い銘柄に投資するときの心構えは？",
    "分散投資で「分散」できるリスクとできないリスクの違いは？",
    # 比較・選択
    "投資信託とETF、コストの面で比較すると？",
    "アクティブファンドとインデックスファンド、長期ではどちらが有利と言われている？",
    "国内株と海外株、リターンとリスクの違いを教えて。",
    "米国株を買うとき、為替ヘッジあり・なしの選び方は？",
    "高配当ETFと成長株ETF、リタイア後はどちらを多めに？",
]


def get_llm_url() -> str:
    url = os.environ.get("LLM_APP_URL", "http://investor-agent:8000")
    return url.rstrip("/")


def run_loop(interval_sec: float = 2.0):
    url_base = get_llm_url()
    ask_url = f"{url_base}/ask"
    session_id = os.environ.get("SESSION_ID") or f"loadgen-{uuid.uuid4().hex[:12]}"
    print(f"Target: {ask_url} (Investor Agent, interval={interval_sec}s, session={session_id})", flush=True)
    with httpx.Client(timeout=60.0) as client:
        n = 0
        while True:
            n += 1
            q = random.choice(QUESTIONS)
            start = time.perf_counter()
            try:
                r = client.post(ask_url, json={"question": q, "session_id": session_id})
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
