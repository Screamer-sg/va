import gemini_tools

def test_detect_language_uk():
    # Може не працювати без справжнього ключа Gemini!
    lang = gemini_tools.gemini_detect_language("Привіт, як справи?")
    assert lang.startswith("uk") or lang == "uk"