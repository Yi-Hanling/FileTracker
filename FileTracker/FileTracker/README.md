# 🗂️ FileTracker — 文件保存路径记录器

FileTracker 是一个基于 Python 的桌面小工具，  
可以自动记录并显示用户最近保存文件的文件夹路径，  
帮助用户快速找到最近保存的文件位置。

---

## ✨ 功能特点
- 自动监控文件保存操作（通过 watchdog）
- 记录最近 20 个文件保存位置
- 图形化界面（CustomTkinter）
- 一键查看、刷新记录
- 支持打包为 EXE 独立运行

---

## 📦 环境配置

### 方法 1：使用 Conda（推荐）
```bash
conda env create -f environment.yml
conda activate filetracker
