📂 便携式套件结构（重要说明）
ParrMotion 是一款无需安装的便携式工具。为确保高清视频处理及播放验证功能正常，请务必将以下组件保存在同一个文件夹内：

ParrMotion.exe — 主用户界面与逻辑控制程序。

ffmpeg.exe — （核心） 用于合并高清视频流与音频流的关键引擎。

ffprobe.exe — （核心） 用于检测媒体元数据及分辨率的分析工具。

ffplay.exe — （可选） 用于技术性流媒体验证的轻量级播放器。

注意：虽然 ffplay.exe 对于核心的下载/合并过程并非强制要求，但将这四个文件放在一起，可确保与 yt-dlp 后端所有功能的最高兼容性。

🚀 ParrMotion 下载器 v1.0.0
ParrMotion 是一款极简、高效的网络媒体获取工具。它专为速度与稳定性而生，为您提供从全球数千个平台下载高保真视频和音频的无缝体验。

💎 卓越工程
核心引擎：基于行业标准的 yt-dlp 框架，确保对全球视频网站的深度兼容与持续更新。

AI 驱动架构：本软件通过与 Google Gemini 3.1 Pro 进行深度的工程协作完成架构设计与优化。代码库强调稳定性、跨平台 UI 的一致性以及高效的资源管理。

✨ 核心功能
🌍 多语言本地化：支持简体中文、繁體中文、英语、日语和韩语的智能自动检测及手动切换。

🎨 适配 UI 界面：全集成的深色模式 (Dark Mode) 支持，在任何环境下都能提供沉浸式、护眼的体验。

⚡ 精准速度限制：先进的带宽管理功能，允许用户设置明确的下载限速 (MB/s)，或留空以实现不受限的极速下载。

🛡️ 健壮性特性：

冲突防止：采用独特的 4 位任务 ID 算法，防止在并发或重复下载时发生文件覆盖。

分辨率反馈：在解析阶段实时识别并显示视频的真实分辨率（如 4K、1080p）。

自动清理：内置垃圾回收逻辑，在任务中断时自动清除 .part 或 .ytdl 等临时文件。

🛠️ 运行与部署
ParrMotion 采用便携式“绿色”软件设计，无需安装。

主程序：ParrMotion.exe

必备二进制文件：ffmpeg.exe 和 ffprobe.exe 必须与主程序置于同一目录下，以实现高清媒体的合并与分析。

👨‍💻 开发信息
核心驱动：Powered by yt-dlp

协作 AI：Google Gemini 3.1 Pro

版本：v1.0.0 (Stable)

联系方式：srlee717421@gmail.com

📂 Portable Suite Structure (Important)
ParrMotion is a portable, no-installation utility. To ensure high-definition video processing and playback verification, the following components should be kept in the same folder:

ParrMotion.exe — The primary user interface and logic controller.

ffmpeg.exe — (Essential) The core engine used for merging high-quality video and audio streams.

ffprobe.exe — (Essential) The analysis tool used to detect media metadata and resolutions.

ffplay.exe — (Optional) A lightweight media player used by the engine for technical stream verification.

Note: While ffplay.exe is not strictly required for the core download/merge process, keeping all four files together ensures maximum compatibility with all yt-dlp backend features.

🚀 ParrMotion Downloader v1.0.0
ParrMotion is a minimalist, high-performance web media acquisition utility. Built for speed and reliability, it provides a seamless interface for downloading high-fidelity video and audio from thousands of platforms globally.

💎 Engineering Excellence
Core Engine: Powered by the industry-standard yt-dlp framework, ensuring deep compatibility and constant updates for global media sites.

AI-Driven Architecture: This software was architected and refined through intensive engineering collaboration with Google Gemini 3.1 Pro. The codebase emphasizes stability, cross-platform UI consistency, and efficient resource management.

✨ Key Capabilities
🌍 Multi-Regional Localization: Intelligent auto-detection and manual switching for English, Simplified Chinese, Traditional Chinese, Japanese, and Korean.

🎨 Adaptive UI Interface: Fully integrated Dark Mode support for an immersive, eye-friendly user experience in any environment.

⚡ Precision Rate Limiting: Advanced bandwidth management allowing users to set explicit speed caps (MB/s) or leave blank for unrestricted throughput.

🛡️ Robustness Features:

Collision Prevention: Implements a unique 4-character task-ID algorithm to prevent file overwrites during concurrent or repeated downloads.

Resolution Feedback: Real-time identification and display of the actual video resolution (e.g., 4K, 1080p) during the extraction phase.

Automated Cleanup: Built-in garbage collection logic that automatically purges temporary .part or .ytdl files if a process is interrupted.

🛠️ Execution & Deployment
ParrMotion is designed as a portable, "green" software suite requiring no installation.

Main Executable: ParrMotion.exe

Required Binaries: Both ffmpeg.exe and ffprobe.exe must be placed in the same directory as the main executable to enable high-definition media merging and analysis.

👨‍💻 Development Information
Powered by yt-dlp

Consulting AI: Google Gemini 3.1 Pro

Version: v1.0.0 (Stable)

Contact: srlee717421@gmail.com
