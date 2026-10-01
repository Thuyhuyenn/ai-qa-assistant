# AI Autonomous QA Agent

Hệ thống hỗ trợ kiểm thử web tự động bằng AI. Từ một user story, hệ thống dùng
Google Gemini để sinh test case, Playwright để chạy test trên SauceDemo, sau đó
dùng Gemini để phân tích các lần chạy thất bại và tạo bug report có ảnh chụp
màn hình.

Đây là prototype hỗ trợ QA, không thay thế việc tái hiện và xác minh thủ công.

## 1. Vì sao chọn SauceDemo?

[SauceDemo](https://www.saucedemo.com) được chọn vì:

- Là website demo công khai, dễ truy cập và không cần dữ liệu người dùng thật.
- Có tài khoản demo với nhiều trạng thái: người dùng bình thường, tài khoản bị
  khóa và tài khoản mô phỏng lỗi.
- Có luồng đăng nhập rõ ràng, selector ổn định và URL đích dễ xác minh.
- Có trang danh sách sản phẩm và giỏ hàng để kiểm tra hành vi sau đăng nhập.
- Có các lỗi được thiết kế sẵn, phù hợp để đánh giá khả năng phát hiện và phân
  tích lỗi của pipeline AI.
- Có thể chạy lặp lại bằng Playwright headless mà không ảnh hưởng hệ thống
  production.

SauceDemo là đối tượng kiểm thử mẫu, không phải ứng dụng do project phát triển.
Kết luận bug chỉ có giá trị trong phiên bản website và môi trường chạy cụ thể.

## 2. Phạm vi kiểm thử

User story chính:

> Người dùng có thể đăng nhập bằng username và password để xem danh sách sản
> phẩm.

Các phần được kiểm thử:

1. **Đăng nhập thành công**: dữ liệu hợp lệ, submit bằng click hoặc Enter và
   chuyển đến `/inventory.html`.
2. **Dữ liệu không hợp lệ**: bỏ trống trường, sai username/password, tài khoản
   không tồn tại và tài khoản bị khóa.
3. **Giá trị biên**: chuỗi dài, khoảng trắng, Unicode, emoji, ký tự đặc biệt và
   dữ liệu copy-paste.
4. **Bảo mật ở mức giao diện**: truy cập trang được bảo vệ khi chưa đăng nhập,
   thử đăng nhập nhiều lần, thông báo lỗi và che mật khẩu.
5. **Phiên và điều hướng**: logout, reload, Back/Forward, nhiều tab, session hết
   hạn và double submit.
6. **Giao diện và khả năng sử dụng**: label, placeholder, thông báo lỗi,
   loading, Tab navigation, hiển thị sản phẩm và responsive.
7. **Hành vi sau đăng nhập**: ảnh sản phẩm không bị trùng và nút thêm sản phẩm
   vào giỏ hàng cập nhật badge.

Thanh toán thật, quản trị người dùng, API độc lập, hiệu năng, accessibility
chuyên sâu, kiểm thử production và khả năng tương thích đầy đủ trên nhiều trình
duyệt nằm ngoài phạm vi hiện tại.

## 3. Vấn đề và giải pháp

Kiểm thử thủ công tốn thời gian khi chuyển user story thành nhiều case, dễ bỏ
sót dữ liệu biên hoặc lỗi quản lý session, đồng thời khó thu thập bằng chứng
nhất quán. Ngoài ra, một test FAIL chưa chắc là bug của ứng dụng; có thể do
test sai hoặc thiếu dữ liệu.

Giải pháp gồm ba bước:

1. Gemini sinh test case theo sáu nhóm QA và lưu vào `output/cases.json`.
2. Playwright chạy từng case trong browser context riêng, ghi PASS/FAIL và
   screenshot vào `output/`.
3. Gemini phân tích chỉ các case FAIL, phân loại `real_bug`, `test_error` hoặc
   `needs_review`, rồi tạo `output/bug_reports/*.md` cho `real_bug`.

## 4. Chiến lược thử nghiệm

Chiến lược kiểm thử bắt đầu từ user story đăng nhập và ưu tiên các rủi ro có
ảnh hưởng trực tiếp đến khả năng truy cập sản phẩm:

1. Xác định luồng quan trọng nhất: đăng nhập hợp lệ và chuyển đến inventory.
2. Mở rộng theo bốn loại bắt buộc: positive, negative, boundary và validation.
3. Bổ sung các nhóm rủi ro thường bị bỏ sót: bảo mật, session/điều hướng và
   khả năng sử dụng.
4. Mỗi case có dữ liệu, expected, mức ưu tiên và lý do cần kiểm thử.
5. Thực thi tự động bằng Playwright Chromium; mỗi case dùng browser context
   riêng để tránh ảnh hưởng giữa các case.
6. Ghi actual, thời lượng và screenshot cho tất cả case, kể cả PASS.
7. Chỉ gửi case FAIL cho AI phân tích; QA xác minh lại `real_bug` trước khi
   phát hành báo cáo chính thức.

Generator kiểm tra tối thiểu 15 case và yêu cầu đủ bốn loại test trước khi ghi
`output/cases.json`. Snapshot hiện tại có 52 case: 19 positive, 20 negative,
11 boundary và 2 validation.

## 5. Kiến trúc và quy trình

```text
User story
    |
    v
generate_cases.py + prompts/generate_cases.md
    | Gemini sinh test case
    v
output/cases.json
    |
    v
run_tests.py + Playwright + SauceDemo
    | chạy test, kiểm tra kết quả, chụp ảnh
    v
output/results.json + output/screenshots/
    |
    v
analyze.py + prompts/analyze_failure.md
    | Gemini phân tích các case FAIL
    v
output/verdicts.json + output/summary.txt + output/bug_reports/
```

Thành phần chính:

- [`main.py`](C:/Users/ASUS-PRO/ai-qa-assistant/main.py): chạy toàn bộ pipeline.
- [`generate_cases.py`](C:/Users/ASUS-PRO/ai-qa-assistant/generate_cases.py):
  sinh, loại trùng và đánh lại ID test case.
- [`run_tests.py`](C:/Users/ASUS-PRO/ai-qa-assistant/run_tests.py): chạy test
  bằng Playwright Chromium headless.
- [`analyze.py`](C:/Users/ASUS-PRO/ai-qa-assistant/analyze.py): phân tích FAIL
  và tạo bug report.
- [`gemini_client.py`](C:/Users/ASUS-PRO/ai-qa-assistant/gemini_client.py):
  gọi Gemini, parse JSON, retry và fallback model.
- [`app.py`](C:/Users/ASUS-PRO/ai-qa-assistant/app.py): dashboard Streamlit.
- [`prompts/`](C:/Users/ASUS-PRO/ai-qa-assistant/prompts/): các prompt của AI.

## 6. Cách sử dụng

Yêu cầu Python 3.10+, Playwright Chromium, API key Gemini và kết nối mạng tới
Gemini/SauceDemo.

```powershell
$env:GEMINI_API_KEY = "YOUR_GEMINI_API_KEY"
python -m playwright install chromium
python main.py
```

Có thể truyền user story:

```powershell
python main.py "Là người dùng, tôi có thể đăng nhập để xem danh sách sản phẩm."
```

Hoặc chỉ rõ URL:

```powershell
python main.py "Là người dùng, tôi có thể đăng nhập để xem danh sách sản phẩm." `
  --url "https://www.saucedemo.com"
```

Chạy dashboard:

```powershell
streamlit run app.py
```

Các đầu ra chính:

| Đường dẫn | Nội dung |
|---|---|
| `output/cases.json` | Test case do AI sinh |
| `output/results.json` | Kết quả PASS/FAIL và actual |
| `output/verdicts.json` | Kết luận AI cho các case FAIL |
| `output/summary.txt` | Báo cáo tổng hợp |
| `output/screenshots/` | Ảnh chụp từng test |
| `output/bug_reports/` | Bug report của `real_bug` |

## 7. Cách sử dụng AI

Prompt [`generate_cases.md`](C:/Users/ASUS-PRO/ai-qa-assistant/prompts/generate_cases.md)
định nghĩa selector, tài khoản demo và schema JSON. Code gọi AI riêng cho sáu
nhóm: happy path, dữ liệu không hợp lệ, giá trị biên, bảo mật, session/điều
hướng và giao diện. Sau đó code loại tiêu đề trùng, gắn category và đánh lại ID.

Prompt [`analyze_failure.md`](C:/Users/ASUS-PRO/ai-qa-assistant/prompts/analyze_failure.md)
buộc Gemini chỉ dựa trên expected, actual và screenshot được cung cấp. Kết quả
phải có verdict, confidence, severity, reasoning, probable cause và bước tái
hiện. `probable_cause` là giả thuyết cần QA xác minh, không phải bằng chứng cuối
cùng.

`gemini_client.py` dùng JSON response mode, temperature thấp, retry khi JSON lỗi
hoặc server quá tải, chờ khi bị giới hạn 429 và chuyển model dự phòng khi model
không khả dụng.

## 8. Công việc đã hoàn thành và kết quả mẫu

- Hoàn thành pipeline sinh test, chạy test và phân tích FAIL end-to-end.
- Có screenshot cho từng test và bug report Markdown có bước tái hiện.
- Có dashboard hiển thị thống kê, test case và bug report.
- Có retry, JSON parsing, deduplication và phân loại verdict.
- Prompt runtime được lưu đúng dưới dạng Markdown UTF-8; không đưa lệnh tạo file
  hoặc nội dung mã hóa lỗi vào prompt gửi cho Gemini.

Snapshot hiện có trong `output/`:

- 52 test case.
- 45 PASS và 7 FAIL.
- 3 case được AI phân loại `real_bug`: TC37, TC42 và TC44.

Đây là kết quả của một lần chạy cụ thể và cần chạy lại pipeline sau khi thay
đổi prompt hoặc code. Kết quả có thể thay đổi theo model, prompt, quota,
network và trạng thái SauceDemo.

## 9. Hạn chế và hướng cải thiện

- Runner đang cố định URL và chủ yếu thực thi luồng đăng nhập; chưa thực thi đầy
  đủ các bước Back/Forward, F5, logout và nhiều tab được mô tả trong case.
- Runner đã nhận `target_url` và `user_story` từ command line/dashboard; tuy
  nhiên selector và dữ liệu test vẫn được thiết kế cho SauceDemo.
- Chưa có schema validation đầy đủ, unit test, CI/CD, lịch sử run và adapter cho
  nhiều website.
- AI vẫn có thể sinh expected chưa phù hợp, tạo case trùng hoặc suy đoán nguyên
  nhân khi thiếu server log/network trace.
- Chỉ chạy Chromium headless; chưa bao phủ đầy đủ browser, performance,
  accessibility và API testing.
- `prompts/self_heal.md` chưa được gọi trong pipeline.
- Dockerfile hiện có thể dùng `requirements.txt`; vẫn cần kiểm tra build trong
  môi trường Docker sạch trước khi triển khai.

Hướng cải thiện là thêm schema validation, executor theo loại thao tác, thu thập
console/network/storage state, review thủ công trước khi phát hành bug report,
semantic deduplication, lưu artifact theo build và self-healing có kiểm soát.

## 10. Đối chiếu với trọng tâm đánh giá

Project được thiết kế để được đánh giá theo chất lượng tư duy QA, không chỉ theo
số lượng test case:

| Tiêu chí | Cách project đáp ứng | Bằng chứng |
|---|---|---|
| Tư duy thử nghiệm | Bắt đầu từ luồng đăng nhập quan trọng, sau đó mở rộng theo rủi ro dữ liệu sai, bảo mật, session, usability và hành vi sau đăng nhập. | [generate_cases.py](C:/Users/ASUS-PRO/ai-qa-assistant/generate_cases.py), `category` trong `output/cases.json` |
| Trường hợp ngoại lệ | Có tài khoản bị khóa, sai từng loại dữ liệu, chuỗi dài, khoảng trắng, Unicode, ký tự đặc biệt, Back/Forward, reload và nhiều tab. | `output/cases.json`, các nhóm boundary/security/session |
| Tự động hóa | Dùng Playwright Chromium headless, context riêng cho mỗi case, kiểm tra URL/thông báo/post-check và chụp ảnh. | [run_tests.py](C:/Users/ASUS-PRO/ai-qa-assistant/run_tests.py), `output/results.json` |
| Phát hiện lỗi | Không coi mọi FAIL là bug; Gemini phân biệt `real_bug`, `test_error` và `needs_review`. Snapshot có 3 `real_bug` và 4 `test_error`. | `output/verdicts.json`, `output/bug_reports/` |
| Sử dụng AI | AI sinh case theo prompt có schema, được deduplicate và kiểm tra đủ bốn loại; AI phân tích chỉ dựa trên expected/actual/screenshot và có confidence. | [generate_cases.md](C:/Users/ASUS-PRO/ai-qa-assistant/prompts/generate_cases.md), [analyze_failure.md](C:/Users/ASUS-PRO/ai-qa-assistant/prompts/analyze_failure.md) |
| Bằng chứng | Mỗi case có actual, duration và screenshot; bug report có expected, actual, severity, probable cause, bước tái hiện và ảnh liên kết. | `output/results.json`, `output/screenshots/`, `output/bug_reports/` |
| Lý luận | Mỗi case bắt buộc có `why_it_matters`, nêu rủi ro nếu bỏ qua; chiến lược ưu tiên các luồng ảnh hưởng đến truy cập sản phẩm. | Trường `why_it_matters` trong `output/cases.json`, mục “Chiến lược thử nghiệm” |

### Đánh giá trung thực về độ tin cậy

Các case hiện đã được chạy tự động, nhưng executor chưa phải là một bộ máy thực
thi đầy đủ mọi câu trong `steps`. Nó thực thi chắc chắn luồng nhập liệu, submit,
kiểm tra URL/thông báo và hai post-check; một số case mô tả Back/Forward, F5,
logout hoặc nhiều tab nhưng runner chưa mô phỏng riêng từng thao tác đó. Vì vậy:

- Tư duy thử nghiệm, ngoại lệ, AI, bằng chứng và lý luận: **đã thể hiện rõ**.
- Phát hiện lỗi: **đã có đầu ra thực tế**, nhưng `real_bug` vẫn cần QA tái hiện.
- Tự động hóa đáng tin cậy: **đạt một phần**, cần mở rộng executor theo loại
  thao tác trước khi xem mọi kết quả là bằng chứng đầy đủ.

Đây là giới hạn được nêu công khai để tránh đánh đồng “AI đã sinh test case” với
“mọi bước của test case đã được thực thi”. Hướng khắc phục là xây dựng executor
theo action (`login`, `logout`, `reload`, `go_back`, `new_tab`, `assert`) và ghi
log từng action đã thực hiện vào `results.json`.

## Giấy phép

Repository hiện chưa khai báo license.
