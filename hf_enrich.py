"""对平台上「验证通过」的模型，去 HuggingFace 抓元数据，用于总结选模型规律。

输入：data/success_records.jsonl（由 fetch_platform_success.py 生成）
输出：data/models_hf.jsonl（一行一个模型，可断点续跑，已抓过的跳过）
汇总：data/hf_summary.json

抓取字段：downloads / likes / createdAt / lastModified / tags / license /
          pipeline_tag / library / gguf 文件数 / 合规量化 / gated / 是否私有
用法：python hf_enrich.py [并发数，默认 6]
"""
import json
import os
import re
import sys
import threading
import time
import urllib.error
import urllib.request
from collections import Counter
from concurrent.futures import ThreadPoolExecutor, as_completed

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(HERE, "data")
IN_FILE = os.path.join(DATA, "success_records.jsonl")
OUT_FILE = os.path.join(DATA, "models_hf.jsonl")
SUM_FILE = os.path.join(DATA, "hf_summary.json")

CONFIG_PY = os.path.join(os.path.dirname(HERE), "hubXcAgent3", "config.py")
WORKERS = int(sys.argv[1]) if len(sys.argv) > 1 else 6

# 平台对 GGUF 的量化白名单（B3/B4/bi150 那套经验值，仅用于统计）
QUANT_PREF = ["Q8_0", "f16", "fp16", "bf16", "Q4_0", "Q6_K", "Q5_K_M", "Q4_K_M"]


def load_hf_token():
    try:
        with open(CONFIG_PY, encoding="utf-8") as f:
            for line in f:
                m = re.match(r'\s*HFTOKEN\s*=\s*["\']([^"\']+)["\']', line)
                if m:
                    return m.group(1)
    except Exception:
        pass
    return None


HF_TOKEN = load_hf_token()
_lock = threading.Lock()


def fetch(repo, retries=3):
    url = f"https://huggingface.co/api/models/{repo}"
    h = {"User-Agent": "Mozilla/5.0"}
    if HF_TOKEN:
        h["Authorization"] = f"Bearer {HF_TOKEN}"
    for attempt in range(retries):
        try:
            with urllib.request.urlopen(urllib.request.Request(url, headers=h), timeout=20) as r:
                d = json.loads(r.read().decode())
            siblings = [s.get("rfilename", "") for s in d.get("siblings", [])]
            gguf = [s for s in siblings if s.lower().endswith(".gguf")]
            quants = set()
            for g in gguf:
                low = g.lower()
                for q in QUANT_PREF:
                    if q.lower() in low:
                        quants.add(q)
                        break
            return {
                "model": repo,
                "ok": True,
                "downloads": d.get("downloads"),
                "likes": d.get("likes"),
                "createdAt": d.get("createdAt"),
                "lastModified": d.get("lastModified"),
                "pipeline_tag": d.get("pipeline_tag"),
                "library": d.get("library_name"),
                "tags": d.get("tags"),
                "license": (d.get("cardData") or {}).get("license"),
                "gated": d.get("gated"),
                "private": d.get("private"),
                "n_files": len(siblings),
                "n_gguf": len(gguf),
                "quants": sorted(quants),
            }
        except urllib.error.HTTPError as e:
            if e.code in (404, 401, 403):
                return {"model": repo, "ok": False, "http": e.code}
            if attempt == retries - 1:
                return {"model": repo, "ok": False, "http": e.code}
        except Exception as e:
            if attempt == retries - 1:
                return {"model": repo, "ok": False, "error": f"{type(e).__name__}: {e}"[:120]}
        time.sleep(1.5 * (attempt + 1))
    return {"model": repo, "ok": False, "error": "retries exhausted"}


def main():
    if not os.path.exists(IN_FILE):
        sys.exit(f"缺少输入文件: {IN_FILE}（先跑 fetch_platform_success.py）")

    models = []
    seen = set()
    for line in open(IN_FILE, encoding="utf-8"):
        try:
            m = json.loads(line)["model"]
        except Exception:
            continue
        if m and m not in seen:
            seen.add(m)
            models.append(m)
    print(f"去重后模型 {len(models)} 个 | HFTOKEN={'有' if HF_TOKEN else '无'} | 并发 {WORKERS}", flush=True)

    done = set()
    if os.path.exists(OUT_FILE):
        for line in open(OUT_FILE, encoding="utf-8"):
            try:
                done.add(json.loads(line)["model"])
            except Exception:
                pass
        print(f"续跑：已完成 {len(done)} 个，本次待抓 {len(models) - len(done)}", flush=True)

    todo = [m for m in models if m not in done]
    t0 = time.time()
    n = 0
    with open(OUT_FILE, "a", encoding="utf-8") as fh, ThreadPoolExecutor(max_workers=WORKERS) as ex:
        futs = {ex.submit(fetch, m): m for m in todo}
        for fut in as_completed(futs):
            r = fut.result()
            with _lock:
                fh.write(json.dumps(r, ensure_ascii=False) + "\n")
                fh.flush()
                n += 1
                if n % 200 == 0:
                    rate = n / (time.time() - t0)
                    print(f"  {n}/{len(todo)}  {rate:.1f} 个/秒", flush=True)

    # --- 汇总 ---
    rows = []
    for line in open(OUT_FILE, encoding="utf-8"):
        try:
            rows.append(json.loads(line))
        except Exception:
            pass
    ok = [r for r in rows if r.get("ok")]
    miss = Counter(r.get("http") or "error" for r in rows if not r.get("ok"))
    lic = Counter(r.get("license") or "未知" for r in ok)
    pipe = Counter(r.get("pipeline_tag") or "未知" for r in ok)
    has_gguf = sum(1 for r in ok if r.get("n_gguf"))
    dl = sorted([r.get("downloads") or 0 for r in ok])
    summary = {
        "models_total": len(rows),
        "hf_ok": len(ok),
        "hf_missing": dict(miss),
        "gguf_repo_ratio": round(has_gguf / len(ok), 3) if ok else 0,
        "license_top": dict(lic.most_common(10)),
        "pipeline_top": dict(pipe.most_common(10)),
        "downloads_median": dl[len(dl) // 2] if dl else 0,
        "downloads_p90": dl[int(len(dl) * 0.9)] if dl else 0,
    }
    json.dump(summary, open(SUM_FILE, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    print(json.dumps(summary, ensure_ascii=False, indent=2), flush=True)


if __name__ == "__main__":
    main()
