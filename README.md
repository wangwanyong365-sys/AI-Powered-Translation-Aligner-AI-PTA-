<!--
GitHub 语言切换功能
使用 HTML 注释实现中英文切换
-->

<!-- en -->
# AI-Powered Translation Aligner (AI-PTA) v0.7

A powerful desktop application for AI-assisted translation and terminology annotation with bilingual corpus generation capabilities.

## Features

- **AI-Powered Translation**: Integrates with multiple AI providers (DeepSeek, SiliconFlow, OpenAI) for high-quality translations
- **Terminology Annotation**: Built-in terminology annotator for source text markup
- **Bilingual Corpus Generation**: Automatically generates aligned bilingual Excel files
- **Context-Aware Translation**: Supports context window settings for better translation quality
- **Customizable Prompts**: Flexible prompt management system for different translation scenarios
- **Batch Processing**: Process multiple text files simultaneously
- **User-Friendly GUI**: Modern Tkinter-based interface with Chinese localization

## Installation

1. **Install Python Dependencies**:
   ```bash
   pip install openai tiktoken pandas openpyxl
   ```

2. **Run the Application**:
   ```bash
   python translator_app.py
   ```
   
   Or use the provided batch files:
   - `requirements.bat` - Install dependencies
   - `run.bat` - Launch the application

## Usage

1. **Select Files**: Choose one or more TXT files for processing
2. **Configure Settings**: Set API key, model, and translation parameters
3. **Manage Terminology**: Use the built-in terminology annotator to create/edit term databases
4. **Start Processing**: Click "Start Processing" to begin translation and corpus generation
5. **Export Results**: Translated texts and bilingual Excel files are saved in separate folders

## API Configuration

- **Supported Providers**: DeepSeek, SiliconFlow, OpenAI
- **API Key Management**: Save and manage multiple API keys with descriptive names
- **Model Selection**: Choose from available models or add custom model names

## Terminology Management

- **CSV Format**: Terminology databases are stored as CSV files in the `terminology/` folder
- **Real-time Editing**: Add, modify, or delete terms during annotation
- **Automatic Saving**: Changes are automatically saved to the terminology database

## Output Format

For each input file, the application creates:
- `[filename]_translated.txt` - Full translated text
- `[filename]_corpus.xlsx` - Bilingual aligned Excel corpus

## License

MIT License - See [LICENSE](LICENSE) file for details

## Author

Wanyong Wang  
Department of Language Science and Technology (LST)  
The Hong Kong Polytechnic University  
Email: wangwanyong365@hotmail.com

<!-- zh -->
# AI 辅助翻译对齐工具 (AI-PTA) v0.7

一款功能强大的桌面应用程序，用于AI辅助翻译和术语标注，具备双语语料库生成能力。

## 功能特点

- **AI 辅助翻译**: 集成多个AI服务提供商（DeepSeek、SiliconFlow、OpenAI）进行高质量翻译
- **术语标注**: 内置术语标注器，支持源文本标记
- **双语语料库生成**: 自动生成对齐的双语Excel文件
- **上下文感知翻译**: 支持上下文窗口设置，提高翻译质量
- **可定制提示词**: 灵活的提示词管理系统，适应不同翻译场景
- **批量处理**: 同时处理多个文本文件
- **用户友好界面**: 基于Tkinter的现代化界面，支持中文本地化

## 安装

1. **安装Python依赖**:
   ```bash
   pip install openai tiktoken pandas openpyxl
   ```

2. **运行应用程序**:
   ```bash
   python translator_app.py
   ```
   
   或使用提供的批处理文件：
   - `requirements.bat` - 安装依赖
   - `run.bat` - 启动应用程序

## 使用方法

1. **选择文件**: 选择一个或多个TXT文件进行处理
2. **配置设置**: 设置API密钥、模型和翻译参数
3. **管理术语**: 使用内置术语标注器创建/编辑术语数据库
4. **开始处理**: 点击"开始处理"开始翻译和语料库生成
5. **导出结果**: 翻译后的文本和双语Excel文件保存在单独的文件夹中

## API 配置

- **支持的服务商**: DeepSeek、SiliconFlow、OpenAI
- **API密钥管理**: 使用描述性名称保存和管理多个API密钥
- **模型选择**: 从可用模型中选择或添加自定义模型名称

## 术语管理

- **CSV格式**: 术语数据库以CSV文件格式存储在`terminology/`文件夹中
- **实时编辑**: 在标注过程中添加、修改或删除术语
- **自动保存**: 更改自动保存到术语数据库

## 输出格式

对于每个输入文件，应用程序会创建：
- `[文件名]_translated.txt` - 完整翻译文本
- `[文件名]_corpus.xlsx` - 双语对齐Excel语料库

## 许可证

MIT 许可证 - 详见 [LICENSE](LICENSE) 文件

## 作者

王万涌  
语言科学与技术系 (LST)  
香港理工大学  
邮箱: wangwanyong365@hotmail.com

<!-- /zh -->
<!-- /en -->