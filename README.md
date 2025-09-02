# AI-Powered Translation Aligner (AI-PTA) v0.7

[English Version](#english-version)

## 中文版

### 项目简介
AI-Powered Translation Aligner (AI-PTA) 是一个基于人工智能的翻译对齐工具，专门用于处理文本翻译和术语标注任务。该工具集成了多种AI API服务商，提供高效的翻译处理和术语管理功能。

### 主要功能
- **智能翻译处理**: 支持批量处理TXT文件，利用AI模型进行高质量翻译
- **术语标注器**: 内置术语管理工具，支持术语的增删改查和自动标注
- **多API支持**: 兼容DeepSeek、SiliconFlow、OpenAI等多种AI服务商
- **上下文感知**: 支持设置上下文段落数，提高翻译准确性
- **批量处理**: 支持多文件批量处理，自动生成翻译结果和Excel对齐文件

### 系统要求
- Python 3.7+
- Windows/Linux/macOS

### 安装步骤
1. 克隆或下载项目文件
2. 运行 `requirements.bat` 安装依赖包
3. 运行 `run.bat` 启动应用程序

### 使用方法
1. **选择文件**: 点击"选择TXT文件"按钮添加待翻译文件
2. **配置参数**: 设置API密钥、模型名称、最大Token数等参数
3. **管理术语**: 使用"术语标注器"工具管理翻译术语库
4. **开始处理**: 点击"开始处理"按钮执行翻译任务

### 文件结构
```
项目根目录/
├── translator_app.py    # 主应用程序
├── requirements.bat     # 依赖安装脚本
├── run.bat             # 启动脚本
└── terminology/        # 术语库文件夹
    └── test.csv        # 示例术语文件
```

### 技术支持
- 开发者: 王万涌 (Wanyong Wang)
- 机构: 香港理工大学语言科学与技术系
- 邮箱: wangwanyong365@hotmail.com

### 许可证
本项目采用 MIT 许可证 - 详见[许可证文件](LICENSE)

---

<a id="english-version"></a>
## English Version

### Project Overview
AI-Powered Translation Aligner (AI-PTA) is an AI-based translation alignment tool designed for text translation and terminology annotation tasks. The tool integrates multiple AI API providers, offering efficient translation processing and terminology management capabilities.

### Key Features
- **Intelligent Translation Processing**: Batch processing of TXT files using AI models for high-quality translation
- **Terminology Annotator**: Built-in terminology management tool supporting CRUD operations and automatic annotation
- **Multi-API Support**: Compatible with DeepSeek, SiliconFlow, OpenAI, and other AI service providers
- **Context Awareness**: Supports setting context paragraphs to improve translation accuracy
- **Batch Processing**: Supports multi-file batch processing with automatic generation of translation results and Excel alignment files

### System Requirements
- Python 3.7+
- Windows/Linux/macOS

### Installation Steps
1. Clone or download the project files
2. Run `requirements.bat` to install dependencies
3. Run `run.bat` to start the application

### Usage Instructions
1. **Select Files**: Click "Select TXT Files" button to add files for translation
2. **Configure Parameters**: Set API key, model name, max tokens, and other parameters
3. **Manage Terminology**: Use the "Terminology Annotator" tool to manage translation terminology
4. **Start Processing**: Click "Start Processing" button to execute translation tasks

### File Structure
```
Project Root/
├── translator_app.py    # Main application
├── requirements.bat     # Dependency installation script
├── run.bat             # Startup script
└── terminology/        # Terminology folder
    └── test.csv        # Example terminology file
```

### Technical Support
- Developer: Wanyong Wang
- Institution: Department of Language Science and Technology, The Hong Kong Polytechnic University
- Email: wangwanyong365@hotmail.com

### License
This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.