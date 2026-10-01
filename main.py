import argparse
from generate_cases import generate
from run_tests import run_all
from analyze import analyze_all

DEFAULT_STORY = (
    "Là người dùng, tôi có thể đăng nhập bằng username và password "
    "để xem danh sách sản phẩm."
)


def main():
    parser = argparse.ArgumentParser(description="Chạy pipeline QA AI end-to-end")
    parser.add_argument("story", nargs="?", default=DEFAULT_STORY,
                        help="User story hoặc yêu cầu cần kiểm thử")
    parser.add_argument("--url", default="https://www.saucedemo.com",
                        help="URL website cần kiểm thử")
    args = parser.parse_args()

    print("=== BẮT ĐẦU CHẠY QUY TRÌNH QA AI ===")
    generate(args.story)
    run_all(base_url=args.url)
    analyze_all()
    print("=== HOÀN TẤT TOÀN BỘ QUY TRÌNH ===")


if __name__ == "__main__":
    main()