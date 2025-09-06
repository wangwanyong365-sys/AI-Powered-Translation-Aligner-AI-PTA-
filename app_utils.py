import os
import re
import json
import datetime
import traceback
import tkinter as tk
from tkinter import messagebox

import openai
import pandas as pd


SETTINGS_FILE = "settings.json"
ERROR_LOG_FILE = "error_log.txt"


def log_error(error_message):
    try:
        with open(ERROR_LOG_FILE, 'a', encoding='utf-8') as f:
            timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            full_error = traceback.format_exc()
            f.write(f"--- {timestamp} ---\n")
            f.write(f"{error_message}\n")
            f.write(f"Traceback:\n{full_error}\n\n")
    except Exception as e:
        print(f"Failed to write to error log: {e}")


def load_settings():
    default_settings = {
        "max_tokens": 8000,
        "context_before": 1,
        "context_after": 1,
        "api_providers": {
            "DeepSeek": {
                "base_url": "https://api.deepseek.com",
                "api_keys": {},
                "model_names": ["deepseek-chat", "deepseek-reasoner"]
            },
            "SiliconFlow": {
                "base_url": "https://api.siliconflow.cn/v1",
                "api_keys": {},
                "model_names": []
            },
            "OpenAI": {
                "base_url": "https://api.openai.com/v1",
                "api_keys": {},
                "model_names": ["gpt-4o", "gpt-4-turbo", "gpt-3.5-turbo"]
            },
            "Microsoft Azure": {
                "azure_endpoint": "",
                "api_version": "2024-12-01-preview",
                "api_keys": {},
                "model_names": []
            }
        },
        "prompts": {
            "Default Translation Prompt": (
                "You are a professional, accurate, and faithful translator. "
                "Please translate the text from the \"[Text to Translate]\" section into American English.\n"
                "Directly output the translated content of that section ONLY. "
                "Do not provide any explanations, annotations, or any other extraneous text.\n\n"
                "{context}"
            )
        },
        "post_editing_prompts": {
            "Default Post-editing Prompt": (
                "You are a professional copyeditor. Your task is to polish the following target text for clarity, fluency, and conciseness, using the source text as a reference. "
                "Correct any grammatical errors, improve sentence structure, and ensure the tone is appropriate. "
                "Preserve the original meaning and intent as conveyed in the source text.\n\n"
                "Directly output the edited target text ONLY. Do not provide any explanations or annotations.\n\n"
                "[Source Text]\n{source}\n\n"
                "[Target Text to Edit]\n{target}"
            )
        }
    }
    if not os.path.exists(SETTINGS_FILE):
        return default_settings
    try:
        with open(SETTINGS_FILE, 'r', encoding='utf-8') as f:
            settings = json.load(f)

        for key, value in default_settings.items():
            settings.setdefault(key, value)
        
        default_providers = default_settings.get("api_providers", {})
        loaded_providers = settings.get("api_providers", {})
        for p_name, p_defaults in default_providers.items():
            loaded_providers.setdefault(p_name, p_defaults)
            for sub_key, sub_default in p_defaults.items():
                if isinstance(sub_default, dict):
                    loaded_providers[p_name].setdefault(sub_key, {})
                    for k, v in sub_default.items():
                         loaded_providers[p_name][sub_key].setdefault(k, v)
                else:
                    loaded_providers[p_name].setdefault(sub_key, sub_default)
        settings["api_providers"] = loaded_providers

        settings.pop("api_keys", None)
        settings.pop("model_names", None)
            
        return settings
    except (json.JSONDecodeError, Exception) as e:
        log_error(f"Failed to load settings.json: {e}. Using default settings.")
        return default_settings

def save_settings(settings):
    try:
        with open(SETTINGS_FILE, 'w', encoding='utf-8') as f:
            json.dump(settings, f, indent=4, ensure_ascii=False)
    except Exception as e:
        messagebox.showerror("Error", f"Failed to save settings file: {e}")
        log_error(f"Failed to save settings.json: {e}")


def split_text_into_paragraphs(text):
    paragraphs = re.split(r'\n\s*\n', text)
    return [p.strip() for p in paragraphs if p.strip()]

def translate_single_paragraph(client, model_name, full_prompt, max_tokens):
    try:
        lines = full_prompt.split('\n', 1)
        system_message = lines[0]
        user_message = lines[1] if len(lines) > 1 else ""
        

        response = client.chat.completions.create(
            model=model_name,
            messages=[
                {"role": "system", "content": system_message},
                {"role": "user", "content": user_message},
            ],
            stream=False,
            max_tokens=max_tokens
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        error_message = f"API call failed: {e}"
        log_error(error_message)
        return f"[Translation Failed: {str(e)[:50]}...]"

def test_api_connection(client, model_name):
    try:
        response = client.chat.completions.create(
            model=model_name,
            messages=[
                {"role": "user", "content": "Hello"},
            ],
            stream=False,
            max_tokens=5
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        raise e