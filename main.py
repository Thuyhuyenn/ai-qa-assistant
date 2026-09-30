import sys
from generate_cases import generate
from run_tests import run_all
from analyze import analyze_all

if __name__ == "__main__":
    story = sys.argv[1] if len(sys.argv) > 1 else \
        "Là người dùng, tôi có thể đăng nhập bằng username và password để xem danh sách sản phẩm."
    
    print("=== BẮT ĐẦU CHẠY QUY TRÌNH QA AI ===")
    generate(story)
    run_all()
    analyze_all()
    print("=== HOÀN TẤT TOÀN BỘ QUY TRÌNH ===")