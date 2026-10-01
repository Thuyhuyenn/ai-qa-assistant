# AI WORKLOG

## 1. Mục đích

Tệp này ghi lại cách các công cụ AI được sử dụng trong dự án AI Autonomous QA
Agent, những phần AI hỗ trợ, các đầu ra chưa chính xác đã phát hiện, biện pháp
đã áp dụng để cải thiện và các việc cần làm tiếp theo.

AI trong dự án đóng vai trò **trợ lý sinh và phân tích**. Kết quả của AI không
được xem là bằng chứng cuối cùng thay cho việc tái hiện và xác minh của QA.

## 2. Các công cụ AI đã sử dụng

### Google Gemini API

Gemini được gọi qua [`gemini_client.py`](C:/Users/ASUS-PRO/ai-qa-assistant/gemini_client.py)
và là công cụ AI chính trong runtime của ứng dụng.

Các model được cấu hình theo thứ tự ưu tiên:

```text
gemini-3.8-flash
gemini-3.7-flash
gemini-3.5-flash-lite
```

Gemini được sử dụng cho hai nhiệm vụ:

1. Sinh test case từ user story.
2. Phân tích các test case thất bại và phân loại nguyên nhân.

### AI assistant/Copilot SDK trong quá trình phát triển

AI assistant sử dụng Copilot SDK trong VS Code được dùng để đọc cấu trúc
repository, phân tích mã nguồn, tổng hợp kết quả thực thi và soạn thảo tài liệu
README/worklog. AI assistant không được dùng để giả lập kết quả chạy test hoặc
thay thế dữ liệu thực tế đã lưu trong `output/`.

### Playwright (không phải mô hình AI)

Playwright là công cụ tự động hóa trình duyệt, không phải công cụ AI. Nó được
dùng để cung cấp bằng chứng thực thi cho phần phân tích của Gemini: PASS/FAIL,
URL thực tế, thông báo lỗi, thời gian chạy và screenshot.

## 3. AI hỗ trợ như thế nào

### 3.1. Sinh test case

File [`prompts/generate_cases.md`](C:/Users/ASUS-PRO/ai-qa-assistant/prompts/generate_cases.md)
định nghĩa vai trò Senior QA, user story, selector, tài khoản demo và schema
JSON bắt buộc.

[`generate_cases.py`](C:/Users/ASUS-PRO/ai-qa-assistant/generate_cases.py) gọi
Gemini riêng cho sáu nhóm:

- Luồng chính (happy path).
- Dữ liệu không hợp lệ.
- Giá trị biên và ký tự đặc biệt.
- Bảo mật.
- Phiên đăng nhập và điều hướng.
- Giao diện, khả năng sử dụng và hiển thị dữ liệu.

AI phải tạo các trường như `id`, `type`, `title`, `steps`, `data`, `expected`,
`why_it_matters` và `priority`. Sau khi nhận kết quả, code:

- Yêu cầu JSON thay vì văn bản tự do.
- Loại bỏ case trùng theo `title`.
- Gắn `category` theo nhóm đang sinh.
- Đánh lại ID liên tục để tránh ID trùng hoặc bị thiếu.
- Ghi kết quả vào `output/cases.json`.

### 3.2. Phân tích test thất bại

File [`prompts/analyze_failure.md`](C:/Users/ASUS-PRO/ai-qa-assistant/prompts/analyze_failure.md)
giới hạn AI vào ba kết luận:

- `real_bug`: lỗi có khả năng thuộc về ứng dụng.
- `test_error`: test hoặc expected không đúng.
- `needs_review`: chưa đủ bằng chứng.

Đầu vào phân tích gồm test case, expected, actual và đường dẫn screenshot.
[`analyze.py`](C:/Users/ASUS-PRO/ai-qa-assistant/analyze.py) chỉ gửi các case
FAIL để tiết kiệm chi phí và tạo:

- `output/verdicts.json`.
- `output/summary.txt`.
- `output/bug_reports/*.md` khi verdict là `real_bug`.

### 3.3. Tăng độ tin cậy khi gọi AI

[`gemini_client.py`](C:/Users/ASUS-PRO/ai-qa-assistant/gemini_client.py) đã
được thiết kế để:

- Dùng `response_mime_type="application/json"` cho các tác vụ cần JSON.
- Parse cả JSON thuần và JSON bị bọc trong markdown code fence.
- Thử lại khi model trả JSON lỗi hoặc bị cắt.
- Retry khi server quá tải (`500/503`).
- Chờ lại khi bị giới hạn tốc độ (`429`).
- Chuyển sang model dự phòng khi model hiện tại không khả dụng (`404`).
- Dùng temperature thấp để giảm biến động trong cùng một đầu vào.

## 4. Các đầu ra không chính xác hoặc có rủi ro

### 4.1. AI sinh case vượt quá khả năng thực thi của runner

Prompt yêu cầu bao phủ Back/Forward, F5, logout, nhiều tab, session hết hạn,
double submit và các tình huống giao diện. Tuy nhiên
[`run_tests.py`](C:/Users/ASUS-PRO/ai-qa-assistant/run_tests.py) hiện chủ yếu
điền form đăng nhập, submit, kiểm tra URL/thông báo và chạy một số post-check.

Vì vậy, một số case có thể **mô tả đúng về mặt ý tưởng nhưng chưa được thực thi
đúng các bước trong `steps`**. Đây là rủi ro tạo false positive hoặc false
negative, đặc biệt với nhóm quản lý phiên và điều hướng.

**Cải thiện đã thực hiện:** README đã ghi rõ giới hạn này và không coi snapshot
hiện tại là bằng chứng cho toàn bộ hành vi được mô tả trong test case.

**Cần cải thiện thêm:** xây dựng executor theo loại thao tác, hỗ trợ riêng
logout, reload, back/forward, nhiều tab, timeout và kiểm tra session.

### 4.2. AI suy đoán nguyên nhân gốc từ bằng chứng hạn chế

Các bug report hiện chỉ cung cấp dữ liệu UI, URL, actual và screenshot; không có
server log, network trace, cookie state hoặc source code của SauceDemo. Do đó,
những câu như “cookie/token chưa bị xóa” hoặc “LocalStorage/SessionStorage
không đồng bộ” là **nguyên nhân có khả năng xảy ra**, chưa phải kết luận kỹ
thuật đã được chứng minh.

Ví dụ các báo cáo:

- [`TC37.md`](C:/Users/ASUS-PRO/ai-qa-assistant/output/bug_reports/TC37.md):
  AI suy đoán session cũ được tái sử dụng sau Back.
- [`TC42.md`](C:/Users/ASUS-PRO/ai-qa-assistant/output/bug_reports/TC42.md):
  AI suy đoán session giữa các tab không được đồng bộ.
- [`TC44.md`](C:/Users/ASUS-PRO/ai-qa-assistant/output/bug_reports/TC44.md):
  AI suy đoán trạng thái/token được lưu trước khi xác thực hoàn tất.

**Cải thiện đã thực hiện:** prompt bắt buộc AI chỉ dựa trên bằng chứng được
cung cấp, ghi `confidence`, `reasoning` và phân biệt `real_bug`,
`test_error`, `needs_review`. Bug report cũng ghi rõ đây là “Phân tích AI”.

**Cần cải thiện thêm:** thu thập HAR, console log, request/response, cookie và
storage state; yêu cầu AI trích dẫn từng bằng chứng trước khi nêu nguyên nhân;
đưa bug report qua bước review thủ công.

### 4.3. Expected do AI sinh có thể không phù hợp với ứng dụng thực tế

AI có thể tạo `error_contains` quá cụ thể, chọn thông báo không đúng phiên bản
website hoặc đặt kỳ vọng chặt hơn hành vi thực tế. Khi đó test có thể FAIL dù
ứng dụng không sai, tương ứng với nhóm `test_error`.

**Cải thiện đã thực hiện:** prompt cung cấp selector, URL đích, tài khoản demo
và yêu cầu từ khóa lỗi tiếng Anh thực tế; analyzer có nhãn `test_error` và
`needs_review` thay vì bắt buộc mọi FAIL là bug.

**Cần cải thiện thêm:** kiểm tra schema và tập giá trị hợp lệ trước khi chạy;
đối chiếu expected với baseline của website; cho phép assertion theo semantic
hoặc pattern ổn định thay vì so khớp chuỗi cứng.

### 4.4. JSON trả về có thể lỗi hoặc không đầy đủ

Trong thực tế model có thể trả JSON kèm markdown, JSON bị cắt hoặc cấu trúc
được bọc trong một object như `{"test_cases": [...]}`.

**Cải thiện đã thực hiện:** `parse_json()` loại code fence và tìm phần JSON;
client retry khi parse lỗi; generator xử lý trường hợp model bọc danh sách
trong object; các nhóm lỗi riêng lẻ được bỏ qua để không làm mất toàn bộ nhóm
đã sinh.

**Cần cải thiện thêm:** dùng JSON Schema/Pydantic để validate từng trường,
ghi lại response lỗi để debug an toàn và báo lỗi rõ ràng nếu thiếu trường bắt
buộc thay vì tiếp tục với dữ liệu không hợp lệ.

### 4.5. AI có thể tạo case trùng hoặc phân bố không đều

Sinh sáu lần riêng giúp giảm kích thước mỗi response nhưng vẫn có thể tạo hai
case khác câu chữ nhưng cùng ý nghĩa. Việc loại trùng hiện chỉ dựa trên
`title` viết thường, chưa hiểu ngữ nghĩa. Số lượng case giữa các nhóm cũng có
thể không cân bằng.

**Cải thiện đã thực hiện:** sinh theo category, yêu cầu không trùng và dedupe
theo tiêu đề trước khi đánh ID.

**Cần cải thiện thêm:** dedupe theo embedding/semantic similarity, kiểm tra
coverage matrix và báo cáo các khoảng trống của yêu cầu.

## 5. Kết quả snapshot đã ghi nhận

Theo các file trong `output/`:

- 52 test case được sinh.
- 45 PASS và 7 FAIL.
- 7 case thất bại được gửi cho Gemini phân tích.
- 3 case được phân loại `real_bug`: TC37, TC42 và TC44.
- Các kết luận này vẫn cần tái hiện thủ công trước khi xem là bug chính thức.

Các con số trên là kết quả của một lần chạy cụ thể. Chúng có thể thay đổi theo
trạng thái website, model, prompt, network, quota và dữ liệu đầu vào.

## 6. Những gì đã cải thiện trong quá trình phát triển

- Chuyển đầu ra sinh test và phân tích sang JSON có cấu trúc.
- Tách prompt sinh test và prompt phân tích để dễ kiểm soát vai trò AI.
- Chia sinh test theo nhóm thay vì yêu cầu một response quá lớn.
- Loại bỏ tiêu đề trùng và đánh lại ID liên tục.
- Chỉ phân tích case FAIL thay vì gửi toàn bộ kết quả cho AI.
- Lưu screenshot cho từng case để AI và QA có bằng chứng đối chiếu.
- Thêm retry, backoff và model fallback cho các lỗi API thường gặp.
- Tách verdict `real_bug`, `test_error` và `needs_review`.
- Ghi confidence, severity, reasoning và probable cause vào kết quả phân tích.
- Phát hiện và sửa prompt runtime từng chứa lệnh `Set-Content` cùng nội dung
  mojibake; chuẩn hóa lại prompt thành Markdown UTF-8 chỉ chứa hướng dẫn gửi cho
  Gemini.
- Ghi nhận rõ các giới hạn của AI trong README thay vì trình bày suy đoán như
  sự thật chắc chắn.

## 7. Kế hoạch cải thiện tiếp theo

### Ưu tiên cao

1. Thêm schema validation cho mọi response từ Gemini.
2. Mở rộng runner để thực thi đầy đủ các bước phức tạp trong test case thay vì
   chỉ xử lý luồng đăng nhập và các post-check cơ bản.
3. Thu thập browser console, network trace, cookie/storage và HTML snapshot khi
   FAIL.
4. Thêm bước QA review bắt buộc trước khi tạo hoặc phát hành bug report.
5. Viết unit test cho parser JSON, deduplication, mapping expected và analyzer.

### Ưu tiên trung bình

1. Tách selector, credential demo và URL khỏi code để hỗ trợ nhiều ứng dụng.
2. Dùng semantic deduplication và coverage report để đo chất lượng bộ test.
3. Lưu lịch sử từng run, model, prompt version và artifact để so sánh kết quả.
4. Bổ sung cơ chế self-healing có kiểm soát; chỉ đề xuất thay đổi locator và
   yêu cầu QA phê duyệt, không tự sửa mù.

### Nguyên tắc tiếp tục sử dụng AI

- AI đề xuất, code kiểm chứng.
- Mọi kết luận bug phải có bằng chứng tái hiện.
- Không gửi secret, token hoặc dữ liệu nhạy cảm vào prompt.
- Ghi phiên bản model/prompt cùng kết quả để có thể truy vết.
- Ưu tiên `needs_review` khi bằng chứng chưa đủ thay vì ép AI kết luận.