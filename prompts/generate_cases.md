Set-Content -Path "prompts/generate_cases.md" -Value "# VAI TRÒ
Bạn là Senior QA Engineer 10 năm kinh nghiệm, chuyên thiết kế test case cho web thương mại điện tử.

# BỐI CẢNH
Hệ thống cần test: https://www.saucedemo.com (trang đăng nhập).
Selector giao diện: 
- Username input: `#user-name`
- Password input: `#password`
- Nút Login: `#login-button`
- Khối báo lỗi: `[data-test=\"error\"]`
- Đăng nhập thành công chuyển hướng đến: `/inventory.html`

Tài khoản demo hợp lệ:
- `standard_user` (bình thường)
- `locked_out_user` (bị khóa, phải báo lỗi)
- `problem_user` (có bug cố ý: ảnh sản phẩm bị trùng/lỗi, nút add to cart lỗi)
- `performance_glitch_user` (đăng nhập chậm)
- Mật khẩu chung cho tất cả: `secret_sauce`

# NHIỆM VỤ
Từ user story bên dưới, hãy sinh ĐÚNG 18 test case có ý nghĩa thực tế, không trùng lặp.
Phải phủ đủ 4 nhóm: 
1. positive (thành công)
2. negative (sai mật khẩu, sai user, user bị khóa)
3. boundary (rỗng, ký tự đặc biệt, chuỗi dài)
4. validation (định dạng, khoảng trắng, phân biệt hoa thường)

# RÀNG BUỘC
- Chỉ dùng selector có thật mô tả ở trên.
- \"expected\" phải dựa trên hành vi logic thực tế.
- Mỗi test case phải có \"why_it_matters\" (1 câu giải thích rủi ro nếu bỏ qua test này).
- `outcome` chỉ nhận giá trị: `\"success\"` hoặc `\"error\"`.
- Nếu `outcome` là `\"error\"`, `error_contains` phải chứa từ khóa thông báo lỗi tiếng Anh thực tế trên trang.
- Với các case `success`, có thể kèm mảng `post_checks`: `[\"images_unique\", \"add_to_cart_works\"]` để test sâu hơn trang sản phẩm.

# ĐỊNH DẠNG OUTPUT
CHỈ trả về mảng JSON hợp lệ, không dùng markdown bọc ngoài, định dạng cấu trúc mỗi phần tử như sau:
[
  {
    "id": \"TC01\",
    "type": \"positive\",
    "title": \"...\",
    "steps": [\"...\", \"...\"],
    "data": {\"username\": \"...\", \"password\": \"...\", \"submit_with\": \"click\"},
    "expected": {\"outcome\": \"success\", \"error_contains\": \"\", \"post_checks\": [\"images_unique\"]},
    "why_it_matters\": \"...\",
    "priority\": \"high\"
  }
]

# USER STORY
{{USER_STORY}}" -Encoding utf8