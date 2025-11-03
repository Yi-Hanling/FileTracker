import json
import os

class RecordManager:
    """管理文件路径记录"""

    def __init__(self, history_file="data/history.json", max_records=50):
        self.history_file = history_file
        self.max_records = max_records
        os.makedirs(os.path.dirname(self.history_file), exist_ok=True)
        if not os.path.exists(self.history_file):
            with open(self.history_file, "w", encoding="utf-8") as f:
                json.dump([], f, ensure_ascii=False, indent=4)

    def load_records(self):
        try:
            with open(self.history_file, "r", encoding="utf-8") as f:
                return json.load(f)
        except (json.JSONDecodeError, FileNotFoundError):
            return []

    def save_records(self, records):
        with open(self.history_file, "w", encoding="utf-8") as f:
            json.dump(records, f, ensure_ascii=False, indent=4)

    def add_record(self, folder_path):
        """添加新记录，重复则移到前面"""
        records = self.load_records()
        if folder_path in records:
            records.remove(folder_path)
        records.insert(0, folder_path)
        records = records[:self.max_records]
        self.save_records(records)

    def get_records(self):
        """返回所有记录"""
        return self.load_records()

    def clear_records(self):
        """清空记录"""
        self.save_records([])
