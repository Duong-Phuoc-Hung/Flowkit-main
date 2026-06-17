import sqlite3
import os
import pytest

DB_PATH = "flow_agent.db"

def test_database_connection():
    """Kiểm tra xem hệ thống có thể kết nối với DB hay không."""
    assert os.path.exists(DB_PATH), f"Database file {DB_PATH} not found!"
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Kiểm tra bảng request có tồn tại không
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='request';")
    table = cursor.fetchone()
    assert table is not None, "Bảng 'request' không tồn tại trong Database!"
    
    conn.close()
