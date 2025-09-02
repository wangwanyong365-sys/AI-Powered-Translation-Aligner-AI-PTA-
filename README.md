# AI-Powered Translation Aligner (AI-PTA) v0.7

<div align="center">
  <button onclick="switchLanguage('zh')" style="background: #0078D7; color: white; border: none; padding: 8px 16px; margin: 5px; border-radius: 4px; cursor: pointer;">中文</button>
  <button onclick="switchLanguage('en')" style="background: #0078D7; color: white; border: none; padding: 8px 16px; margin: 5px; border-radius: 4px; cursor: pointer;">English</button>
</div>

<div id="zh-content" style="display: block;">

## 📖 项目简介

AI-PTA (AI-Powered Translation Aligner) 是一个基于人工智能的翻译对齐工具，专门用于处理文本翻译和对齐任务。该工具集成了术语标注、上下文感知翻译和语料库生成功能。

## ✨ 主要功能

- **智能翻译**: 支持多种AI API提供商（DeepSeek、SiliconFlow、OpenAI）
- **术语管理**: 内置术语标注器，支持术语的增删改查
- **上下文感知**: 可配置上下文段落数，提高翻译准确性
- **批量处理**: 支持多文件批量翻译处理
- **语料库生成**: 自动生成Excel格式的双语对齐语料库
- **Prompt管理**: 可自定义和保存翻译提示模板

## 🚀 快速开始

### 环境要求

- Python 3.7+
- Windows/Linux/macOS

### 安装依赖

```bash
pip install -r requirements.txt
```

或者直接运行：
```bash
requirements.bat
```

### 启动应用

```bash
python translator_app.py
```

或者直接运行：
```bash
run.bat
```

## 📁 项目结构

```
AI-PTA/
├── translator_app.py     # 主应用程序
├── requirements.bat     # 依赖安装脚本
├── run.bat             # 启动脚本
├── terminology/         # 术语库目录
│   └── test.csv        # 示例术语库
├── settings.json       # 配置文件（自动生成）
└── error_log.txt       # 错误日志（自动生成）
```

## ⚙️ 配置说明

### API 设置

1. 在设置界面选择API提供商
2. 输入或选择API Key
3. 配置模型名称（可选）

### 术语库管理

1. 将CSV格式的术语库文件放入 `terminology/` 目录
2. CSV格式：源术语,目标术语（每行一对）
3. 支持在应用中动态管理术语

### Prompt 模板

- 使用 `{context}` 占位符插入上下文
- 支持多个Prompt模板的保存和管理

## 🎯 使用指南

1. **选择文件**: 点击"选择 TXT 文件"按钮添加待翻译文件
2. **配置参数**: 设置Token数、上下文段落数等参数
3. **选择术语库**: 从下拉菜单选择要使用的术语库
4. **开始处理**: 点击"开始处理"按钮开始翻译
5. **查看结果**: 翻译结果保存在原文件同名的子目录中

## 🔧 工具菜单

- **术语标注器**: 打开独立的术语管理工具
- **帮助**: 查看关于信息和许可证

## 📊 输出文件

处理完成后，每个输入文件会生成：
- `[文件名]_translated.txt` - 翻译后的完整文本
- `[文件名]_corpus.xlsx` - Excel格式的双语对齐语料库

## 🛠️ 开发信息

- **开发者**: 王万涌 (Wanyong Wang)
- **机构**: 香港理工大学语言科学与技术系
- **邮箱**: wangwanyong365@hotmail.com
- **许可证**: MIT License

## 🤝 贡献

欢迎提交Issue和Pull Request来改进这个项目。

## 📄 许可证

本项目采用 MIT 许可证 - 查看 [LICENSE](LICENSE) 文件了解详情。

</div>

<div id="en-content" style="display: none;">

## 📖 Project Introduction

AI-PTA (AI-Powered Translation Aligner) is an AI-based translation alignment tool specifically designed for text translation and alignment tasks. The tool integrates terminology annotation, context-aware translation, and corpus generation functionalities.

## ✨ Key Features

- **Smart Translation**: Supports multiple AI API providers (DeepSeek, SiliconFlow, OpenAI)
- **Terminology Management**: Built-in terminology annotator with CRUD operations
- **Context Awareness**: Configurable context paragraphs for improved translation accuracy
- **Batch Processing**: Supports batch translation of multiple files
- **Corpus Generation**: Automatically generates Excel-format bilingual aligned corpora
- **Prompt Management**: Customizable and savable translation prompt templates

## 🚀 Quick Start

### Requirements

- Python 3.7+
- Windows/Linux/macOS

### Install Dependencies

```bash
pip install -r requirements.txt
```

Or run directly:
```bash
requirements.bat
```

### Launch Application

```bash
python translator_app.py
```

Or run directly:
```bash
run.bat
```

## 📁 Project Structure

```
AI-PTA/
├── translator_app.py     # Main application
├── requirements.bat      # Dependency installation script
├── run.bat              # Launch script
├── terminology/         # Terminology directory
│   └── test.csv         # Example terminology database
├── settings.json        # Configuration file (auto-generated)
└── error_log.txt        # Error log (auto-generated)
```

## ⚙️ Configuration

### API Settings

1. Select API provider in settings interface
2. Enter or select API Key
3. Configure model name (optional)

### Terminology Management

1. Place CSV-format terminology files in `terminology/` directory
2. CSV format: source term,target term (one pair per line)
3. Supports dynamic terminology management within the application

### Prompt Templates

- Use `{context}` placeholder to insert context
- Supports saving and managing multiple prompt templates

## 🎯 Usage Guide

1. **Select Files**: Click "Select TXT Files" button to add files for translation
2. **Configure Parameters**: Set token count, context paragraphs, etc.
3. **Choose Terminology**: Select terminology database from dropdown
4. **Start Processing**: Click "Start Processing" button to begin translation
5. **View Results**: Translation results are saved in subdirectories with original file names

## 🔧 Tools Menu

- **Terminology Annotator**: Open standalone terminology management tool
- **Help**: View about information and license

## 📊 Output Files

After processing, each input file generates:
- `[filename]_translated.txt` - Complete translated text
- `[filename]_corpus.xlsx` - Excel-format bilingual aligned corpus

## 🛠️ Development Information

- **Developer**: Wanyong Wang
- **Institution**: Department of Language Science and Technology, The Hong Kong Polytechnic University
- **Email**: wangwanyong365@hotmail.com
- **License**: MIT License

## 🤝 Contributing

Welcome to submit Issues and Pull Requests to improve this project.

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

</div>

<script>
function switchLanguage(lang) {
    if (lang === 'zh') {
        document.getElementById('zh-content').style.display = 'block';
        document.getElementById('en-content').style.display = 'none';
    } else if (lang === 'en') {
        document.getElementById('zh-content').style.display = 'none';
        document.getElementById('en-content').style.display = 'block';
    }
}
</script>

<style>
body {
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
    line-height: 1.6;
    max-width: 800px;
    margin: 0 auto;
    padding: 20px;
}

h1, h2, h3, h4 {
    color: #333;
    margin-top: 1.5em;
}

code {
    background: #f4f4f4;
    padding: 2px 6px;
    border-radius: 3px;
    font-family: 'Consolas', 'Monaco', monospace;
}

pre code {
    display: block;
    padding: 10px;
    border-radius: 5px;
    overflow-x: auto;
}

button:hover {
    opacity: 0.9;
}
</style>