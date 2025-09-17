# AI-Powered Translation Aligner (AI-PTA) v0.18

A comprehensive desktop application for AI-assisted translation and text processing with advanced post-editing capabilities.

**Note**: The AI-Powered Translation Aligner program has been **officially released** starting from version **0.18**. 

This means you can directly click to use it on a Windows computer **without** installing Python.

If you want to use this software, please adjust the settings first. This is very important!

<img width="1802" height="1128" alt="image" src="https://github.com/user-attachments/assets/69dd4a37-c951-4d44-929d-6d95858e7251" />

## New Features in v0.18

<img width="518" height="420" alt="image" src="https://github.com/user-attachments/assets/29cbfab4-d3a1-4771-9c8c-dc2ac99dcfe3" />

Fixed some known bugs in the API Provider ribbon and added the ability to call the DeepSeek model from Microsoft Azure.

### Post-Editing Tool
- **Batch Processing**: Apply post-editing to entire documents paragraph by paragraph
- **AI-Assisted Editing**: Polish and refine translated text using AI models with custom editing prompts
- **Before/After Comparison**: Generate Excel files showing original vs. edited text side-by-side
- **Batch Processing**: Apply post-editing to entire documents paragraph by paragraph
- **Flexible Placeholders**: Use {source} and {target} placeholders for targeted editing instructions
- **Resume Capability**: Automatic task resumption with progress tracking

<img width="1052" height="948" alt="image" src="https://github.com/user-attachments/assets/dd660c3d-9f3a-4eb6-96e8-dd78cd8f929c" />

### API Connection Testing
- **Built-in API Testing**: Test API connections directly from the main interface
- **Real-time Validation**: Immediate feedback on API connectivity and model availability
- **Error Diagnostics**: Detailed error reporting for connection issues

### Azure OpenAI Integration
- **Streamlined Configuration**: Simplified Azure endpoint and API version management
- **Enhanced Security**: Better handling of Azure-specific authentication parameters
- **Configuration Persistence**: Automatic saving of Azure-specific settings

### User Interface
- **Improved Status Indicators**: More detailed progress and status messaging
- **Better Error Handling**: Enhanced error reporting throughout the application

### Terminology Management
- **Interactive Term Editor**: Add, modify, and delete terms with visual interface
- **Real-time Annotation**: Automatically annotate source text with target terms
- **CSV Terminology Support**: Import/export terminology lists in CSV format
- **Term Highlighting**: Visual source text highlighting with target term annotations

<img width="1502" height="1098" alt="image" src="https://github.com/user-attachments/assets/66c47f56-a757-4bba-9e51-5a19b1b5ab3d" />

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
