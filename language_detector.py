from langdetect import detect


def detect_language(text: str) -> str:
    try:
        language = detect(text)
        if language == "zh-cn":
            return "Chinese"
        elif language == "en":
            return "English"
        return language
    except Exception as e:
        print(f"Error detecting language: {e}")
        return "Unknown"
