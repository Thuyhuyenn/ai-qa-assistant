import json, os, re, sys
from gemini_client import call_gemini


def extract_json(text: str):
    text = re.sub(r"^```(?:json)?|```$", "", text.strip(), flags=re.M).strip()
    return json.loads(text)


def generate(user_story: str, out_path="output/cases.json"):
    prompt_template = open("prompts/generate_cases.md", encoding="utf-8").read()
    prompt = prompt_template.replace("{{USER_STORY}}", user_story)

    print("[1] Đang gọi Gemini AI để sinh test cases (tự động thử lại + đổi model nếu quá tải)...")
    cases = extract_json(call_gemini(prompt))

    os.makedirs("output", exist_ok=True)
    json.dump(cases, open(out_path, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    print(f"[1] Đã sinh thành công {len(cases)} test cases -> {out_path}")
    return cases


if __name__ == "__main__":
    story = sys.argv[1] if len(sys.argv) > 1 else \
        "Là người dùng, tôi có thể đăng nhập bằng username và password để xem danh sách sản phẩm."
    generate(story)