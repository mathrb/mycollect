from mycollect.processors.file_processor import FileProcessor

def test_file_processor():
    fp = FileProcessor("tests/test_files/tweets_to_process.jsonl")
    fp.set_offset(0)
    result = fp.process()
    assert result
    assert len(result) == 6