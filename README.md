# AI-Powered Translation Aligner (AI-PTA) v0.14

A comprehensive desktop application for AI-assisted translation and text processing with advanced post-editing capabilities.

## New Features in v0.14

### Enhanced Post-Editing Tool
- **AI-Assisted Editing**: Polish and refine translated text using AI models with custom editing prompts
- **Before/After Comparison**: Generate Excel files showing original vs. edited text side-by-side
- **Batch Processing**: Apply post-editing to entire documents paragraph by paragraph
- **Flexible Placeholders**: Use {source} and {target} placeholders for targeted editing instructions
- **Resume Capability**: Automatic task resumption with progress tracking

### Advanced Terminology Management
- **Interactive Term Editor**: Add, modify, and delete terms with visual interface
- **Real-time Annotation**: Automatically annotate source text with target terms
- **CSV Terminology Support**: Import/export terminology lists in CSV format
- **Term Highlighting**: Visual source text highlighting with target term annotations

### Microsoft Azure Integration
- **Azure OpenAI Support**: Full integration with Microsoft Azure OpenAI services
- **Custom Endpoint Configuration**: Support for custom Azure endpoints and API versions
- **Secure Key Management**: Encrypted API key storage and management

### Enhanced API Management
- **Multiple Provider Support**: DeepSeek, SiliconFlow, OpenAI, and Microsoft Azure
- **API Key Management**: Secure storage and organization of multiple API keys
- **Connection Testing**: Built-in API connection testing and validation
- **Custom Model Names**: Support for custom model configurations

### Improved User Experience
- **Resume Functionality**: Automatic recovery from interruptions with resume files
- **Progress Tracking**: Real-time progress indicators and timer display
- **Error Handling**: Comprehensive error logging and user-friendly error messages
- **Status Updates**: Detailed status messages with color-coded indicators

## Core Features

### Translation Engine
- **AI-Powered Translation**: Leverages OpenAI-compatible APIs for high-quality translations
- **Context-Aware Processing**: Includes previous and next paragraphs for better contextual understanding
- **Batch Processing**: Process multiple TXT files simultaneously with automatic folder organization
- **Customizable Prompts**: Save and manage multiple translation prompts with {context} placeholder

### File Management
- **Automatic Organization**: Creates output folders for each processed file
- **Excel Export**: Generates side-by-side comparison Excel files
- **Text Export**: Produces clean translated text files
- **Error Logging**: Comprehensive error tracking and reporting

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
2. Select the Excel file to edit
3. Choose or create a post-editing prompt
4. Click "Start Post-editing" to process the document

## File Structure

- `main.py` - Main application window and translation processing
- `app_utils.py` - Utility functions and settings management
- `ui_tools.py` - Term annotator and post-editing tool implementations
- `terminology/` - Folder for CSV terminology files
- `settings.json` - Application settings (auto-generated)
- `error_log.txt` - Error logging
- `resume_info.json` - Translation task resume data
- `resume_post_edit.json` - Post-editing task resume data

## Supported API Providers

- **DeepSeek**: https://api.deepseek.com
- **SiliconFlow**: https://api.siliconflow.cn/v1
- **OpenAI**: https://api.openai.com/v1
- **Microsoft Azure**: Custom endpoints with Azure OpenAI
- Custom providers with OpenAI-compatible endpoints

## Requirements

- Python 3.7+
- OpenAI Python library
- Pandas for Excel export
- OpenPyXL for Excel manipulation
- Tkinter for GUI

## License

MIT License - See application Help → View License for details

## Authors

- Wanyong Wang (wangwanyong365@hotmail.com)
- Dechao Li (ctdechao@polyu.edu.hk)
- Department of Language Science and Technology (LST)
- The Hong Kong Polytechnic University