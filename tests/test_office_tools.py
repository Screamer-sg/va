import office_tools

def test_parse_formatting_from_command():
    assert office_tools.parse_formatting_from_command("жирний курсив") == {"bold": True, "italic": True}
    assert office_tools.parse_formatting_from_command("bold underline") == {"bold": True, "underline": True}
    assert office_tools.parse_formatting_from_command("без форматування") == {}

def test_append_text_to_odt(tmp_path):
    filename = tmp_path / "test.odt"
    from odf.opendocument import OpenDocumentText
    doc = OpenDocumentText()
    doc.save(str(filename))
    result = office_tools.append_text_to_odt(str(filename), "Тестовий текст", {"bold": True})
    assert "Текст додано" in result