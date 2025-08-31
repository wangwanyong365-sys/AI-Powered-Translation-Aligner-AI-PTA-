# <a name="chinese-version"></a>AI-Powered Translation Aligner (AI-PTA)

[English](#english-version)

---

一个基于AI的翻译对齐工具，使用Python和Tkinter构建的GUI应用程序，能够将中文文本翻译成英文并生成对齐的语料库。

<img width="1204" height="1354" alt="image" src="https://github.com/user-attachments/assets/2b912507-17eb-4664-afd9-8f868c3c2f1f" />


### 功能特性

- **智能段落分割**: 自动按空行分割文本段落。
- **上下文感知翻译**: 支持添加上下文段落辅助翻译，提升翻译准确性。
- **多API提供商支持**: 集成 DeepSeek、SiliconFlow、OpenAI 等多家API服务。
- **Prompt管理**: 用户可自定义和保存用于翻译的提示词（Prompt）。
- **批量处理**: 支持同时处理一个或多个TXT文件。
- **双语对齐输出**: 生成 Excel 格式的双语对齐语料库，方便后续使用。
- **错误日志**: 自动记录处理过程中的错误信息，便于调试和问题排查。

### 系统要求

- Python 3.7+
- Windows 10 及以上版本 (推荐)

### 安装

1.  克隆或下载本项目到本地。

2.  安装所需的依赖库：
    ```bash
    pip install openai tiktoken pandas openpyxl
    ```
    或者，直接运行项目中的批处理文件：
    ```bash
    requirements.bat
    ```

### 使用方法

1.  **启动应用程序**:
    ```bash
    python translator_app.py
    ```
    或者，直接运行项目中的批处理文件：
    ```bash
    run.bat
    ```

2.  **配置设置**:
    - 在 "API Key" 输入框中填入您的API密钥。
    - 选择您要使用的 "API服务商" (DeepSeek/SiliconFlow/OpenAI)。
    - 根据需要设置 "最大Token数"、"上下文段落数" 等参数。

3.  **选择文件**: 点击 "选择TXT文件" 按钮，添加一个或多个需要翻译的文本文件。

4.  **开始处理**: 点击 "开始处理" 按钮，程序将开始执行翻译和对齐任务。

### 输出文件

处理完成后，每个输入文件会在其所在目录下生成一个同名文件夹，其中包含：

- `[文件名]_translated.txt` - 完整的翻译后文本。
- `[文件名]_corpus.xlsx` - Excel 格式的双语对齐语料库。

### 项目结构

```
AI-PTA/
├── translator_app.py      # 主应用程序
├── requirements.bat       # 依赖安装脚本
├── run.bat                # 快速运行脚本
├── settings.json          # 配置文件
├── alpha/                 # 历史版本
└── sample text/           # 示例文本
    ├── 差不多先生.txt
    └── 心经.txt
```

### 许可证

本项目采用 MIT 许可证。详细信息请参见应用程序内的许可证说明。

### 作者

- **王万涌 (Wanyong Wang)**
- 香港理工大学 中文及双语学系
- Email: wangwanyong365@hotmail.com

### 版本

当前版本: v0.6

[返回顶部](#readme) | [Switch to English](#english-version)

---

## <a name="english-version"></a>AI-Powered Translation Aligner (AI-PTA)

An AI-based translation alignment tool. It's a GUI application built with Python and Tkinter that translates Chinese text into English and generates an aligned bilingual corpus.

### Features

- **Intelligent Paragraph Splitting**: Automatically splits text into paragraphs based on blank lines.
- **Context-Aware Translation**: Supports adding contextual paragraphs to improve translation accuracy.
- **Multi-API Provider Support**: Integrates with multiple API services, including DeepSeek, SiliconFlow, and OpenAI.
- **Prompt Management**: Allows users to customize and save prompts for translation.
- **Batch Processing**: Supports processing one or more TXT files simultaneously.
- **Bilingual Aligned Output**: Generates a bilingual aligned corpus in Excel format for easy use.
- **Error Logging**: Automatically records error messages during processing for convenient debugging and troubleshooting.

### System Requirements

- Python 3.7+
- Windows 10 or later (Recommended)

### Installation

1.  Clone or download this project to your local machine.

2.  Install the required dependencies:
    ```bash
    pip install openai tiktoken pandas openpyxl
    ```
    Alternatively, you can run the batch file in the project directory:
    ```bash
    requirements.bat
    ```

### Usage

1.  **Start the application**:
    ```bash
    python translator_app.py
    ```
    Alternatively, you can run the batch file:
    ```bash
    run.bat
    ```

2.  **Configure Settings**:
    - Enter your API key in the "API Key" field.
    - Select your desired "API Provider" (DeepSeek/SiliconFlow/OpenAI).
    - Adjust parameters like "Max Tokens" and "Context Paragraphs" as needed.

3.  **Select Files**: Click the "Select TXT Files" button to add one or more text files for translation.

4.  **Start Processing**: Click the "Start Processing" button to begin the translation and alignment tasks.

### Output Files

After processing is complete, a new folder with the same name as the input file will be created in its directory, containing:

- `[filename]_translated.txt` - The complete translated text.
- `[filename]_corpus.xlsx` - The bilingual aligned corpus in Excel format.

### Project Structure

```
AI-PTA/
├── translator_app.py      # Main application
├── requirements.bat       # Dependency installation script
├── run.bat                # Quick run script
├── settings.json          # Configuration file
├── alpha/                 # Alpha/Older versions
└── sample text/           # Sample texts
    ├── 差不多先生.txt
    └── 心经.txt
```

### License

This project is licensed under the MIT License. See the license information within the application for more details.

### Author

- **Wanyong Wang (王万涌)**
- Department of Chinese and Bilingual Studies, The Hong Kong Polytechnic University
- Email: wangwanyong365@hotmail.com

### Version

Current Version: v0.6

[Back to Top](#readme) | [切换到中文](#chinese-version)
