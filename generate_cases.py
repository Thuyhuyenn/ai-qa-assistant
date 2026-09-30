import json, os, re, sys
from gemini_client import call_gemini_json

# Mỗi nhóm được sinh bằng 1 lần gọi riêng -> đầy đủ hơn và JSON ngắn, ít bị lỗi
CATEGORIES = [
    ("Luồng chính (happy path)",
     "các luồng thành công: dữ liệu hợp lệ, các cách thao tác khác nhau (bấm nút, nhấn Enter), kết quả sau khi thành công."),
    ("Dữ liệu không hợp lệ",
     "để trống từng trường/tất cả trường, sai username, sai password, đúng username sai password, "
     "tài khoản không tồn tại, tài khoản bị khóa, chỉ có khoảng trắng, phân biệt hoa/thường."),
    ("Giá trị biên & ký tự đặc biệt",
     "độ dài tối thiểu/tối đa/vượt quá, chuỗi rất dài, khoảng trắng đầu/cuối, ký tự đặc biệt, "
     "Unicode/tiếng Việt có dấu, emoji, copy-paste dữ liệu."),
    ("Bảo mật",
     "SQL injection, XSS, đăng nhập sai nhiều lần liên tiếp (brute-force/khóa tài khoản), "
     "thông báo lỗi lộ thông tin, password có bị che không, truy cập trang yêu cầu đăng nhập khi chưa đăng nhập, "
     "thông tin nhạy cảm trên URL."),
    ("Phiên đăng nhập & điều hướng",
     "đăng xuất, nút Back/Forward của trình duyệt sau đăng nhập/đăng xuất, tải lại trang (F5), "
     "phiên hết hạn, mở nhiều tab, bấm nút đăng nhập nhiều lần liên tiếp (double submit)."),
    ("Giao diện, khả năng sử dụng & hiển thị dữ liệu",
     "nhãn/placeholder/thông báo lỗi hiển thị đúng và rõ ràng, điều hướng bằng phím Tab, "
     "trạng thái loading, danh sách sản phẩm hiển thị đủ/đúng (rỗng, nhiều, thiếu ảnh/giá), responsive, hiển thị trên trình duyệt khác."),
]

PER_CATEGORY = "8 đến 12"


def _split_id(case_id: str):
    m = re.match(r"^(\D*)(\d+)$", str(case_id))
    return (m.group(1), len(m.group(2))) if m else ("TC", 2)


def generate(user_story: str, out_path="output/cases.json"):
    template = open("prompts/generate_cases.md", encoding="utf-8").read()
    base_prompt = template.replace("{{USER_STORY}}", user_story)

    print("[1] Đang gọi Gemini AI để sinh test cases theo từng nhóm (đầy đủ mọi trường hợp)...")

    all_cases, seen_titles = [], set()
    for i, (name, desc) in enumerate(CATEGORIES, 1):
        prompt = (
            base_prompt
            + f"\n\n---\n## YÊU CẦU BỔ SUNG (QUAN TRỌNG)\n"
              f"Lần này CHỈ sinh test case thuộc nhóm: **{name}**.\n"
              f"Phạm vi nhóm này gồm: {desc}\n"
              f"Hãy liệt kê thật đầy đủ mọi trường hợp có thể xảy ra trong nhóm này, khoảng {PER_CATEGORY} test case, "
              f"không trùng lặp, gồm cả trường hợp bình thường lẫn bất thường.\n"
              f"Giữ NGUYÊN định dạng JSON và các trường như yêu cầu ở phần trên; "
              f"thêm trường \"category\": \"{name}\" vào mỗi test case. Chỉ trả về JSON."
        )
        print(f"  - Nhóm {i}/{len(CATEGORIES)}: {name} ...")
        try:
            cases = call_gemini_json(prompt)
        except Exception as e:
            print(f"    [Lỗi] Bỏ qua nhóm '{name}': {e}")
            continue
        if isinstance(cases, dict):  # phòng khi model bọc trong {"test_cases": [...]}
            cases = next((v for v in cases.values() if isinstance(v, list)), [])
        added = 0
        for c in cases:
            key = str(c.get("title", "")).strip().lower()
            if key in seen_titles:
                continue
            seen_titles.add(key)
            c["category"] = name
            all_cases.append(c)
            added += 1
        print(f"    -> {added} test case")

    if not all_cases:
        raise RuntimeError("Không sinh được test case nào. Hãy thử lại sau.")

    # Đánh lại id liên tục, giữ kiểu id mà model đang dùng (vd TC01)
    prefix, width = _split_id(all_cases[0].get("id", "TC01"))
    width = max(width, 2)
    for n, c in enumerate(all_cases, 1):
        c["id"] = f"{prefix}{n:0{width}d}"

    os.makedirs("output", exist_ok=True)
    json.dump(all_cases, open(out_path, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    print(f"[1] Đã sinh thành công {len(all_cases)} test cases -> {out_path}")
    return all_cases


if __name__ == "__main__":
    story = sys.argv[1] if len(sys.argv) > 1 else \
        "Là người dùng, tôi có thể đăng nhập bằng username và password để xem danh sách sản phẩm."
    generate(story)