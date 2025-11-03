import threading
import os
import tkinter as tk
import customtkinter as ctk
from tkinter import messagebox
from .file_monitor import FileMonitor
from .record_manager import RecordManager

class FileTrackerGUI:
    """文件监控图形界面（customtkinter）"""

    def __init__(self, record_manager=None, monitor_dirs=None):
        # 如果没有传入 RecordManager，则创建一个
        self.record_manager = record_manager if record_manager else RecordManager()
        self.monitor_dirs = monitor_dirs
        self.monitor = None

        self.window = ctk.CTk()
        self.window.title("文件保存位置追踪器")
        self.window.geometry("650x420")

        ctk.set_appearance_mode("System")
        ctk.set_default_color_theme("blue")

        self.create_widgets()
        self.start_monitoring_thread()

        # 绑定窗口关闭事件
        self.window.protocol("WM_DELETE_WINDOW", self.on_close)

        self.window.mainloop()

    def create_widgets(self):
        """创建 GUI 元素"""
        label = ctk.CTkLabel(self.window, text="📁 最近保存的文件夹路径：", font=("Microsoft YaHei", 16))
        label.pack(pady=10)

        self.listbox = tk.Listbox(self.window, height=10, font=("Consolas", 12))
        self.listbox.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)

        btn_frame = ctk.CTkFrame(self.window)
        btn_frame.pack(pady=10)

        refresh_btn = ctk.CTkButton(btn_frame, text="🔄 刷新", command=self.refresh)
        refresh_btn.grid(row=0, column=0, padx=10)

        copy_btn = ctk.CTkButton(btn_frame, text="📋 复制选中路径", command=self.copy_selected)
        copy_btn.grid(row=0, column=1, padx=10)

        clear_btn = ctk.CTkButton(btn_frame, text="🧹 清空记录", command=self.clear_history)
        clear_btn.grid(row=0, column=2, padx=10)

        self.refresh()

    def refresh(self):
        """刷新列表显示"""
        self.listbox.delete(0, tk.END)
        records = self.record_manager.get_records()
        if not records:
            self.listbox.insert(tk.END, "（暂无记录）")
        else:
            for folder in records:
                self.listbox.insert(tk.END, folder)

    def copy_selected(self):
        """复制选中的路径"""
        try:
            selection = self.listbox.get(self.listbox.curselection())
            self.window.clipboard_clear()
            self.window.clipboard_append(selection)
            messagebox.showinfo("已复制", f"已复制路径：\n{selection}")
        except Exception:
            messagebox.showwarning("提示", "请先选择一个路径！")

    def clear_history(self):
        """清空历史记录"""
        confirm = messagebox.askyesno("确认", "确定要清空所有记录吗？")
        if confirm:
            self.record_manager.clear_records()
            self.refresh()

    def start_monitoring_thread(self):
        """启动后台监控线程"""
        if not self.monitor_dirs:
            from .file_monitor import get_default_monitor_dirs
            self.monitor_dirs = get_default_monitor_dirs()
        self.monitor = FileMonitor(self.monitor_dirs, self.record_manager)
        thread = threading.Thread(target=self.monitor.start, daemon=True)
        thread.start()

    def on_close(self):
        """安全关闭程序"""
        if messagebox.askokcancel("退出", "确定要退出程序吗？"):
            if self.monitor:
                print("🛑 正在停止监控线程...")
                self.monitor.stop()
            self.window.destroy()
            print("✅ 程序已安全退出。")
