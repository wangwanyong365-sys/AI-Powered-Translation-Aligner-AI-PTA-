# AI-Powered Translation Aligner (AI-PTA) v0.9

A comprehensive desktop application for AI-assisted translation and text processing with advanced post-editing capabilities.

## Features

### Core Translation
- **AI-Powered Translation**: Leverages OpenAI-compatible APIs (DeepSeek, SiliconFlow, OpenAI) for high-quality translations
- **Context-Aware Processing**: Includes previous and next paragraphs for better contextual understanding
- **Batch Processing**: Process multiple TXT files simultaneously with automatic folder organization
- **Customizable Prompts**: Save and manage multiple translation prompts with {context} placeholder
- **API Management**: Securely store and manage multiple API keys and providers

### Terminology Management
- **Term Annotator Tool**: Interactive terminology annotation with source text highlighting
- **CSV Terminology Support**: Import/export terminology lists in CSV format
- **Real-time Annotation**: Automatically annotate source text with target terms
- **Terminology Editor**: Add, modify, and delete terms with visual interface

### **Post-Editing Tool (NEW)**
- **AI-Assisted Editing**: Polish and refine translated text using AI models
- **Custom Editing Prompts**: Create and save specialized post-editing instructions
- **Before/After Comparison**: Generate Excel files showing original vs. edited text
- **Batch Processing**: Apply post-editing to entire documents paragraph by paragraph
- **Flexible Placeholders**: Use {paragraph} placeholder for targeted editing

## Installation

1. Install required dependencies:
   ```bash
   pip install openai tiktoken pandas openpyxl
   ```

2. Run the application:
   ```bash
   python main.py
   ```

## Usage

### Basic Translation
1. Select TXT files using the file browser
2. Configure API settings (provider, key, model)
3. Choose or create a translation prompt
4. Set context parameters (previous/next paragraphs)
5. Click "Start Processing"

### Terminology Annotation
1. Access via Tools → Term Annotator
2. Load terminology from CSV files in the `terminology/` folder
3. Select source text file
4. Click "Start Annotation" to apply terminology

### Post-Editing
1. Access via Tools → Post-editing
2. Select the text file to edit
3. Choose or create a post-editing prompt
4. Click "Start Post-editing" to process the document

## File Structure

- `main.py` - Main application window and translation processing
- `app_utils.py` - Utility functions and settings management
- `ui_tools.py` - Term annotator and post-editing tool implementations
- `terminology/` - Folder for CSV terminology files
- `settings.json` - Application settings (auto-generated)
- `error_log.txt` - Error logging

## Supported API Providers

- DeepSeek (https://api.deepseek.com)
- SiliconFlow (https://api.siliconflow.cn/v1) 
- OpenAI (https://api.openai.com/v1)
- Custom providers with OpenAI-compatible endpoints

## Requirements

- Python 3.7+
- OpenAI Python library
- Pandas for Excel export
- Tkinter for GUI

## License

MIT License - See application Help → View License for details

## Authors

- Wanyong Wang (wangwanyong365@hotmail.com)
- Dechao Li (ctdechao@polyu.edu.hk)
- Department of Language Science and Technology (LST)
- The Hong Kong Polytechnic University