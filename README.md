🚀 ParrMotion Downloader v1.0.0 (中文版)
📂 便携式套件结构
ParrMotion 是一款完全免费的下载工具，它基于强大的开源引擎 yt-dlp 构建，支持从全球 1000 多个平台（如 YouTube 和 Bilibili）下载视频，作者旨在为这款功能强大的下载器编写直观、易于操作的UI。

本软件无需安装，下载后请确保以下文件放在同一个文件夹内：

ParrMotion.exe — 主程序。

ffmpeg.exe — 用于合并高清音视频。

ffprobe.exe — 用于解析视频信息。

ffplay.exe — （可选）用于视频验证。

🛠️ 功能特点
核心引擎：基于 yt-dlp，支持多平台下载。

多语言：支持中（简/繁）、英、日、韩语。

界面：支持深色模式，操作直观。

限速控制：支持自定义下载速度上限。

稳定性：

自动为文件添加 ID 防止重名。

实时显示视频真实分辨率。

中断时自动清理临时文件。

👨‍💻 项目信息
技术支持：yt-dlp & Google Gemini 3.1 Pro

版本：v1.0.0

联系方式：srlee717421@gmail.com

🚀 ParrMotion Downloader v1.0.0 (English Version)
📂 Portable Suite Structure
ParrMotion is a free utility powered by the yt-dlp engine, supporting video downloads from more than 1000+ platforms like YouTube and Instagram, The author aims to provide an intuitive and user-friendly UI for this powerful downloader.

No installation is required. Please ensure the following files are kept in the same folder:

ParrMotion.exe — Main application.

ffmpeg.exe — Used for merging HD video and audio.

ffprobe.exe — Used for parsing video information.

ffplay.exe — (Optional) Used for video verification.

🛠️ Features
Core Engine: Built on yt-dlp for multi-platform support.

Multi-Language: Supports EN, CN, JP, and KO.

UI: Native Dark Mode support with a simple interface.

Speed Control: Custom download speed limits.

Stability:

Unique task-IDs to prevent file overwrites.

Real-time video resolution display.

Auto-cleanup of temporary files.

👨‍💻 Project Info
Tech Support: yt-dlp & Google Gemini 3.1 Pro

Version: v1.0.0

Contact: srlee717421@gmail.com

## 维护版：YouTube 403 与 Windows 构建

旧版 `ParrMotion.exe` 内置的 yt-dlp 不会因为替换 FFmpeg 或更新系统 Python 包而更新。
维护版安装完整的 YouTube 解析依赖（EJS + Deno），优先检测程序目录中的运行时和 FFmpeg，
保留可复制的完整报错，并写入轮转日志。403 也可能来自网站登录要求、地区或 IP 限制，
更新引擎不能保证解决所有 403；请根据日志进一步判断。

### 下载新的安装包或便携程序

将此更改合入 GitHub 后，在 **Actions → Windows installer build → Run workflow** 运行构建。
推送 `maintenance/windows-*` 维护分支也会自动构建，无需修改主分支。
默认更新到构建时最新的稳定版 yt-dlp 及其匹配依赖，无需在使用者电脑安装 Python 或 Deno。
完成后下载 `ParrMotion-windows-x64` artifact。运行 `ParrMotion-Setup-windows-x64.exe`
可安装到当前用户目录，创建开始菜单快捷方式，并通过 Windows 应用列表卸载；支持 Windows 10/11 x64。
若需要便携版，解压其中的 `ParrMotion-windows-x64.zip`，
保留整个文件夹（包括 `_internal`、`deno.exe`、`ffmpeg.exe`、`ffprobe.exe`），运行新的 `ParrMotion.exe`。
不要只复制单个 EXE。手动构建可取消 `update_engine`，使用 requirements.txt 的已验证版本。
`build-versions.txt` 记录本次构建的实际依赖版本，`SHA256SUMS.txt` 记录安装包和便携 ZIP 的校验值。

### 开发与本机 Windows 打包

使用 Python 3.12：

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe main.py
```

在 Windows 安装 Inno Setup 6，将 FFmpeg 和 FFprobe 放到仓库根目录或 PATH，然后执行：

```powershell
.\.venv\Scripts\python.exe -m pip install pyinstaller==6.22.3
.\.venv\Scripts\python.exe -m unittest discover -s tests -v
.\.venv\Scripts\python.exe tools/build_windows.py
```

生成文件为 `dist/ParrMotion-Setup-windows-x64.exe` 和 `dist/ParrMotion-windows-x64.zip`。
Actions 会实际安装产物、检查捆绑运行时、启动桌面窗口并卸载。Linux 不能直接构建 Windows EXE。
维护安装包 1.0.2 补齐 Flet 的 Material/Cupertino 图标资源，修复启动后 `icons.json` 缺失的错误页。
构建会对比源码、便携 ZIP 和安装目录中的图标文件；Windows 验收通过截图 OCR 检查主界面的
下载按钮、保存位置、画质和链接输入框，并故意移走图标文件确认错误页会被拒绝。
`ParrMotion-desktop-verification` artifact 保存实际截图、OCR 文字和验收结果。
日后刷新引擎可先运行 `python -m pip install --upgrade "yt-dlp[default,deno]"`，再重新构建。

Windows 日志位于 `%LOCALAPPDATA%\ParrMotion\logs\download.log`；无法写入时退回临时目录，
具体路径会显示在错误下方。日志保留引擎版本、下载警告及错误，自动隐藏 URL 查询参数和
常见认证头；分享日志前仍应检查个人信息。不要公开 Cookies 或账号令牌。

当前验证范围：本地视频下载、MP3 转码、界面初始化和错误处理。
真实 YouTube 请求仍需在可访问 YouTube 的网络中验证，Windows 打包产物需在 Windows 验证。
