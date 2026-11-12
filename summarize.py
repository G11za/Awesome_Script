"""把抓到的「验证通过」记录汇总成报表。

输入：data/success_records.jsonl（fetch_success_v2.py 产出）
输出：
  out/REPORT.md            规律总结（人×卡矩阵、模型作者、规模、格式）
  out/user_gpu_matrix.csv  账号 × 卡 的验证通过数量
  out/models_by_gpu.csv    卡,模型,提交人数,提交人
  out/models_unique.csv    去重后的模型清单（含在哪些卡上过）
  out/anonymized_records.csv  去掉账号名的版本（可公开）
用法：python summarize.py
"""
import csv
import json
import os
import re
from collections import Counter, defaultdict

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(HERE, "data")
OUT = os.path.join(HERE, "out")
os.makedirs(OUT, exist_ok=True)
IN_FILE = os.path.join(DATA, "success_records.jsonl")

QUANT_RE = re.compile(r"(IQ\d_[A-Z0-9_]+|Q\d_K_[SML]|Q\d_K|Q\d_\d|BF16|FP16|F16|Q8_0|AWQ|GPTQ|GGUF|INT4|FP8|EXL2)", re.I)
SIZE_RE = re.compile(r"(\d+\.?\d*)\s*[Bb](?![a-zA-Z])")


def size_bucket(name):
    m = SIZE_RE.findall(name)
    if not m:
        return "无标注"
    try:
        v = float(m[-1])
    except Exception:
        return "无标注"
    if v < 1:
        return "<1B"
    if v < 3:
        return "1-3B"
    if v < 8:
        return "3-8B"
    if v < 14:
        return "8-14B"
    if v < 32:
        return "14-32B"
    if v < 70:
        return "32-70B"
    return "70B+"


def main():
    rows = []
    for line in open(IN_FILE, encoding="utf-8"):
        try:
            rows.append(json.loads(line))
        except Exception:
            pass
    print(f"读入 {len(rows)} 条验证通过记录")

    users = sorted({r["user"] for r in rows})
    gpus = sorted({r["gpu"] for r in rows})

    usergpu = Counter((r["user"], r["gpu"]) for r in rows)
    model_users = defaultdict(set)
    model_gpus = defaultdict(set)
    for r in rows:
        model_users[r["model"]].add(r["user"])
        model_gpus[r["model"]].add(r["gpu"])

    # --- 矩阵 CSV ---
    with open(os.path.join(OUT, "user_gpu_matrix.csv"), "w", newline="", encoding="utf-8-sig") as f:
        w = csv.writer(f)
        w.writerow(["账号"] + gpus + ["合计"])
        for u in users:
            line = [u] + [usergpu[(u, g)] for g in gpus]
            w.writerow(line + [sum(usergpu[(u, g)] for g in gpus)])
        w.writerow(["合计"] + [sum(usergpu[(u, g)] for u in users) for g in gpus] + [len(rows)])

    # --- 卡 x 模型 ---
    with open(os.path.join(OUT, "models_by_gpu.csv"), "w", newline="", encoding="utf-8-sig") as f:
        w = csv.writer(f)
        w.writerow(["卡", "模型", "提交人数", "提交人"])
        seen = set()
        for r in rows:
            k = (r["gpu"], r["model"])
            if k in seen:
                continue
            seen.add(k)
            w.writerow([r["gpu"], r["model"], len(model_users[r["model"]]), ";".join(sorted(model_users[r["model"]]))])

    # --- 去重模型 ---
    with open(os.path.join(OUT, "models_unique.csv"), "w", newline="", encoding="utf-8-sig") as f:
        w = csv.writer(f)
        w.writerow(["模型", "通过卡数", "卡列表", "提交人数", "作者", "规模", "格式标识"])
        for m in sorted(model_users):
            q = sorted({x.upper() for x in QUANT_RE.findall(m)})
            w.writerow([m, len(model_gpus[m]), ";".join(sorted(model_gpus[m])),
                        len(model_users[m]), m.split("/")[0], size_bucket(m), ";".join(q)])

    # --- 匿名版（去掉账号，仅保留 卡+模型+时间） ---
    with open(os.path.join(OUT, "anonymized_records.csv"), "w", newline="", encoding="utf-8-sig") as f:
        w = csv.writer(f)
        w.writerow(["卡", "机器名", "模型", "任务类型", "时间"])
        for r in rows:
            w.writerow([r["gpu"], r["machine"], r["model"], r["level"], r["time"]])

    # --- REPORT.md ---
    auth = Counter(r["model"].split("/")[0] for r in rows)
    sizes = Counter(size_bucket(r["model"]) for r in rows)
    fmt = Counter()
    for r in rows:
        for x in QUANT_RE.findall(r["model"]):
            fmt[x.upper()] += 1
            break
    levels = Counter(r["level"] or "未标注" for r in rows)

    L = []
    L.append("# ModelHub XC 验证通过记录分析\n")
    L.append(f"- 记录总数：**{len(rows):,}** 条（status=success 且 verifyResult=1）")
    L.append(f"- 去重模型：**{len(model_users):,}** 个")
    L.append(f"- 涉及账号：{len(users)} 个；卡：{len(gpus)} 张\n")
    L.append("## 一、账号 × 卡 矩阵（验证通过条数）\n")
    L.append("| 账号 | " + " | ".join(gpus) + " | 合计 |")
    L.append("|" + "---|" * (len(gpus) + 2))
    for u in users:
        vals = [str(usergpu[(u, g)] or "") for g in gpus]
        L.append(f"| {u} | " + " | ".join(vals) + f" | {sum(usergpu[(u, g)] for g in gpus)} |")
    L.append("| **合计** | " + " | ".join(str(sum(usergpu[(u, g)] for u in users)) for g in gpus) + f" | **{len(rows)}** |\n")

    L.append("## 二、模型作者 Top 20\n")
    L.append("| 作者 | 条数 | 占比 |")
    L.append("|---|---|---|")
    for a, n in auth.most_common(20):
        L.append(f"| {a} | {n} | {n*100/len(rows):.1f}% |")

    L.append("\n## 三、模型规模分布\n")
    L.append("| 规模 | 条数 | 占比 |")
    L.append("|---|---|---|")
    for k in ["<1B", "1-3B", "3-8B", "8-14B", "14-32B", "32-70B", "70B+", "无标注"]:
        if sizes.get(k):
            L.append(f"| {k} | {sizes[k]} | {sizes[k]*100/len(rows):.1f}% |")

    L.append("\n## 四、模型格式标识（名字里带的）\n")
    L.append("| 标识 | 条数 |")
    L.append("|---|---|")
    for k, n in fmt.most_common(12):
        L.append(f"| {k} | {n} |")

    L.append("\n## 五、任务类型\n")
    L.append("| 类型 | 条数 |")
    L.append("|---|---|")
    for k, n in levels.most_common(12):
        L.append(f"| {k} | {n} |")

    L.append("\n## 六、跨卡通用模型 Top 20（同一模型在多张卡上验证通过）\n")
    L.append("| 模型 | 通过卡数 | 人数 |")
    L.append("|---|---|---|")
    for m, _ in sorted(model_gpus.items(), key=lambda kv: -len(kv[1]))[:20]:
        L.append(f"| {m} | {len(model_gpus[m])} | {len(model_users[m])} |")

    with open(os.path.join(OUT, "REPORT.md"), "w", encoding="utf-8") as f:
        f.write("\n".join(L) + "\n")
    print(f"报表已生成: {OUT}")
    for fn in sorted(os.listdir(OUT)):
        p = os.path.join(OUT, fn)
        print(f"  {fn:26s} {os.path.getsize(p)/1024:8.1f} KB")


if __name__ == "__main__":
    main()
