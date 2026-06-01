<p align="center">
  <img src="autoenter_icon.ico" width="80" alt="AutoEnter">
</p>

<h1 align="center">AutoEnter</h1>

<p align="center">
  一个简约的 Windows 自动按键工具 · 后台运行 · 全局热键控制
</p>

<p align="center">
  <img src="https://img.shields.io/badge/platform-Windows%2010%2F11-blue?style=flat-square" alt="platform">
  <img src="https://img.shields.io/badge/license-MIT-green?style=flat-square" alt="license">
  <img src="https://img.shields.io/badge/python-3.8%2B-blue?style=flat-square" alt="python">
  <img src="https://img.shields.io/badge/dependencies-zero-brightgreen?style=flat-square" alt="dependencies">
</p>

---

## 这是什么

AutoEnter 是一个轻量级 Windows 工具，可以按照你设定的时间间隔**自动模拟按下回车键**。切换窗口后依然生效，非常适合需要频繁确认操作的场景。

**典型场景：** 在 PyCharm 中使用 AI 终端生成代码时，每次修改都需要输入 Yes 确认——开着 AutoEnter，让它帮你自动回车。

## 特性

- **可调节间隔** — 从 5 秒到任意秒数，自由设定
- **全局热键** — `Ctrl+Alt+1` 开始，`Ctrl+Alt+2` 停止，无需切回程序窗口
- **后台运行** — 最小化或切到其他窗口，按键持续生效
- **零依赖** — 仅使用 Python 标准库 + Windows API，exe 直接运行
- **暗色 UI** — 简洁的深色界面，无边框设计，可拖拽
- **单文件** — 8MB 便携 exe，无需安装

## 快速开始

从 [Releases](https://github.com/hudejintou/AutoEnter-Claude/releases) 下载 `AutoEnter.exe`，双击运行。

1. 设置回车间隔（默认 10 秒）
2. 点击 **开始** 或按 `Ctrl+Alt+1`
3. 切换到目标窗口
4. 点击 **停止** 或按 `Ctrl+Alt+2` 结束

## 快捷键

| 快捷键 | 功能 |
| ------ | ---- |
| `Ctrl + Alt + 1` | 开始运行 |
| `Ctrl + Alt + 2` | 停止运行 |

即使程序窗口在后台，快捷键依然生效。

## 从源码构建

```bash
git clone https://github.com/hudejintou/AutoEnter-Claude.git
cd AutoEnter-Claude
pip install pyinstaller
pyinstaller --onefile --windowed --name AutoEnter --icon autoenter_icon.ico auto_enter_gui.py
```

构建产物在 `dist/AutoEnter.exe`。

## 项目结构

```
├── auto_enter_gui.py       # 主程序 (GUI + 热键 + 键盘模拟)
├── generate_icon.py        # 图标生成脚本
├── autoenter_icon.ico      # 应用图标
├── .gitignore
├── LICENSE
└── README.md
```

## 常见问题

**Q: 杀毒软件报毒？**  
A: 程序使用了 `SendInput` API 模拟键盘输入，部分杀软会误报。所有源码公开，可自行审查。

**Q: 能不能设置间隔小于 1 秒？**  
A: 可以，但不建议——太快可能让目标程序来不及响应。

## License

MIT © [hudejintou](https://github.com/hudejintou)
