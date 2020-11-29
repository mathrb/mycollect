from mycollect.processors.file_processor import FileProcessor
from mycollect.data_manager.file_data_manager import FileDataManager

def test_file_processor():
    fdm = FileDataManager("tests/test_files")
    fp = FileProcessor(fdm)
    fp.set_offset(0)
    result = fp.process()
    assert result
    assert len(result) == 4