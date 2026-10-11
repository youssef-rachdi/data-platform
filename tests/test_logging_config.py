import logging

import pytest

from data_platform.logging_config import setup_logging


@pytest.fixture(autouse=True)
def restore_root_logger():
    """Put the root logger back as it was after each test."""
    root = logging.getLogger()
    original_handlers = root.handlers[:]
    original_level = root.level
    yield
    for handler in root.handlers[:]:
        if handler not in original_handlers:
            root.removeHandler(handler)
            handler.close()
    root.handlers[:] = original_handlers
    root.setLevel(original_level)


def test_log_file_is_created_and_written(tmp_path):
    setup_logging("INFO", tmp_path)
    logging.getLogger("test").info("hello pipeline")

    log_file = tmp_path / "app.log"
    assert log_file.exists()
    assert "hello pipeline" in log_file.read_text(encoding="utf-8")


def test_calling_setup_twice_does_not_duplicate_handlers():
    setup_logging("INFO")
    setup_logging("INFO")
    assert len(logging.getLogger().handlers) == 1