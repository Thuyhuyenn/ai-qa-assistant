import json, os, time
from playwright.sync_api import sync_playwright

BASE = "https://www.saucedemo.com"

def check_images_unique(page):
    srcs = page.locator(".inventory_item_img img").evaluate_all("els => els.map(e => e.src)")
    ok = len(srcs) > 0 and len(set(srcs)) == len(srcs)
    return ok, f"{len(set(srcs))} ảnh khác nhau trên tổng số {len(srcs)} sản phẩm"

def check_add_to_cart(page):
    btn = page.locator("button[data-test^='add-to-cart']").first
    if btn.count() > 0:
        btn.click()
        badge = page.locator(".shopping_cart_badge")
        ok = badge.count() > 0 and badge.inner_text() == "1"
        return ok, f"Badge giỏ hàng = {badge.inner_text() if badge.count() else 'không xuất hiện'}"
    return False, "Không tìm thấy nút thêm vào giỏ hàng"

CHECKS = {"images_unique": check_images_unique, "add_to_cart_works": check_add_to_cart}

def run_case(page, tc, base_url=BASE):
    d, e = tc["data"], tc["expected"]
    page.goto(base_url)
    page.fill("#user-name", d.get("username", ""))
    page.fill("#password", d.get("password", ""))
    
    submit_with = d.get("submit_with", "click")
    if submit_with == "enter_on_username":
        page.press("#user-name", "Enter")
    elif submit_with in ("enter", "enter_on_password"):
        page.press("#password", "Enter")
    else:
        page.click("#login-button")
        
    page.wait_for_timeout(1000)
    
    if e["outcome"] == "success":
        if "inventory" not in page.url:
            err = page.locator("[data-test='error']")
            msg = err.inner_text() if err.count() else "không có thông báo"
            return False, f"Không vào được trang sản phẩm. URL={page.url}. Thông báo lỗi: {msg}"
        for name in e.get("post_checks", []):
            ok, detail = CHECKS[name](page)
            if not ok:
                return False, f"Kiểm tra nâng cao '{name}' thất bại: {detail}"
        return True, f"Đăng nhập thành công, URL={page.url}"
    
    err = page.locator("[data-test='error']")
    if "inventory" in page.url:
        return False, f"Lẽ ra phải bị chặn ở trang đăng nhập nhưng lại vào được {page.url}"
    if err.count() == 0:
        return False, "Hệ thống không hiển thị thông báo lỗi nào khi nhập sai"
    
    text = err.inner_text()
    want = e.get("error_contains", "").lower()
    if want and want not in text.lower():
        return False, f"Thông báo lỗi khác với mong đợi. Thực tế nhận được: '{text}'"
    return True, f"Hiển thị đúng lỗi mong đợi: '{text}'"

def run_all(cases_path="output/cases.json", out_path="output/results.json",
            base_url=BASE):
    cases = json.load(open(cases_path, encoding="utf-8"))
    os.makedirs("output/screenshots", exist_ok=True)
    results = []
    
    print("[2] Bắt đầu thực thi test tự động bằng Playwright...")
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        for tc in cases:
            ctx = browser.new_context()
            page = ctx.new_page()
            start = time.time()
            try:
                passed, actual = run_case(page, tc, base_url=base_url)
            except Exception as ex:
                passed, actual = False, f"Lỗi ngoại lệ khi chạy test: {ex}"
            
            shot = f"output/screenshots/{tc['id']}.png"
            page.screenshot(path=shot)
            
            results.append({
                "id": tc["id"], "title": tc["title"], "type": tc["type"],
                "passed": passed, "actual": actual,
                "duration_s": round(time.time() - start, 2), "screenshot": shot,
            })
            print(f"  [{'PASS' if passed else 'FAIL'}] {tc['id']}: {tc['title']}")
            ctx.close()
        browser.close()
        
    json.dump(results, open(out_path, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    passed_count = sum(r['passed'] for r in results)
    print(f"[2] Hoàn thành. Kết quả: {passed_count}/{len(results)} pass -> {out_path}")
    return results

if __name__ == "__main__":
    run_all()