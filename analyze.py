import json, os
from gemini_client import call_gemini_json


def analyze_all():
    cases = {c["id"]: c for c in json.load(open("output/cases.json", encoding="utf-8"))}
    results = json.load(open("output/results.json", encoding="utf-8"))
    template = open("prompts/analyze_failure.md", encoding="utf-8").read()

    os.makedirs("output/bug_reports", exist_ok=True)
    verdicts = []

    failed = [r for r in results if not r["passed"]]
    print(f"[3] Đang phân tích {len(failed)}/{len(results)} test case thất bại bằng Gemini AI...")

    for idx, r in enumerate(failed, 1):
        tc = cases[r["id"]]
        print(f"  ({idx}/{len(failed)}) Phân tích {r['id']} - {tc['title']}")
        prompt = (template
            .replace("{{CASE}}", json.dumps(tc, ensure_ascii=False))
            .replace("{{EXPECTED}}", json.dumps(tc["expected"], ensure_ascii=False))
            .replace("{{ACTUAL}}", r["actual"])
            .replace("{{SCREENSHOT}}", r["screenshot"]))

        try:
            a = call_gemini_json(prompt)
        except Exception as e:  # 1 case lỗi không làm dừng cả quy trình
            print(f"    [Lỗi] Không phân tích được {r['id']}: {e}")
            a = {"verdict": "analysis_failed", "probable_cause": f"AI không phân tích được: {e}"}
        a["test_id"] = r["id"]
        verdicts.append(a)

        if a.get("verdict") == "real_bug":
            title_text = a.get('title', tc['title'])
            severity_text = a.get('severity', 'major')
            severity_reason = a.get('severity_reason', '')
            confidence_text = a.get('confidence', 'medium')
            expected_json = json.dumps(tc['expected'], ensure_ascii=False, indent=2)
            steps_list = "\n".join(f"{i+1}. {s}" for i, s in enumerate(a.get('steps_to_reproduce', [])))
            cause_text = a.get('probable_cause', 'Chưa xác định')

            md = (
                f"# BUG REPORT: {title_text}\n\n"
                f"- **Mã Test Case:** {tc['id']} – {tc['title']}\n"
                f"- **Nhóm:** {tc.get('category', '-')}\n"
                f"- **Mức độ nghiêm trọng:** {severity_text} ({severity_reason})\n"
                f"- **Độ tin cậy của AI:** {confidence_text}\n\n"
                f"## Kết quả mong đợi\n```json\n{expected_json}\n```\n\n"
                f"## Kết quả thực tế\n{r['actual']}\n\n"
                f"## Các bước tái hiện\n{steps_list}\n\n"
                f"## Nguyên nhân gốc rễ (Phân tích AI)\n{cause_text}\n\n"
                f"## Bằng chứng màn hình\n![Screenshot](../screenshots/{r['id']}.png)\n"
            )
            open(f"output/bug_reports/{r['id']}.md", "w", encoding="utf-8").write(md)

    json.dump(verdicts, open("output/verdicts.json", "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    print_and_save_summary(cases, results, verdicts)


def print_and_save_summary(cases, results, verdicts):
    vmap = {v["test_id"]: v for v in verdicts}
    passed = sum(1 for r in results if r["passed"])
    failed = len(results) - passed
    real_bugs = sum(1 for v in verdicts if v.get("verdict") == "real_bug")

    lines = []
    lines.append("=" * 70)
    lines.append("BÁO CÁO TỔNG HỢP KẾT QUẢ KIỂM THỬ")
    lines.append("=" * 70)
    lines.append(f"Tổng số test case : {len(results)}")
    lines.append(f"Đạt (PASS)        : {passed}")
    lines.append(f"Thất bại (FAIL)   : {failed}")
    lines.append(f"Lỗi thật (bug)    : {real_bugs}")
    lines.append("")

    # Thống kê theo nhóm
    by_cat = {}
    for r in results:
        cat = cases.get(r["id"], {}).get("category", "Khác")
        s = by_cat.setdefault(cat, [0, 0])
        s[0 if r["passed"] else 1] += 1
    lines.append("--- Thống kê theo nhóm ---")
    for cat, (p, f) in by_cat.items():
        lines.append(f"  {cat}: {p} đạt / {f} thất bại")
    lines.append("")

    lines.append("--- Chi tiết TẤT CẢ test case ---")
    for r in results:
        tc = cases.get(r["id"], {})
        status = "PASS" if r["passed"] else "FAIL"
        lines.append(f"[{status}] {r['id']} | {tc.get('category', '-')} | {tc.get('title', '')}")
        if not r["passed"]:
            v = vmap.get(r["id"], {})
            lines.append(f"       Kết quả thực tế : {r['actual']}")
            lines.append(f"       Kết luận AI     : {v.get('verdict', '-')}"
                         f" | mức độ: {v.get('severity', '-')} | tin cậy: {v.get('confidence', '-')}")
            lines.append(f"       Nguyên nhân     : {v.get('probable_cause', '-')}")
    lines.append("=" * 70)

    text = "\n".join(lines)
    print(text)
    open("output/summary.txt", "w", encoding="utf-8").write(text)
    print("[3] Phân tích hoàn tất. Báo cáo lỗi: output/bug_reports/ | Tổng hợp: output/summary.txt")


if __name__ == "__main__":
    analyze_all()