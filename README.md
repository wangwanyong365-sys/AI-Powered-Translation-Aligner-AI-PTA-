# AI-Powered Translation Aligner (AI-PTA) v0.7

A professional desktop application for AI-assisted translation and terminology management with parallel corpus generation capabilities.

## Features

- **AI-Powered Translation**: Uses OpenAI-compatible APIs (DeepSeek, SiliconFlow, OpenAI) for high-quality translations
- **Terminology Management**: Built-in term annotator for managing translation glossaries
- **Context-Aware Processing**: Maintains paragraph context for more accurate translations
- **Batch Processing**: Process multiple text files simultaneously
- **Parallel Corpus Generation**: Automatically creates Excel files with source-target alignment
- **Customizable Prompts**: Flexible prompt system for different translation requirements
- **API Key Management**: Secure storage and management of multiple API keys

## System Requirements

- Python 3.7+
- Windows (Recommended), macOS, or Linux
- Internet connection for API access

## Installation

1. **Install Python Dependencies**:
   ```bash
   pip install openai tiktoken pandas openpyxl
   ```

2. **Run the Application**:
   ```bash
   python translator_app.py
   ```

## Quick Start

1. **Configure API Settings**:
   - Select your preferred API provider (DeepSeek, SiliconFlow, or OpenAI)
   - Enter your API key (or save it with a memorable name)
   - Optional: Specify a custom model name

2. **Set Up Terminology** (Optional):
   - Use the "Term Annotator" tool from the Tools menu
   - Create CSV files in the `terminology/` folder with source→target term pairs
   - The application will automatically detect and load terminology files

3. **Select Files**:
   - Click "Select TXT Files..." to choose text files for translation
   - Files should contain the source text you want to translate

4. **Configure Translation Settings**:
   - **Max Tokens**: Maximum tokens per API call (default: 8000)
   - **Previous/Next Paragraphs**: Number of context paragraphs to include
   - **Prompt**: Customize the translation instructions (use `{context}` placeholder)

5. **Start Processing**:
   - Click "Start Processing" to begin translation
   - Each file will be processed and saved in its own subfolder
   - Output includes translated text and Excel corpus files

## File Structure

```
project/
├── translator_app.py     # Main application
├── requirements.bat      # Dependency installation script
├── run.bat              # Application launcher
├── terminology/         # Terminology CSV files
│   └── test.csv         # Example terminology file
├── settings.json        # Application settings (auto-generated)
└── error_log.txt        # Error logging (auto-generated)
```

## Terminology Management

Create CSV files in the `terminology/` folder with the format:
```csv
source_term_1,target_term_1
source_term_2,target_term_2
```

The term annotator tool allows you to:
- Add, modify, and delete terms
- Browse and select terminology files
- Annotate source text with terminology tags

## Output Format

For each input file `example.txt`, the application creates:
- `example/example_translated.txt` - Full translated text
- `example/example_corpus.xlsx` - Excel file with aligned source-target paragraphs

## Supported API Providers

- **DeepSeek**: `https://api.deepseek.com`
- **SiliconFlow**: `https://api.siliconflow.cn/v1`
- **OpenAI**: `https://api.openai.com/v1`

## Customization

### Prompts
Modify the translation prompt in the "Prompt Management" section. Use `{context}` as a placeholder for the text context, which includes:
- Previous paragraphs (configurable)
- Current paragraph to translate
- Next paragraphs (configurable)

### Settings
Application settings are automatically saved in `settings.json` and include:
- API keys (encrypted)
- Model preferences
- Custom prompts
- Processing parameters

## Troubleshooting

### Common Issues
1. **API Errors**: Check your API key and provider settings
2. **File Encoding**: Ensure text files use UTF-8 encoding
3. **Dependencies**: Run `requirements.bat` to install required packages

### Error Logging
Detailed error information is saved to `error_log.txt` for debugging.

## License

MIT License - See the application's "View License" option for details.

## Authors

- Wanyong Wang (wangwanyong365@hotmail.com)
- Dechao Li (ctdechao@polyu.edu.hk)
- Department of Language Science and Technology (LST)
- The Hong Kong Polytechnic University

## Version History

- v0.7: Initial release with core translation and terminology features