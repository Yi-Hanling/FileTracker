import os
import time
import psutil
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import json

# ================================
# 自动生成黑名单目录
# ================================
def get_exclude_dirs():
    """
    自动生成黑名单目录
    包括系统目录、临时目录、隐藏文件夹、安装程序缓存等
    """
    user_home = os.path.expanduser("~")  # 当前用户主目录

    exclude_dirs = [
        # 系统目录
        "C:\\Windows",
        "C:\\Program Files",
        "C:\\Program Files (x86)",
        "C:\\ProgramData",
        "C:\\$Recycle.Bin",
        "C:\\Recovery",
        "C:\\PerfLogs",
        "C:\\System Volume Information",
        "C:\\Config.Msi",

        # 公共用户目录
        os.path.join("C:\\Users", "Default"),
        os.path.join("C:\\Users", "Public"),
        os.path.join("C:\\Users", "All Users"),

        # 用户目录下系统隐藏文件夹
        os.path.join(user_home, "AppData"),
        os.path.join(user_home, "Local"),
        os.path.join(user_home, "LocalLow"),
        os.path.join(user_home, "Roaming"),
        os.path.join(user_home, "Temp"),
        os.path.join(user_home, "cache"),
        os.path.join(user_home, "__pycache__"),

        # 特定应用目录
        "WindowsApps",     # Microsoft Store
        "Microsoft",       # Office / Edge / OneDrive 等
        "OneDrive",        # OneDrive 同步文件
        "WeChat Files\\Cache",
        "WeChat Files\\Temp",
        # "Steam",         # 如果需要监控 Steam 游戏库，可注释掉
    ]

    return exclude_dirs


EXCLUDE_DIRS = get_exclude_dirs()

def is_excluded(path: str) -> bool:
    """判断路径是否应被排除"""
    path = path.lower()
    return any(ex.lower() in path for ex in EXCLUDE_DIRS)


# ================================
# 文件记录管理器
# ================================
class RecordManager:
    """管理文件保存路径记录"""
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
        records = self.load_records()
        if folder_path in records:
            records.remove(folder_path)
        records.insert(0, folder_path)
        records = records[:self.max_records]
        self.save_records(records)

    def get_records(self):
        return self.load_records()

    def clear_records(self):
        self.save_records([])


# ================================
# 文件监控处理类
# ================================
class FileEventHandler(FileSystemEventHandler):
    """处理文件创建事件"""
    def __init__(self, record_manager):
        super().__init__()
        self.record_manager = record_manager

    def on_created(self, event):
        if not event.is_directory:
            folder_path = os.path.dirname(event.src_path)
            if not is_excluded(folder_path):
                print(f"🟢 检测到新文件：{event.src_path}")
                self.record_manager.add_record(folder_path)


# ================================
# 文件监控器
# ================================
class FileMonitor:
    def __init__(self, monitor_dirs, record_manager):
        self.monitor_dirs = monitor_dirs
        self.record_manager = record_manager
        self.observer = Observer()

    def start(self):
        event_handler = FileEventHandler(self.record_manager)
        for directory in self.monitor_dirs:
            if os.path.exists(directory):
                try:
                    print(f"📂 开始监控目录：{directory}")
                    self.observer.schedule(event_handler, directory, recursive=True)
                except Exception as e:
                    print(f"⚠️ 无法监控目录 {directory}：{e}")
        self.observer.start()

        try:
            while self.observer.is_alive():
                time.sleep(1)
        except KeyboardInterrupt:
            self.stop()

    def stop(self):
        if self.observer.is_alive():
            self.observer.stop()
            self.observer.join(timeout=3)
            print("🛑 文件监控已停止。")


# ================================
# 自动获取监控盘符
# ================================
def get_default_monitor_dirs():
    """监控所有盘符，但排除系统光驱和移动设备"""
    monitor_dirs = []
    partitions = psutil.disk_partitions(all=False)
    for p in partitions:
        drive = p.device
        if "cdrom" in p.opts or "removable" in p.opts.lower():
            continue
        if os.path.exists(drive):
            monitor_dirs.append(drive)
    return monitor_dirs


# ================================
# 启动示例
# ================================
if __name__ == "__main__":
    record_manager = RecordManager()
    monitor_dirs = get_default_monitor_dirs()
    print("✅ 正在监控以下盘符：", monitor_dirs)
    monitor = FileMonitor(monitor_dirs, record_manager)
    monitor.start()
