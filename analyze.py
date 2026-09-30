import json, os, re
from gemini_client import call_gemini


def extract_json(text: str):
    text = re.sub(r"^```(?:json)?|```$", "", text.strip(), flags=re.M).strip()
    return json.loads(text)


def analyze_all():
    cases = {c["id"]: c for c in json.load(open("output/cases.json", encoding="utf-8"))}
    results = json.load(open("output/results.json", encoding="utf-8"))
    template = open("prompts/analyze_failure.md", encoding="utf-8").read()

    os.makedirs("output/bug_reports", exist_ok=True)
    verdicts = []

    print("[3] Đang gọi Gemini AI để phân tích các test case thất bại (tự động thử lại + đổi model nếu quá tải)...")

    for r in results:
        if r["passed"]:
            continue
        tc = cases[r["id"]]
        prompt = (template
            .replace("{{CASE}}", json.dumps(tc, ensure_ascii=False))
            .replace("{{EXPECTED}}", json.dumps(tc["expected"], ensure_ascii=False))
            .replace("{{ACTUAL}}", r["actual"])
            .replace("{{SCREENSHOT}}", r["screenshot"]))

        a = extract_json(call_gemini(prompt))
        a["test_id"] = r["id"]
        verdicts.append(a)

        if a["verdict"] == "real_bug":
            title_text = a.get('title', tc['title'])
            severity_text = a.get('severity', 'major')
            severity_reason = a.get('severity_reason', '')
            confidence_text = a.get('confidence', 'medium')
            expected_json = json.dumps(tc['expected'], ensure_ascii=False, indent=2)
            actual_text = r['actual']
            steps_list = "\n".join(f"{i+1}. {s}" for i, s in enumerate(a.get('steps_to_reproduce', [])))
            cause_text = a.get('probable_cause', 'Chưa xác định')
            shot_id = r['id']

            md = (
                f"# BUG REPORT: {title_text}\n\n"
                f"- **Mã Test Case:** {tc['id']} – {tc['title']}\n"
                f"- **Mức độ nghiêm trọng:** {severity_text} ({severity_reason})\n"
                f"- **Độ tin cậy của AI:** {confidence_text}\n\n"
                f"## Kết quả mong đợi\n```json\n{expected_json}\n```\n\n"
                f"## Kết quả thực tế\n{actual_text}\n\n"
                f"## Các bước tái hiện\n{steps_list}\n\n"
                f"## Nguyên nhân gốc rễ (Phân tích AI)\n{cause_text}\n\n"
                f"## Bằng chứng màn hình\n![Screenshot](../screenshots/{shot_id}.png)\n"
            )
            open(f"output/bug_reports/{r['id']}.md", "w", encoding="utf-8").write(md)

    json.dump(verdicts, open("output/verdicts.json", "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    print("[3] Phân tích hoàn tất. Đã ghi nhận báo cáo lỗi vào thư mục output/bug_reports/")


if __name__ == "__main__":
    analyze_all()