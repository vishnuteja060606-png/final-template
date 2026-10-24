from app.services.file_service import file_service

def test_sanitize_filename_removes_traversal():
    assert ".." not in file_service.sanitize_filename("../../../etc/passwd")
    assert ".." not in file_service.sanitize_filename("..\\..\\windows\\system32")

def test_sanitize_filename_cleans_characters():
    clean = file_service.sanitize_filename("my crazy file #1 (v2) [final].mp4")
    assert clean == "my_crazy_file__1__v2___final_.mp4"

def test_get_extension():
    assert file_service.get_extension("video.mp4") == "mp4"
    assert file_service.get_extension("IMAGE.PNG") == "png"
    assert file_service.get_extension("no_ext") == ""
