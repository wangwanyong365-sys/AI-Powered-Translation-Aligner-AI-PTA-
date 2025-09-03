# AI-Powered Translation Aligner (AI-PTA)

A comprehensive desktop application for AI-assisted translation and terminology management with built-in annotation capabilities.

<img width="1202" height="1353" alt="image" src="https://github.com/user-attachments/assets/b65da4b7-8d06-4a22-a3aa-04e4a8a4eacd" />

## Features

- **AI-Powered Translation**: Uses OpenAI-compatible APIs (DeepSeek, SiliconFlow, OpenAI) for high-quality translations
- **Terminology Management**: Create and manage custom terminology databases in CSV format
- **Text Annotation**: Automatically annotate source text with terminology translations
- **Context-Aware Processing**: Maintains paragraph context for more accurate translations
- **Batch Processing**: Process multiple text files simultaneously
- **Export Capabilities**: Export translations as text files and Excel spreadsheets

<img width="1502" height="1098" alt="image" src="https://github.com/user-attachments/assets/0c5c16d4-252c-4057-8c6c-6f96d0934a52" />

## System Requirements

- Python 3.7+
- Windows (Recommended), macOS, or Linux
- Internet connection for API access

## Installation

1. **Install Python Dependencies**:
   ```bash
   pip install openai tiktoken pandas openpyxl
   ```
   
   Or run the included batch file:
   ```
   requirements.bat
   ```

2. **Run the Application**:
   ```bash
   python translator_app.py
   ```
   
   Or use the provided batch file:
   ```
   run.bat
   ```

## Getting Started

### 1. Configure API Settings

1. Open the application
2. Go to Settings → API Provider and select your preferred service
3. Enter your API key in the API Key field
4. Select your preferred model (e.g., "deepseek-chat")
5. Save your settings

### 2. Set Up Terminology

1. Create a `terminology` folder in the application directory
2. Add CSV files with your terminology (format: `source_term,target_term`)
3. Use the built-in Term Annotator tool (Tools → Term Annotator) to manage terminology

### 3. Process Files

1. Click "Select TXT Files" to choose your source text files
2. Configure translation settings (max tokens, context paragraphs)
3. Click "Start Processing" to begin translation

## File Structure

```
project/
├── translator_app.py    # Main application
├── requirements.bat     # Dependency installer
├── run.bat             # Application launcher
├── terminology/        # Terminology database folder
│   └── *.csv           # CSV files with source→target terms
├── settings.json       # Application settings (auto-generated)
└── error_log.txt       # Error logging (auto-generated)
```

## Terminology Format

Create CSV files in the `terminology` folder with the format:
```csv
source_term_1,target_term_1
source_term_2,target_term_2
source_term_3,target_term_3
```

Example:
```csv
人类,Man
存在,being
技术,technology
```

## Output Files

For each processed text file, the application creates:
- `[filename]_translated.txt` - Full translated text
- `[filename]_corpus.xlsx` - Excel file with source and translation columns

## Supported API Providers

- **DeepSeek**: https://api.deepseek.com
- **SiliconFlow**: https://api.siliconflow.cn/v1  
- **OpenAI**: https://api.openai.com/v1

## Custom Prompts

The application supports custom translation prompts. Use `{context}` as a placeholder for the text to be translated and surrounding context.

## Troubleshooting

### Common Issues

1. **API Connection Errors**: Check your API key and internet connection
2. **File Not Found**: Ensure terminology CSV files are in the `terminology` folder
3. **Memory Issues**: Reduce "Max Tokens" setting for large files

### Error Logging

Errors are automatically logged to `error_log.txt` for debugging purposes.

## License

MIT License - See included license information in the application.

## Authors

- **Wanyong Wang** - wangwanyong365@hotmail.com
- **Dechao Li** - ctdechao@polyu.edu.hk

Department of Language Science and Technology (LST)  
The Hong Kong Polytechnic University  
Kowloon, Hong Kong, China

## Version

v0.8 - Current stable release
