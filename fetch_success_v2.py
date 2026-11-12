"""并发抓取指定账号的「验证通过」记录（v2）。

相比 v1：creatorId 直接内置（省掉扫描），翻页用线程池并发，按 taskId 去重。
判定：status=success 且 verifyResult=1。

输出：
  data/success_records.jsonl   所有记录（去重，按 taskId）
  data/success_by_user.json    每人 {uid, 验证通过数, 卡: {模型集合/数量}, 任务类型}
用法：python fetch_success_v2.py [并发数，默认 8]
"""
import json
import os
import sys
import threading
import time
import urllib.error
import urllib.parse
import urllib.request
from collections import Counter, defaultdict
from concurrent.futures import ThreadPoolExecutor, as_completed

BASE = "https://modelhub.org.cn"
ACCOUNT, PASSWORD = "15542668542", "Pxy18185548!"

# 已通过扫描最近 1.2 万条记录确认的 creatorId
USERS = {
    "i-kanxinlei": 48, "zhoushasha": 14, "i-xiejiahao": 25, "sunruoxi": 17,
    "lucky": 725, "i-dengming": 67, "cpuz": 1916, "lucy": 156,
    "i-liyongjie": 72, "yancuili": 465,
}
WORKERS = int(sys.argv[1]) if len(sys.argv) > 1 else 8

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(HERE, "data")
os.makedirs(DATA, exist_ok=True)
OUT_JSONL = os.path.join(DATA, "success_records.jsonl")
OUT_BY_USER = os.path.join(DATA, "success_by_user.json")

_tl = threading.local()


def session_token():
    if not hasattr(_tl, "tok"):
        body = json.dumps({"userAccount": ACCOUNT, "userPassword": PASSWORD,
                           "loginType": "password"}).encode()
        h = {"Content-Type": "application/json", "User-Agent": "Mozilla/5.0"}
        req = urllib.request.Request(BASE + "/api/user/login", data=body, headers=h, method="POST")
        with urllib.request.urlopen(req, timeout=30) as r:
            _tl.tok = json.loads(r.read().decode())["data"]["token"]
    return _tl.tok


def api(params, retries=3):
    url = BASE + "/api/adapt/task/page?" + urllib.parse.urlencode(params)
    for attempt in range(retries):
        try:
            h = {"User-Agent": "Mozilla/5.0", "Authorization": f"Bearer {session_token()}"}
            with urllib.request.urlopen(urllib.request.Request(url, headers=h), timeout=45) as r:
                return json.loads(r.read().decode())
        except Exception:
            if attempt == retries - 1:
                return {"data": {"records": [], "total": 0}}
            time.sleep(1.0 * (attempt + 1))


def fetch_page(uid, page, size=100):
    d = api({"current": page, "pageSize": size, "onlyMine": "false",
             "status": "success", "creatorId": uid})
    dd = d.get("data") or {}
    return page, int(dd.get("total") or 0), (dd.get("records") or [])


def main():
    t0 = time.time()
    all_rows = {}
    by_user = {}

    for name, uid in USERS.items():
        _, total, recs = fetch_page(uid, 1)
        pages = (total + 99) // 100 if total else 0
        print(f"[{name}] uid={uid} 验证通过总数={total} 页数={pages}", flush=True)
        collected = {}

        def take(page_recs):
            for x in page_recs:
                if int(x.get("verifyResult") or 0) != 1:
                    continue
                tid = x.get("taskId")
                if tid in collected:
                    continue
                collected[tid] = {
                    "user": name, "uid": uid, "taskId": tid,
                    "gpu": x.get("gpuType"), "machine": x.get("machineName"),
                    "model": x.get("modelId"), "level": x.get("modelTaskLevel"),
                    "time": x.get("updateTime"),
                }

        take(recs)
        if pages > 1:
            with ThreadPoolExecutor(max_workers=WORKERS) as ex:
                futs = [ex.submit(fetch_page, uid, p) for p in range(2, pages + 1)]
                done = 1
                for fut in as_completed(futs):
                    _, _, page_recs = fut.result()
                    take(page_recs)
                    done += 1
                    if done % 100 == 0:
                        print(f"    {name}: {done}/{pages} 页, 记录 {len(collected)}", flush=True)

        cards = defaultdict(set)
        levels = Counter()
        for r in collected.values():
            cards[r["gpu"]].add(r["model"])
            levels[r["level"] or "?"] += 1
        by_user[name] = {
            "uid": uid, "api_total": total, "verify_passed": len(collected),
            "cards": {g: {"count": len(ms), "models": sorted(m for m in ms if m)}
                      for g, ms in sorted(cards.items(), key=lambda kv: -len(kv[1]))},
            "levels": dict(levels),
        }
        all_rows.update({(name, k): v for k, v in collected.items()})
        print(f"[{name}] 完成：{len(collected)} 条验证通过，卡 {list(cards)}  ({time.time()-t0:.0f}s)", flush=True)

        with open(OUT_JSONL, "w", encoding="utf-8") as fh:
            for v in all_rows.values():
                fh.write(json.dumps(v, ensure_ascii=False) + "\n")
        with open(OUT_BY_USER, "w", encoding="utf-8") as fh:
            json.dump(by_user, fh, ensure_ascii=False, indent=2)

    total_rec = len(all_rows)
    distinct = len({v["model"] for v in all_rows.values()})
    print(f"\n=== 全部完成：{total_rec} 条验证通过记录，{distinct} 个不同模型，耗时 {time.time()-t0:.0f}s", flush=True)
    for n, d in by_user.items():
        print(f"  {n:14s} uid={d['uid']:5d} 通过={d['verify_passed']:6d} 卡数={len(d['cards'])}", flush=True)


if __name__ == "__main__":
    main()
