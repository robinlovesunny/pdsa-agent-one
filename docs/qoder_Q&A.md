# 问题排查指南

本文介绍如何使用 Qoder 诊断脚本排查 Qoder 的启动与连接问题。该脚本会自动收集关键系统信息，包括环境信息、网络配置、Qoder 服务状态及相关日志，帮助快速定位并解决常见问题。

## 先决条件

在运行诊断脚本之前，请确认以下事项：

- 操作系统：Windows
- 权限：以管理员权限运行脚本，以便完整访问系统设置和日志。
- 脚本文件：下载并将 windows_Qoder.bat 保存为 .bat 文件（例如：qoder_Debug.bat）。
- 安装路径：确认 Qoder 安装在默认目录 C:\Users\<YourUsername>\.qoder。

## 运行诊断脚本

### 步骤 1：运行脚本

1. 找到已保存的 .bat 文件。
   - 示例：qoder_Debug.bat
2. 双击该文件以执行脚本。
3. 脚本将自动运行，收集系统和应用程序数据。
4. ⚠️ 请等待脚本完全执行完成。不要提前关闭命令窗口。

### 步骤 2：查看生成的日志

脚本执行完成后：

- 系统会自动生成一个包含所收集日志文件和关键配置文件的 ZIP 压缩包。
  - 文件名格式：qoder-diagnosis_YYYYMMDD_HHMMSS.zip
  - 示例：qoder-diagnosis_Sat_2025-10-11_16-00-03.93.zip
- 主要日志文件已包含在压缩包中，命名格式：Qoder_Log_YYYYMMDD_HHMMSS.txt
  - 示例：Qoder_Log_20250405_143022.txt
- 你可以将整个诊断 ZIP 包发送给 Qoder 官方团队，以便协助问题定位与排障。

## 常见问题

| 问题类型 | 问题 | 解决方案 |
|---------|------|----------|
| 网络 | 检查代理设置 | 脚本会检查是否启用了代理。请查看 [Network Settings 0x0 means proxy is disabled] 部分以确认预期行为。如在使用代理，请在设置中为 Qoder 手动配置网络代理。 |
| Qoder 服务器状态 | Qoder.exe 是否存在 | 脚本会检查 Qoder.exe 是否存在。如出现错误：1. 检查安装路径。2. 删除 .qoder 目录。3. 重启 IDE 以重新生成该目录。 |
| 版本与启动测试 | 查看 [Version Test] 和 [Start Qoder] 部分以确认：* Qoder 版本 * 与公共服务器的连接情况 | 若显示"failed"，请使用错误信息中的 URL 在设置中配置代理访问。 |
| Qoder.exe 运行但登录失败 | 将可执行文件加入 Windows 防火墙白名单： | 路径：1. Windows：C:\Users\用户名\AppData\Local\Programs\Qoder\resources\app\resources\bin`CPU_architecture_64_system\Qoder.exe<br/>2. Mac：/Applications/Qoder.app/Contents/Resources/app/resources\bin\CPU_architecture_64_system`\Qoder 步骤：控制面板 → 系统和安全 → Windows Defender 防火墙 → 允许的应用 → 允许其他应用 然后重试登录。 |
| 系统兼容性 | 系统与硬件信息 | 脚本会收集：* 操作系统版本（如 Windows 10/11）* CPU 型号 查看 [Operating System Information] 以确认系统满足 Qoder 的要求：* Windows 10 或更高版本（64 位）* x86_64 兼容 CPU |
| 日志分析 | Qoder 应用日志 | 生成的日志包含 qoder.log 的最后 80 行。可用于定位运行时错误、警告或连接问题。 |
| 目录结构与文件大小 | 脚本会列出 .qoder 下的完整目录结构和文件大小。可用于： | * 检查磁盘占用 * 验证文件完整性（例如缺失或异常小的文件） |
| 注意 | 二进制执行限制 | 某些企业环境会限制或阻止可执行文件运行，这可能导致 Qoder 无法启动。如果应用无法启动，请联系 IT 部门以调整权限。 |
| 无法自行解决的问题 | 超出自助排障范围的问题 | 如仍无法解决，请联系： contact@qoder.com。请附上生成的日志文件：Qoder_Log_YYYYMMDD_HHMMSS.txt，以便更快获得支持。 |

# 支持

## FAQ

本常见问题解答覆盖与 Qoder 相关的常见疑问，包括安装、登录、支持的平台、语言兼容性、数据安全、计费、网络问题与故障排查。

如果遇到问题，请先尝试重启 Qoder。若仍未解决，请通过 contact@qoder.com 联系我们，我们的支持团队将尽快协助你。

## 快速入门

### 如果 Qoder 一直停在"Qoder starting"，我该怎么办？

请尝试以下步骤：

1. 检查你的环境。
   - a. 确保 Qoder 已更新到最新版本。
   - b. 确认你的操作系统和系统架构支持 Qoder。
2. 测试网络连接。
   - a. 在终端运行以下命令以检查连通性。如果收到 pong，表示网络已连接。否则，请检查防火墙，或请你的 IT 管理员将以下域名加入白名单。
     ```bash
     curl https://{hosts}/algo/api/v1/ping 
     ```
     // 您可以将 {hosts} 替换为以下任一选项：
     1. api1.qoder.sh
     2. api2.qoder.sh
     3. api3.qoder.sh
   - b. 如需使用代理，请按以下格式设置代理地址：
     ```bash
     http(s)://用户名:密码@代理服务器地址:端口
     ```
   - c. 清理 DNS 缓存：
     - Windows：ipconfig /flushdns。
     - macOS：sudo killall -HUP mDNSResponder。
3. 清理本地缓存。
   - a. 结束 Qoder 进程。
   - b. 删除 .Qoder 目录：
     - Windows：
       ```
       C:\Users\[username]\.Qoder
       C:\Users\Username\AppData\Local\Programs\Qoder\
       ```
     - macOS: 
       ```
       /Applications/Qoder.app
       ```
   - c. 重启 Qoder。
4. 如果问题仍然存在，手动启动：
   - a. 前往目录：.Qoder/bin/x.x.x/CPU_architecture_64_system/
     - Windows：
       ```
       C:\Users\Username\AppData\Local\Programs\Qoder\resources\app\resources\bin$version`CPU_architecture_64_system`\Qoder.exe
       ```
     - Mac：
       ```
       /Applications/Qoder.app/Contents/Resources/app/resources\bin$versionCPU_ahicture_64_system\Qoder 
       ```
   - b. 运行：
     ```bash
     Qoder.exe start 或 Qoder start
     ```
   - c. 再次尝试登录。
5. （可选）排查安全相关问题
   - a. 如果你看到"不兼容的程序"消息或 Qoder 无法启动：
     - i. 点击右下角的 Qoder 图标，选择高级设置。
     - ii. 将解压路径移动到非 C 盘的文件夹（公司可能限制对 C 盘的读写权限），并确保该路径以一个空文件夹结尾。
     - iii. 重启 Qoder。
   - b. 将 Qoder 添加到防火墙/安全软件的允许列表：
     - i. 控制面板 > 系统和安全 > Windows Defender 防火墙 > 允许的应用。
     - ii. 公司安全软件也可能要求你放行：
       - Windows：
         ```
         C:\Users\Username\AppData\Local\Programs\Qoder\resources\app\resources\bin\$version\CPU_architecture_64_system\Qoder.exe
         C:\Users\Username\.qoder\bin\qoder.exe
         ```
       - Mac：
         ```
         /Applications/Qoder.app/Contents/Resources/app/resources\bin\$version\CPU_architecture_64_system\Qoder
         ```

## 登录和权限

### 如果登录失败或看到权限被拒绝错误怎么办？

- 过期的登录会话需要您重新尝试。
- 确保您的网络允许访问下面列出的域名，并配置代理（如果需要）。详情请参阅 [配置网络代理](https://docs.qoder.com/user-guide/configure-network-proxy)。

```
api1.qoder.sh
api2.qoder.sh
api3.qoder.sh
```

更改设置后，请完全退出 Qoder 并重新启动。

## 代理与连接

Qoder 支持 HTTP、HTTPS 和 SOCKS5 代理。请在 Qoder 的设置中进行配置。更多详情参见配置网络代理。

要测试连接，请运行：

```bash
curl https://{hosts}/algo/api/v1/ping 
```

//您可以将 {hosts} 替换为以下任一选项：
1. api1.qoder.sh
2. api2.qoder.sh
3. api3.qoder.sh

如果返回 pong，说明你的网络已连接到 Qoder 服务器。

## 帐户管理

### 我的账户被暂停了。如何重新激活？

如果你的账户因创建过多免费试用账户而被暂停，你可以按照以下步骤重新激活：

1. 登录 Qoder 官网，点击右上角头像，进入 Settings > Usage。
2. 在 Usage 页面顶部找到暂停通知横幅，点击 Reactivate Account。
3. 确认政策提示： 为防止滥用，我们的政策仅允许你的首个账户享受免费 Pro 试用。重新激活将放弃此账户剩余的 Credits（将被清零）。确认后，此账户将自动重新激活并恢复正常使用。

### 如何计费？

Qoder 提供灵活的定价以满足多样化需求。新用户可享受为期 2 周的 Pro 试用，期间可完整使用所有 Pro 专属功能。

试用结束后，您有以下选项：

- 升级至 Pro 方案，$20/月
- 升级至 Pro+ 方案，$60/月，获得更高的 Credits 配额
- 不进行任何操作，将自动降级至我们的免费方案

在 Qoder 中的使用以 Credits 计量。每个付费方案都包含特定数量的 Credits ，便于您选择最符合需求的方案。了解更多详情，请访问我们的 Pricing 页面。

请注意，除非另有说明，所有显示的价格均不含适用税费（如增值税或销售税）。最终税额取决于多种因素，包括但不限于您的账单地址或税务登记号。

为确保所有用户都能获得公平的试用体验，Pro 试用每位用户仅限一个账户。任何额外创建的试用账户将被停用。

### 专业版试用如何运作？

当新用户首次登录 Qoder IDE（需使用最新版本；不支持在虚拟机上运行）时，将获得一次性的免费 2 周（14 天）专业版试用。试用包含 300 Credits 以及对专业版专属功能的完整访问权限。试用到期后，你的账户将自动降级为免费方案，任何未使用的试用 Credits 将被清空。

如果你在试用结束前升级为付费方案，剩余的试用 Credits 将自动转换为一个 Credit Pack，并以原有的到期日期保留在你的账户中。这样可确保你不会因提前升级而损失未使用的 Credits 。

为确保公平的试用体验，每位用户的专业版试用仅限一个账户。任何额外创建的试用账户将被停用。

### 试用期结束后会怎样？

当试用期结束时，你有以下选择：

- 升级到付费方案：选择最符合你需求的订阅，解锁更多资源。
- 切换到免费方案：你随时可以使用我们的免费方案，适合轻量使用场景。

### 试用期间如果我的 Credits 用完了会怎样？

你可以随时升级到 Pro 或 Pro+ 方案以获取更多 Credits 。如果你选择继续使用 Free 方案，也不用担心——我们会让你在基础模型上继续使用，但会有每日限额。

当使用基础模型时，将会有以下变化：

- 你将切换到基础模型：你仍可继续使用我们的服务，但会有每日使用限额。
- 性能可能会有所变化：基础模型在处理复杂任务时不如更高阶的模型强大。
- 你可能会注意到 Agent 模式和 Quest 模式等功能的性能差异，尤其是在图像对话质量和整体效果方面。

## 支持的平台

- macOS：11.0 及更高版本
- Windows：10/11

## 支持的编程语言

Qoder 支持所有主流语言，并在以下语言上提供增强体验：
JavaScript、TypeScript、Python、Go、C/C++、C# 和 Java

## 数据安全

### Qoder 会存储我的代码吗？

Qoder 不会存储或分享你的代码。在代码补全过程中会用到你的代码上下文，但这些内容不会被存储，也不会用于其他用途。

仅当你明确提交反馈（例如点赞/点踩）时，聊天记录（不包含实际代码）才可能被匿名化，用于算法改进。

详情参见 隐私政策。

### 我的代码片段会与其他用户共享吗？

不会。系统不会将你的代码片段与其他用户共享。在使用大语言模型进行代码补全时，我们需要获取你的代码信息来完成补全，但这些上下文信息不会被存储，也不会用于任何其他用途。

### 我可以直接使用 Qoder 生成的代码吗？

Qoder 生成的代码仅作参考，无法保证其可用性。开发者应自行审查并决定是否采用。

## 疑难排查与常见问题

### 如果我在 Quest Mode 和 Repo Wiki 中遇到"System Error"，该怎么办？

请更新至 Qoder v0.2.1 或更高版本。旧版本不支持这些功能。

### CPU 或内存占用过高

大型项目在进行代码索引时可能会占用大量资源。

将不需要索引的文件模式或目录添加到项目根目录的 .qoderignore（类似于 .gitignore）。

编辑 .qoderignore 后，请重启 Qoder。

### Qoder 扩展宿主崩溃

错误："extension host terminated unexpectedly 3 times within the last 5 minutes"

可能由内存泄漏引起。

1. 使用 extension bisect 确认是否由 Qoder 导致问题。
2. 尝试重新安装 Qoder 并重启。
3. 在 Windows 上，确保安全软件未拦截或阻止 Qoder。

如果问题仍然存在，请发送邮件至 contact@qoder.com。

- 操作系统及 Qoder 版本
- 复现步骤
- Qoder 详细日志（运行 qoder --verbose）
- 如需崩溃转储：运行 qoder --crash-reporter-directory <directory>，复现错误，并将生成的 .dmp 文件发送给我们。

## 支持

如需更多帮助，请通过 contact@qoder.com 与我们联系。

# 支持

## MCP 常见问题

本指南帮助你在安装和运行 Model Context Protocol（MCP）服务时诊断并解决常见问题，包括缺少依赖环境、服务初始化失败以及配置错误。

### 无法添加或安装 MCP（Model Context Protocol）服务

#### 问题：缺少 NPX 运行环境

**错误消息**
```
failed to start command: exec: "npx": executable file not found in $PATH
```

**原因**
npx 命令行工具（属于 Node.js 生态）未安装，或未在系统的 PATH 中可用。

**解决方案**
安装 Node.js V18 或更高版本（内含 NPM V8 及以上）。较早版本可能导致工具运行失败。

**安装步骤**

*Windows*
1. 安装 nvm-windows 以管理多个版本：
   ```bash
   nvm install 22.14.0  # 安装指定版本。
   nvm use 22.14.0
   ```
2. 验证是否已成功安装。
   ```bash
   node -v
   npx -v
   ```
   然后，终端会显示已安装的 Node.js 版本号。

*macOS*
1. 使用 Homebrew（如需请先安装）。
   ```bash
    # 1. 更新 Homebrew 并安装 Node.js
   brew update
   brew install node

       # 2. 验证安装并确认版本
   echo "Node.js version: $(node -v)"
   echo "npm version: $(npm -v)"
   echo "npx version: $(npx -v)"

   # 3. 配置环境变量（如需要）
   echo 'export PATH="/usr/local/opt/node@16/bin:$PATH"' >> ~/.zshrc
   ```

#### 问题：缺少 UVX 环境

**错误消息**
```
failed to start command: exec: "uvx": executable file not found in $PATH
```

**原因**
用于借助 uv 在隔离环境中运行 Python 脚本的 uvx 命令尚未安装。

**解决方案**
安装 uv，一款快速的 Python 包安装工具与虚拟环境管理器。

**安装步骤**

*Windows*
```bash
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
```

*macOS 与 Linux*
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

验证安装是否成功。
```bash
uv --version
```
然后，终端会显示已安装的 uv 的版本号。

#### 问题：无法初始化 MCP（Model Context Protocol）客户端

**错误信息**
```
failed to initialize MCP client: context deadline exceeded
```

**可能原因**

- MCP（Model Context Protocol）服务参数配置不正确
- 网络问题导致资源无法下载
- 企业网络安全策略阻止初始化

**解决方案**

1. 在 UI 中点击复制完整命令。
2. 在终端运行该命令以获取更详细的错误输出。5eecdaf48460cde54c3c3804ffe8bf87ad3cbe07b57fd6f075b8339e1c4c24831b75b38faadcd24bec177c308ebd53044ba5cb417a050fa713573df52e9556d73089d0c5ebddcce6fb457c16604993997e5e3b8f420e29e64fb4c8ed7016461c Pn
3. 根据具体错误进行分析与处理。

**常见问题 1：配置错误**

错误可能表示配置无效，例如 Redis 连接 URL 不正确。

修复：在 MCP 服务器设置中检查并纠正配置。

**常见问题 2：Node.js 被安全软件拦截**

企业级安全工具可能会阻止 Node.js 的运行。

修复：在安全软件中将 Node.js 或相关进程加入白名单。

### 工具使用相关问题

#### 问题：因环境或参数错误导致工具执行失败

**症状**

调用 MCP（Model Context Protocol）工具时出现异常行为或报错。

**原因**

某些 MCP 服务器（如 MasterGo、Figma）在设置时需要在参数中手动配置 API_KEY 或 TOKEN。

**解决方案**

1. 在 Qoder IDE 左上角，点击用户图标，或使用键盘快捷键（⌘ ⇧ ,（macOS）或 Ctrl Shift ,（Windows）），然后选择 Qoder 设置。
2. 在左侧导航栏，点击 MCP。
3. 找到相关服务器并点击 Edit。
4. 在 Edit MCP Server 页面，检查 Arguments 中的参数。
5. 将其替换为正确的值，重新连接服务器并重试。

#### 问题：LLM 无法调用 MCP 工具

**原因 1： 未处于 Agent mode**

如果未打开任何项目目录，Qoder 会默认进入 Ask 模式，而该模式不支持调用 MCP 工具。

**解决方案：** 打开项目目录并切换到 Agent mode。

**原因 2： MCP 服务器未连接**

服务器断开连接会阻止调用工具。

**解决方案：** 在界面中点击 Retry 图标。系统会尝试自动重启 MCP 服务器。

**最佳实践：** 避免为 MCP 服务器及其工具使用过于相似的名称（例如 TextAnalyzer-Pro 和 TextAnalyzer-Plus 都包含一个 fetchText 工具），以避免调用时产生歧义。

#### 问题：MCP（Model Context Protocol）服务器列表无法加载

**症状**

服务器列表一直处于加载状态。

**解决方案**

重启 Qoder IDE 后再试。

# 支持

## 终端执行异常

### 简介

在使用 Qoder 智能体模式时，终端执行高度依赖于你的本地环境和 shell 配置。你可能会遇到以下问题：

- 无法启动终端
- 命令无法执行
- 没有任何输出

本主题提供常见的排查方法，帮助解决这些问题。

### 常见故障排查方法

#### 方法 1：配置受支持的 shell

Qoder 支持多种 shell。请确保你使用的是兼容的 shell。

1. 打开 Qoder。
2. 按下 Cmd + Shift + P（macOS）或 Ctrl + Shift + P（Windows/Linux）打开命令面板（Command Palette）。
3. 输入 Terminal: Select Default Profile 并选择该项。
4. 选择一个受支持的 shell：
   - Linux/macOS：bash、fish、pwsh、zsh
   - Windows：Git Bash、pwsh
5. 完全关闭并重新打开 Qoder 以使更改生效。

#### 方法 2：手动安装 shell 集成

如果终端集成仍然失败，请通过在 shell 的配置文件中添加相应语句来手动安装 shell 集成。

*zsh（~/.zshrc）：*
```bash
[[ "$TERM_PROGRAM" == "vscode" ]] && . "$(code --locate-shell-integration-path zsh)"
```

*Bash（~/.bashrc）：*
```bash
[[ "$TERM_PROGRAM" == "vscode" ]] && . "$(code --locate-shell-integration-path bash)"
```

*PowerShell（$Profile）：*
```bash
[[ "$TERM_PROGRAM" == "vscode" ]] && . "$(code --locate-shell-integration-path bash)"
```

*Fish（~/.config/fish/config.fish）：*
```bash
string match -q "$TERM_PROGRAM" "vscode"; and . (code --locate-shell-integration-path fish)
```

在编辑该文件后：

1. 保存更改。
2. 完全重启 Qoder。

针对其他 shell，请参阅手动 shell 集成。

#### 如果问题仍然存在

如果你仍然看不到终端输出：

1. 点击"Terminate Terminal"按钮以关闭当前终端会话。
2. 重新运行该命令。这会刷新终端连接，通常能解决临时性问题。

### Windows 专属故障排除

#### Git Bash

1. 从 https://git-scm.com/downloads/win 下载并安装 Windows 版 Git。
2. 退出并重新打开 Qoder。
3. 将"Git Bash"设为默认终端：
   - a. 打开命令面板（Command Palette）。
   - b. 运行：Terminal: Select Default Profile。
   - c. 选择 Git Bash。

#### PowerShell

请确保使用 PowerShell 7 或更高版本。

查看当前版本：
```powershell
$PSVersionTable.PSVersion
```

如有需要，请更新 PowerShell。

默认情况下，出于安全考虑，PowerShell 会限制脚本执行。您可能需要调整执行策略。

1. 以管理员身份打开 PowerShell：
   - 按下 Win + X
   - 选择 Windows PowerShell（管理员）或 Windows Terminal（管理员）
2. 检查当前策略：
   ```powershell
   Get-ExecutionPolicy

   # 如果输出是 RemoteSigned、Unrestricted 或 Bypass，您可能不需要更改执行策略。这些设置应该允许 shell 集成正常工作。
   # 如果输出是 Restricted 或 AllSigned，您可能需要更改策略以启用 shell 集成。
   ```
3. 为你的用户更新策略：
   ```powershell
   Set-ExecutionPolicy RemoteSigned -Scope CurrentUser

   # 这将仅为当前用户设置 RemoteSigned 策略，比系统级更改更安全。
   ```
4. 在出现提示时按 Y 确认，然后验证：
   ```powershell
   Get-ExecutionPolicy
   ```
5. 重启 Qoder 后重试。

#### WSL

如果使用 Windows Subsystem for Linux（WSL）：

1. 在你的 ~/.bashrc 中添加以下一行：
   ```bash
   . "$(code --locate-shell-integration-path bash)"
   ```
2. 重新加载你的 shell，或运行 source ~/.bashrc。
3. 在 Qoder 中再次尝试该终端命令。

### 其他常见问题

#### 异常终端输出

如果你看到：

- 乱码
- 方块符号
- 转义序列（例如：^[[1m、^[[32m）
- 控制码

这通常是由第三方 shell 个性化配置引起的，例如：

- Powerlevel10k
- Oh My Zsh
- 自定义的 fish 主题

**解决方案**

1. 在你的 shell 配置文件中暂时禁用这些个性化配置。
2. 例如，在 ~/.zshrc 中，将与 Powerlevel10k 相关的那一行注释掉：
   ```bash
   # source /path/to/powerlevel10k/powerlevel10k.zsh-theme
   ```
3. 重启 Qoder 并进行测试。
4. 如果问题已解决，请逐项重新启用自定义设置，以定位发生冲突的组件。
5. 为长期使用，请选择与 Qoder 终端集成兼容的配置。