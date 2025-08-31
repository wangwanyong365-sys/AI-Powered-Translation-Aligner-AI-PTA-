# AI-Powered Translation Aligner (AI-PTA)

一个基于AI的翻译对齐工具，使用Python和Tkinter构建的GUI应用程序，能够将中文文本翻译成英文并生成对齐的语料库。

## 功能特性

- **智能段落分割**: 自动按空行分割文本段落
- **上下文感知翻译**: 支持添加上下文段落辅助翻译
- **多API提供商支持**: DeepSeek、SiliconFlow、OpenAI
- **Prompt管理**: 可自定义和保存翻译提示词
- **批量处理**: 支持同时处理多个TXT文件
- **双语对齐输出**: 生成Excel格式的双语对齐语料库
- **错误日志**: 自动记录错误信息便于调试

## 系统要求

- Python 3.7+
- Windows 10 及以上（推荐）

## 安装

1. 克隆或下载项目文件
2. 安装依赖：
   ```bash
   pip install openai tiktoken pandas openpyxl
   ```
   或者运行：
   ```bash
   requirements.bat
   ```

## 使用方法

1. **启动应用程序**:
   ```bash
   python translator_app.py
   ```
   或者运行：
   ```bash
   run.bat
   ```

2. **配置设置**:
   - 在"API Key"中输入您的API密钥
   - 选择API服务商（DeepSeek/SiliconFlow/OpenAI）
   - 设置最大Token数、上下文段落数等参数

3. **选择文件**: 点击"选择TXT文件"按钮添加要翻译的文本文件

4. **开始处理**: 点击"开始处理"按钮开始翻译

## 输出文件

处理完成后，每个输入文件会在同目录下生成一个文件夹，包含：
- `[文件名]_translated.txt` - 完整的翻译文本
- `[文件名]_corpus.xlsx` - Excel格式的双语对齐语料库

## 项目结构

```
AI-PTA/
├── translator_app.py      # 主应用程序
├── requirements.bat       # 依赖安装脚本
├── run.bat               # 运行脚本
├── settings.json         # 配置文件
├── alpha/               # 历史版本
└── sample text/         # 示例文本
    ├── 差不多先生.txt
    └── 心经.txt
```

## 许可证

MIT License - 详见应用程序内的许可证信息

## 作者

王万涌 (Wanyong Wang)  
香港理工大学中文及双语学系  
Email: wangwanyong365@hotmail.com

## 版本

当前版本: v0.6