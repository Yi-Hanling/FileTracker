import os
from tracker.gui import FileTrackerGUI
from tracker.file_monitor import get_default_monitor_dirs

if __name__ == "__main__":
    # 自动扫描磁盘，选择要监控的盘符（避开系统盘敏感目录）
    monitor_dirs = get_default_monitor_dirs()

    print("✅ 将监控以下目录：")
    for d in monitor_dirs:
        print("  ", d)

    # 启动图形界面
    app = FileTrackerGUI(monitor_dirs=monitor_dirs)
