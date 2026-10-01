# BUG REPORT: Hệ thống cho phép đăng nhập thành công khi username chứa ký tự xuống dòng ẩn

- **Mã Test Case:** TC_HP_28 – Đăng nhập sử dụng dữ liệu copy-paste có chứa ký tự xuống dòng ẩn
- **Nhóm:** Giá trị biên & ký tự đặc biệt
- **Mức độ nghiêm trọng:** major (Lỗi này làm sai lệch logic xác thực đầu vào, cho phép người dùng đăng nhập bằng dữ liệu bị dính ký tự thừa từ clipboard, gây tiềm ẩn rủi ro về bảo mật hoặc trải nghiệm người dùng không nhất quán.)
- **Độ tin cậy của AI:** high

## Kết quả mong đợi
```json
{
  "outcome": "error",
  "error_contains": "Username and password do not match",
  "post_checks": []
}
```

## Kết quả thực tế
Lẽ ra phải bị chặn ở trang đăng nhập nhưng lại vào được https://www.saucedemo.com/inventory.html

## Các bước tái hiện
1. Truy cập trang https://www.saucedemo.com
2. Dán chuỗi 'standard_user
' vào ô #user-name
3. Nhập 'secret_sauce' vào ô #password
4. Click vào nút #login-button

## Nguyên nhân gốc rễ (Phân tích AI)
Hệ thống backend hoặc frontend không thực hiện hàm sanitize (cắt bỏ ký tự trắng/ký tự xuống dòng ẩn như \n, \r) đối với trường input 'username' trước khi thực hiện truy vấn xác thực cơ sở dữ liệu.

## Bằng chứng màn hình
![Screenshot](../screenshots/TC_HP_28.png)
