import os, re, json, time, random
from google import genai
from google.genai import types
from google.genai.errors import ServerError, ClientError

api_key = os.getenv("GEMINI_API_KEY")
if not api_key:
    raise ValueError("Chưa tìm thấy GEMINI_API_KEY!")

client = genai.Client(api_key=api_key)

# Thử lần lượt từng model; model đầu tiên được ưu tiên
MODELS = ["gemini-3.8-flash", "gemini-3.7-flash", "gemini-3.5-flash-lite"]
MAX_RETRIES = 4


def parse_json(text: str):
    """Parse JSON, tự bỏ ```json ... ``` và phần thừa quanh JSON."""
    text = re.sub(r"^```(?:json)?|```$", "", (text or "").strip(), flags=re.M).strip()
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        starts = [i for i in (text.find("["), text.find("{")) if i != -1]
        if not starts:
            raise
        start = min(starts)
        end = max(text.rfind("]"), text.rfind("}"))
        return json.loads(text[start:end + 1])


def _call(prompt: str, json_mode: bool):
    config = types.GenerateContentConfig(
        response_mime_type="application/json" if json_mode else None,
        temperature=0.3,
        max_output_tokens=32000,
    )
    last_error = None
    for model in MODELS:
        for attempt in range(MAX_RETRIES):
            try:
                resp = client.models.generate_content(
                    model=model, contents=prompt, config=config
                )
                if not json_mode:
                    return resp.text
                return parse_json(resp.text)
            except json.JSONDecodeError as e:  # JSON bị lỗi/cắt cụt -> gọi lại
                last_error = e
                print(f"  [Cảnh báo] {model} trả JSON lỗi ({e}), gọi lại {attempt + 1}/{MAX_RETRIES}...")
                time.sleep(2)
            except ServerError as e:  # 500/503: server quá tải
                last_error = e
                wait = min(2 ** attempt * 3, 30) + random.uniform(0, 2)
                print(f"  [Cảnh báo] {model} quá tải (503), thử lại {attempt + 1}/{MAX_RETRIES} sau {wait:.0f}s...")
                time.sleep(wait)
            except ClientError as e:
                if e.code == 429:
                    last_error = e
                    print(f"  [Cảnh báo] {model} bị giới hạn (429), đợi 10s...")
                    time.sleep(10)
                elif e.code == 404:
                    print(f"  [Cảnh báo] Model {model} không khả dụng, đổi model khác...")
                    last_error = e
                    break
                else:
                    raise
        print("  [Cảnh báo] Chuyển sang model dự phòng...")
    raise last_error


def call_gemini(prompt: str) -> str:
    """Trả về text thuần."""
    return _call(prompt, json_mode=False)


def call_gemini_json(prompt: str):
    """Trả về object Python (list/dict) đã parse; tự thử lại nếu JSON lỗi."""
    return _call(prompt, json_mode=True)