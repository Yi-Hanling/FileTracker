from tracker.record_manager import RecordManager
# 如果想用 Tkinter 版本
from tracker.gui import FileTrackerGUI
# 如果想用 customtkinter 版本
# from tracker.gui_custom import FileTrackerGUI

if __name__ == "__main__":
    record_manager = RecordManager()
    gui = FileTrackerGUI(record_manager)
