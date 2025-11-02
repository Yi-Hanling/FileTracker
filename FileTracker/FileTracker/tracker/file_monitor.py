import os
import time
import psutil
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler


# 🚫 忽略的目录（系统目录、微信缓存、临时文件等）
EXCLUDE_DIRS = [
    "C:\\Windows", "C:\\Program Files", "C:\\Program Files (x86)",
    "C:\\ProgramData", "C:\\Users\\Public",
    "C:\\Users\\Default", "C:\\Users\\All Users",
    "C:\\$Recycle.Bin", "C:\\Recovery", "C:\\PerfLogs",
    "C:\\Users\\17295\\Documents\\WeChat Files",
    "AppData", "Temp", "cache", "__pycache__"
]


def is_excluded(path: str) -> bool:
    """判断路径是否应被排除"""
    path = path.lower()
    return any(ex.lower() in path for ex in EXCLUDE_DIRS)


class FileEventHandler(FileSystemEventHandler):
    """文件系统事件处理类"""

    def __init__(self, record_manager):
        super().__init__()
        self.record_manager = record_manager

    def on_created(self, event):
        if not event.is_directory:
            folder_path = os.path.dirname(event.src_path)
            if not is_excluded(folder_path):
                print(f"🟢 检测到新文件：{event.src_path}")
                self.record_manager.add_record(folder_path)



class FileMonitor:
    """文件监控器"""

    def __init__(self, monitor_dirs, record_manager):
        self.monitor_dirs = monitor_dirs
        self.record_manager = record_manager
        self.observer = Observer()

    def start(self):
        """开始监控"""
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
        """停止监控"""
        if self.observer.is_alive():
            self.observer.stop()
            self.observer.join(timeout=3)
            print("🛑 文件监控已停止。")


def get_default_monitor_dirs():
    """自动检测所有盘符并过滤系统盘常见路径"""
    monitor_dirs = []
    partitions = psutil.disk_partitions(all=False)

    for p in partitions:
        drive = p.device  # 如 "C:\\"
        # 跳过无效驱动器或特殊盘
        if "cdrom" in p.opts or "removable" in p.opts.lower():
            continue
        # 仅添加存在的路径
        if os.path.exists(drive):
            monitor_dirs.append(drive)

    return monitor_dirs
