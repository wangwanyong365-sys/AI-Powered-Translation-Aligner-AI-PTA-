import os
import json
import time
import threading
import tkinter as tk
from tkinter import ttk, filedialog, messagebox, simpledialog, scrolledtext

import openai
import pandas as pd

from app_utils import load_settings, save_settings, log_error, split_text_into_paragraphs, translate_single_paragraph, test_api_connection
from ui_tools import TermAnnotatorApp, PostEditingWindow

RESUME_FILE = "resume_info.json"

class TranslationApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.settings = load_settings()
        self.selected_files = []
        self.annotator_window = None
        self.post_editor_window = None
        
        self.stop_requested = threading.Event()
        self.is_processing = False
        self.resume_data = None
        self.timer_id = None
        
        self._setup_style()
        self._setup_ui()
        self._post_ui_setup()
        
        self.protocol("WM_DELETE_WINDOW", self._on_closing)
        self.after(100, self._check_for_resume_task)
    
    def _on_closing(self):
        if self.is_processing:
            if not messagebox.askyesno("Confirm Exit", "A translation task is currently in progress. Exiting now will stop it. Are you sure you want to exit?"):
                return
            self.stop_requested.set()
        
        save_settings(self.settings)
        self.destroy()
    
    def _setup_style(self):
        self.style = ttk.Style(self)
        self.style.theme_use("clam")
        self.style.configure("Stop.TButton", font=("Segoe UI", 11), padding=(10, 5))
        self.style.map("Stop.TButton", background=[("active", "#c42b1c"), ("!disabled", "#d13438")], foreground=[("!disabled", "white")])
        self.style.configure("TLabelFrame.Label", font=("Segoe UI", 11, "bold"))
    
    def _setup_ui(self):
        self.title("AI-Powered Translation Aligner (AI-PTA) v0.13")
        self.geometry("1000x700")
        self.minsize(1000, 700)
    
        self.menu_bar = tk.Menu(self)
        self.config(menu=self.menu_bar)

        settings_menu = tk.Menu(self.menu_bar, tearoff=0)
        self.menu_bar.add_cascade(label="Settings", menu=settings_menu)
        settings_menu.add_command(label="Translation Options...", command=self._open_translation_settings)
        
        tools_menu = tk.Menu(self.menu_bar, tearoff=0)
        self.menu_bar.add_cascade(label="Tools", menu=tools_menu)
        tools_menu.add_command(label="Term Annotator", command=self._open_annotator)
        tools_menu.add_command(label="Post-editing", command=self._open_post_editor)
    
        help_menu = tk.Menu(self.menu_bar, tearoff=0)
        self.menu_bar.add_cascade(label="Help", menu=help_menu)
        help_menu.add_command(label="About", command=self._show_about_info)
        help_menu.add_command(label="View License", command=self._show_license_info)
    
        main_frame = ttk.Frame(self, padding="10")
        main_frame.pack(expand=True, fill=tk.BOTH)
        main_frame.rowconfigure(0, weight=1)
        main_frame.columnconfigure(0, weight=1)

        paned_window = ttk.PanedWindow(main_frame, orient=tk.HORIZONTAL)
        paned_window.grid(row=0, column=0, sticky="nsew")

        left_pane = ttk.Frame(paned_window, padding=5)
        right_pane = ttk.Frame(paned_window, padding=5)
        paned_window.add(left_pane, weight=2)
        paned_window.add(right_pane, weight=1)

        left_pane.rowconfigure(1, weight=1)
        left_pane.columnconfigure(0, weight=1)
        
        files_frame = ttk.LabelFrame(left_pane, text="File Selection", padding="10")
        files_frame.grid(row=0, column=0, sticky="ew", pady=(0, 10))
        files_frame.columnconfigure(0, weight=1)
        self.file_listbox = tk.Listbox(files_frame, height=5, font=("Segoe UI", 10))
        self.file_listbox.grid(row=0, column=0, sticky="ew")
        scrollbar = ttk.Scrollbar(files_frame, orient=tk.VERTICAL, command=self.file_listbox.yview)
        scrollbar.grid(row=0, column=1, sticky="ns")
        self.file_listbox.config(yscrollcommand=scrollbar.set)
        browse_button = ttk.Button(files_frame, text="Select TXT Files...", command=self._on_browse_files)
        browse_button.grid(row=1, column=0, columnspan=2, pady=(10, 0), sticky="e")

        prompt_frame = ttk.LabelFrame(left_pane, text="Prompt Management", padding="10")
        prompt_frame.grid(row=1, column=0, sticky="nsew", pady=5)
        prompt_frame.columnconfigure(0, weight=1)
        prompt_frame.rowconfigure(1, weight=1)
        prompt_selection_frame = ttk.Frame(prompt_frame)
        prompt_selection_frame.grid(row=0, column=0, sticky="ew", pady=(0, 5))
        prompt_selection_frame.columnconfigure(1, weight=1)
        ttk.Label(prompt_selection_frame, text="Select Prompt:").grid(row=0, column=0, padx=(0, 5))
        self.prompt_var = tk.StringVar()
        self.prompt_combo = ttk.Combobox(prompt_selection_frame, textvariable=self.prompt_var, state="readonly")
        self.prompt_combo.grid(row=0, column=1, sticky="ew")
        self.prompt_combo.bind("<<ComboboxSelected>>", self._on_prompt_select)
        btn_frame = ttk.Frame(prompt_selection_frame)
        btn_frame.grid(row=0, column=2, padx=(10, 0))
        ttk.Button(btn_frame, text="Add", command=self._add_prompt).pack(side=tk.LEFT, padx=2)
        ttk.Button(btn_frame, text="Save", command=self._save_current_prompt).pack(side=tk.LEFT, padx=2)
        ttk.Button(btn_frame, text="Delete", command=self._delete_prompt).pack(side=tk.LEFT, padx=2)
        self.prompt_text = tk.Text(prompt_frame, wrap=tk.WORD, height=8, font=("Segoe UI", 10))
        self.prompt_text.grid(row=1, column=0, sticky="nsew")
        prompt_scrollbar = ttk.Scrollbar(prompt_frame, orient=tk.VERTICAL, command=self.prompt_text.yview)
        prompt_scrollbar.grid(row=1, column=1, sticky="ns")
        self.prompt_text.config(yscrollcommand=prompt_scrollbar.set)

        right_pane.rowconfigure(0, weight=0)
        right_pane.columnconfigure(0, weight=1)
        
        api_settings_frame = ttk.LabelFrame(right_pane, text="API Settings", padding="10")
        api_settings_frame.grid(row=0, column=0, sticky="new")
        api_settings_frame.columnconfigure(1, weight=1)
    
        ttk.Label(api_settings_frame, text="API Provider:").grid(row=0, column=0, sticky="w", padx=5, pady=5)
        self.api_provider_var = tk.StringVar()
        self.api_provider_combo = ttk.Combobox(api_settings_frame, textvariable=self.api_provider_var, state="readonly")
        self.api_provider_combo.grid(row=0, column=1, sticky="ew", padx=5, pady=5)
        self.api_provider_combo.bind("<<ComboboxSelected>>", self._on_provider_select)
    
        ttk.Label(api_settings_frame, text="API Key:").grid(row=1, column=0, sticky="w", padx=5, pady=5)
        api_key_frame = ttk.Frame(api_settings_frame)
        api_key_frame.grid(row=1, column=1, sticky="ew", padx=5, pady=5)
        api_key_frame.columnconfigure(0, weight=1)
        self.api_key_var = tk.StringVar()
        self.api_key_combo = ttk.Combobox(api_key_frame, textvariable=self.api_key_var)
        self.api_key_combo.grid(row=0, column=0, sticky="ew")
        self.api_key_combo.bind("<<ComboboxSelected>>", self._on_api_key_select)
        self.api_key_combo.bind("<KeyRelease>", self._on_api_key_typed) 
        api_btn_frame = ttk.Frame(api_key_frame)
        api_btn_frame.grid(row=0, column=1, padx=(5,0))
        ttk.Button(api_btn_frame, text="Save", command=self._save_api_key, width=6).pack(side=tk.LEFT, padx=2)
        ttk.Button(api_btn_frame, text="Delete", command=self._delete_api_key, width=6).pack(side=tk.LEFT, padx=2)
    
        ttk.Label(api_settings_frame, text="Model Name:").grid(row=2, column=0, sticky="w", padx=5, pady=5)
        model_frame = ttk.Frame(api_settings_frame)
        model_frame.grid(row=2, column=1, sticky="ew", padx=5, pady=5)
        model_frame.columnconfigure(0, weight=1)
        self.model_name_var = tk.StringVar()
        self.model_name_combo = ttk.Combobox(model_frame, textvariable=self.model_name_var)
        self.model_name_combo.grid(row=0, column=0, sticky="ew")
        model_btn_frame = ttk.Frame(model_frame)
        model_btn_frame.grid(row=0, column=1, padx=(5,0))
        ttk.Button(model_btn_frame, text="Save", command=self._save_model_name, width=6).pack(side=tk.LEFT, padx=2)
        ttk.Button(model_btn_frame, text="Delete", command=self._delete_model_name, width=6).pack(side=tk.LEFT, padx=2)
        self.test_api_button = ttk.Button(model_btn_frame, text="Test", command=self._test_api_connection, width=6)
        self.test_api_button.pack(side=tk.LEFT, padx=2)
    
        self.azure_settings_frame = ttk.LabelFrame(api_settings_frame, text="Microsoft Azure Settings", padding=5)
        self.azure_settings_frame.grid(row=3, column=0, columnspan=2, sticky="ew", padx=5, pady=10)
        ttk.Label(self.azure_settings_frame, text="Azure Endpoint:").grid(row=0, column=0, sticky="w", padx=5, pady=2)
        self.azure_endpoint_var = tk.StringVar()
        ttk.Entry(self.azure_settings_frame, textvariable=self.azure_endpoint_var).grid(row=0, column=1, sticky="ew", padx=5, pady=2)
        ttk.Label(self.azure_settings_frame, text="API Version:").grid(row=1, column=0, sticky="w", padx=5, pady=2)
        self.api_version_var = tk.StringVar()
        ttk.Entry(self.azure_settings_frame, textvariable=self.api_version_var).grid(row=1, column=1, sticky="ew", padx=5, pady=2)
        ttk.Button(self.azure_settings_frame, text="Save Azure Config", command=self._save_azure_config).grid(row=1, column=2, padx=5, pady=2)
        self.azure_settings_frame.columnconfigure(1, weight=1)
    
        self.process_button = ttk.Button(main_frame, text="Start Processing", command=self._start_processing)
        self.process_button.grid(row=1, column=0, pady=10, ipady=5, sticky="ew")
        
        status_frame = ttk.Frame(self)
        status_frame.pack(side=tk.BOTTOM, fill=tk.X, padx=5, pady=2)
        self.status_label = ttk.Label(status_frame, text="Ready", anchor=tk.W)
        self.status_label.pack(side=tk.LEFT, expand=True, fill=tk.X)
        self.timer_label = ttk.Label(status_frame, text="", anchor=tk.E, width=10)
        self.timer_label.pack(side=tk.RIGHT)
        self._update_status("Ready", "gray")

    def _open_translation_settings(self):
        dialog = tk.Toplevel(self)
        dialog.transient(self)
        dialog.title("Translation Options")
        dialog.grab_set()
        dialog.resizable(False, False)

        content_frame = ttk.Frame(dialog, padding="15")
        content_frame.pack(expand=True, fill="both")

        max_tokens = tk.IntVar(value=self.settings.get("max_tokens", 8000))
        context_before = tk.IntVar(value=self.settings.get("context_before", 1))
        context_after = tk.IntVar(value=self.settings.get("context_after", 1))

        ttk.Label(content_frame, text="Max Tokens:").grid(row=0, column=0, sticky="w", padx=5, pady=5)
        ttk.Entry(content_frame, textvariable=max_tokens, width=15).grid(row=0, column=1, sticky="w", padx=5, pady=5)
        
        ttk.Label(content_frame, text="Previous Paragraphs (Context):").grid(row=1, column=0, sticky="w", padx=5, pady=5)
        ttk.Entry(content_frame, textvariable=context_before, width=15).grid(row=1, column=1, sticky="w", padx=5, pady=5)
        
        ttk.Label(content_frame, text="Next Paragraphs (Context):").grid(row=2, column=0, sticky="w", padx=5, pady=5)
        ttk.Entry(content_frame, textvariable=context_after, width=15).grid(row=2, column=1, sticky="w", padx=5, pady=5)

        def save_and_close():
            try:
                self.settings['max_tokens'] = max_tokens.get()
                self.settings['context_before'] = context_before.get()
                self.settings['context_after'] = context_after.get()
                save_settings(self.settings)
                messagebox.showinfo("Success", "Settings saved.", parent=dialog)
                dialog.destroy()
            except tk.TclError:
                messagebox.showerror("Invalid Input", "Please ensure all values are valid integers.", parent=dialog)

        button_frame = ttk.Frame(dialog, padding="10")
        button_frame.pack(fill="x")
        ttk.Button(button_frame, text="Save", command=save_and_close).pack(side="right", padx=5)
        ttk.Button(button_frame, text="Cancel", command=dialog.destroy).pack(side="right")
    
    def _open_annotator(self):
        if self.annotator_window and self.annotator_window.winfo_exists():
            self.annotator_window.lift()
            self.annotator_window.focus_force()
            return
        self.annotator_window = tk.Toplevel(self)
        app = TermAnnotatorApp(self.annotator_window)
    
    def _open_post_editor(self):
        if self.post_editor_window and self.post_editor_window.winfo_exists():
            self.post_editor_window.lift()
            self.post_editor_window.focus_force()
            return
        self.post_editor_window = PostEditingWindow(self)
    
    def _post_ui_setup(self):
        self._update_prompt_combo()
        if self.settings['prompts']:
            first_prompt_name = list(self.settings['prompts'].keys())[0]
            self.prompt_var.set(first_prompt_name)
            self._on_prompt_select()
        
        self._update_api_provider_combo()
        if self.settings.get('api_providers'):
            first_provider = list(self.settings['api_providers'].keys())[0]
            self.api_provider_var.set(first_provider)
        self._on_provider_select()
    
    def _on_provider_select(self, event=None):
        provider_name = self.api_provider_var.get()
        if provider_name == "Microsoft Azure":
            self.azure_settings_frame.grid()
            provider_config = self.settings["api_providers"].get(provider_name, {})
            self.azure_endpoint_var.set(provider_config.get("azure_endpoint", ""))
            self.api_version_var.set(provider_config.get("api_version", ""))
        else:
            self.azure_settings_frame.grid_remove()
    
        self.api_key_var.set("")
        self.model_name_var.set("")
        self._update_api_key_combo()
        self._update_model_name_combo()
    
    def _save_azure_config(self):
        provider_name = "Microsoft Azure"
        if self.api_provider_var.get() != provider_name:
            return
        
        endpoint = self.azure_endpoint_var.get().strip()
        version = self.api_version_var.get().strip()
    
        self.settings["api_providers"][provider_name]["azure_endpoint"] = endpoint
        self.settings["api_providers"][provider_name]["api_version"] = version
        save_settings(self.settings)
        messagebox.showinfo("Success", "Azure configuration saved.")
    
    def _show_about_info(self):
        messagebox.showinfo(
            "About",
            "Wanyong Wang\n"
            "Email: wangwanyong365@hotmail.com\n\n"
            "Dechao Li\n"
            "Email: ctdechao@polyu.edu.hk\n\n"
            "Department of Language Science and Technology (LST)\n"            
            "The Hong Kong Polytechnic University\n"
            "Kowloon, Hong Kong, China\n"
        )
    
    def _show_license_info(self):
        license_window = tk.Toplevel(self)
        license_window.title("MIT License")
        license_window.geometry("600x500")
        text_area = scrolledtext.ScrolledText(license_window, wrap=tk.WORD, font=("Segoe UI", 10))
        text_area.pack(expand=True, fill="both", padx=10, pady=10)
        mit_license_text = """MIT License

Copyright (c) 2025 Wanyong Wang

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE."""
        text_area.insert(tk.INSERT, mit_license_text)
        text_area.config(state=tk.DISABLED)

    def _get_current_api_key(self):
        displayed_text = self.api_key_var.get().strip()
        provider = self.api_provider_var.get()
        if not provider or not displayed_text:
            return displayed_text
        
        api_keys_for_provider = self.settings['api_providers'].get(provider, {}).get('api_keys', {})
        return api_keys_for_provider.get(displayed_text, displayed_text)
    
    def _update_api_key_combo(self):
        provider = self.api_provider_var.get()
        if not provider:
            self.api_key_combo['values'] = []
            return
        
        keys = self.settings['api_providers'].get(provider, {}).get('api_keys', {})
        self.api_key_combo['values'] = list(keys.keys())
    
    def _on_api_key_select(self, event=None):
        provider = self.api_provider_var.get()
        if not provider: return
        
        selected_name = self.api_key_combo.get()
        api_keys_for_provider = self.settings['api_providers'][provider]['api_keys']
        if selected_name in api_keys_for_provider:
            self.api_key_var.set(selected_name)
            self.api_key_combo.config(show="")
    
    def _on_api_key_typed(self, event=None):
        provider = self.api_provider_var.get()
        if not provider: return
    
        current_text = self.api_key_var.get()
        api_keys_for_provider = self.settings['api_providers'][provider]['api_keys']
        self.api_key_combo.config(show="" if current_text in api_keys_for_provider else "●")
    
    def _save_api_key(self):
        provider = self.api_provider_var.get()
        if not provider:
            return messagebox.showwarning("Warning", "Please select an API Provider first.")
    
        key_or_name = self.api_key_var.get().strip()
        if not key_or_name: return messagebox.showwarning("Warning", "API Key cannot be empty.")
    
        api_keys_for_provider = self.settings['api_providers'][provider]['api_keys']
        if key_or_name in api_keys_for_provider:
            return messagebox.showinfo("Info", "This is a saved API Key name, no need to save again.")
        
        name = simpledialog.askstring("Save API Key", "Please enter an easy-to-remember name for this Key:", parent=self)
        if name and name.strip():
            name = name.strip()
            if name in api_keys_for_provider and not messagebox.askyesno("Confirm Overwrite", f"Name '{name}' already exists. Overwrite with the new Key?"):
                return
            
            api_keys_for_provider[name] = key_or_name
            save_settings(self.settings)
            self._update_api_key_combo()
            self.api_key_combo.set(name)
            self.api_key_combo.config(show="")
            messagebox.showinfo("Success", f"API Key '{name}' has been saved for {provider}.")
    
    def _delete_api_key(self):
        provider = self.api_provider_var.get()
        if not provider:
            return messagebox.showerror("Error", "Please select an API Provider first.")
            
        name = self.api_key_combo.get()
        api_keys_for_provider = self.settings['api_providers'][provider]['api_keys']
    
        if not name or name not in api_keys_for_provider:
             return messagebox.showerror("Error", "Please select a saved API Key to delete first.")
        if messagebox.askyesno("Confirm Deletion", f"Are you sure you want to delete API Key '{name}'?"):
            del api_keys_for_provider[name]
            save_settings(self.settings)
            self._update_api_key_combo()
            self.api_key_var.set("")
            self.api_key_combo.config(show="●")
    
    def _update_model_name_combo(self):
        provider = self.api_provider_var.get()
        if not provider:
            self.model_name_combo['values'] = []
            return
            
        models = self.settings['api_providers'].get(provider, {}).get('model_names', [])
        self.model_name_combo['values'] = models
    
    def _save_model_name(self):
        provider = self.api_provider_var.get()
        if not provider:
            return messagebox.showwarning("Warning", "Please select an API Provider first.")
            
        name = self.model_name_var.get().strip()
        if not name: return messagebox.showwarning("Warning", "Model name cannot be empty.")
        
        model_names_for_provider = self.settings['api_providers'][provider]['model_names']
        if name not in model_names_for_provider:
            model_names_for_provider.append(name)
            save_settings(self.settings)
            self._update_model_name_combo()
            messagebox.showinfo("Success", f"Model '{name}' has been saved for {provider}.")
        else:
            messagebox.showinfo("Info", f"Model '{name}' already exists in the list for {provider}.")
    
    def _delete_model_name(self):
        provider = self.api_provider_var.get()
        if not provider:
            return messagebox.showerror("Error", "Please select an API Provider first.")
    
        name = self.model_name_var.get().strip()
        model_names_for_provider = self.settings['api_providers'][provider]['model_names']
    
        if not name or name not in model_names_for_provider:
             return messagebox.showerror("Error", "The currently entered model name is not in the list.")
        if messagebox.askyesno("Confirm Deletion", f"Are you sure you want to delete model '{name}' from the list?"):
            model_names_for_provider.remove(name)
            save_settings(self.settings)
            self._update_model_name_combo()
            self.model_name_var.set("")
    
    def _create_client(self):
        provider_name = self.api_provider_var.get()
        api_key = self._get_current_api_key()
    
        if not provider_name:
            raise ValueError("API Provider must be selected.")
        if not api_key:
            raise ValueError("API Key is required.")
    
        provider_config = self.settings['api_providers'][provider_name]
    
        if provider_name == "Microsoft Azure":
            azure_endpoint = provider_config.get('azure_endpoint')
            api_version = provider_config.get('api_version')
            if not azure_endpoint or not api_version:
                raise ValueError("Azure Endpoint and API Version must be configured in settings.")
            return openai.AzureOpenAI(
                api_key=api_key,
                azure_endpoint=azure_endpoint,
                api_version=api_version,
            )
        else:
            base_url = provider_config.get('base_url')
            if not base_url:
                raise ValueError(f"Base URL for '{provider_name}' is not configured.")
            return openai.OpenAI(api_key=api_key, base_url=base_url)
    
    def _test_api_connection(self):
        model_name = self.model_name_var.get().strip()
        if not model_name:
            messagebox.showerror("Error", "Model Name is required for the test.", parent=self)
            return
    
        self.test_api_button.config(state=tk.DISABLED)
        messagebox.showinfo("Testing", "Sending a test request... Please wait.", parent=self)
        threading.Thread(target=self._test_api_thread_task, args=(model_name,), daemon=True).start()
    
    def _test_api_thread_task(self, model_name):
        try:
            client = self._create_client()
            response_content = test_api_connection(client, model_name)
            self.after(0, lambda: messagebox.showinfo("Success", f"Connection successful!\n\nModel response: '{response_content}'", parent=self))
        except Exception as e:
            error_message = f"API Test Failed: {e}"
            log_error(error_message)
            self.after(0, lambda: messagebox.showerror("Connection Failed", str(e), parent=self))
        finally:
            self.after(0, lambda: self.test_api_button.config(state=tk.NORMAL))
            
    def _update_api_provider_combo(self):
        self.api_provider_combo['values'] = list(self.settings.get('api_providers', {}).keys())
    
    def _update_prompt_combo(self):
        self.prompt_combo['values'] = list(self.settings['prompts'].keys())
    
    def _on_prompt_select(self, event=None):
        name = self.prompt_var.get()
        if name in self.settings['prompts']:
            self.prompt_text.delete("1.0", tk.END)
            self.prompt_text.insert("1.0", self.settings['prompts'][name])
    
    def _add_prompt(self):
        name = simpledialog.askstring("New Prompt", "Please enter the name for the new Prompt:", parent=self)
        if name and name.strip():
            name = name.strip()
            if name in self.settings['prompts']: return messagebox.showerror("Error", "This name already exists!")
            self.settings['prompts'][name] = f"This is the prompt for '{name}'.\nPlease enter your instructions here, using {{context}} as a placeholder."
            save_settings(self.settings)
            self._update_prompt_combo()
            self.prompt_var.set(name)
            self._on_prompt_select()
    
    def _save_current_prompt(self):
        name = self.prompt_var.get()
        if not name: return messagebox.showerror("Error", "No prompt selected to save.")
        content = self.prompt_text.get("1.0", tk.END).strip()
        if "{context}" not in content and not messagebox.askyesno("Warning", "The placeholder '{context}' was not found in the current prompt.\nThis might prevent the original text and context from being inserted correctly.\nDo you still want to save?"):
            return
        self.settings['prompts'][name] = content
        save_settings(self.settings)
        messagebox.showinfo("Success", f"Prompt '{name}' has been saved.")
    
    def _delete_prompt(self):
        name = self.prompt_var.get()
        if not name: return messagebox.showerror("Error", "Please select a prompt to delete.")
        if len(self.settings['prompts']) <= 1: return messagebox.showwarning("Warning", "You cannot delete the last prompt.")
        if messagebox.askyesno("Confirm Deletion", f"Are you sure you want to delete the prompt '{name}'?"):
            del self.settings['prompts'][name]
            save_settings(self.settings)
            self._update_prompt_combo()
            first_name = list(self.settings['prompts'].keys())[0]
            self.prompt_var.set(first_name)
            self._on_prompt_select()
    
    def _on_browse_files(self):
        files = filedialog.askopenfilenames(title="Please select TXT files", filetypes=[("Text files", "*.txt")])
        if files:
            self.selected_files = list(files)
            self.file_listbox.delete(0, tk.END)
            for file in self.selected_files: self.file_listbox.insert(tk.END, os.path.basename(file))
            self._update_status(f"Selected {len(self.selected_files)} files", "blue")
    
    def _update_status(self, text, color):
        self.status_label.config(text=text, foreground=color)
        self.update_idletasks()
    
    def _update_timer(self, start_time):
        elapsed = time.time() - start_time
        mins, secs = divmod(elapsed, 60)
        self.timer_label.config(text=f"{int(mins):02d}:{secs:04.1f}")
        self.timer_id = self.after(100, self._update_timer, start_time)
    
    def _cancel_timer(self):
        if self.timer_id:
            self.after_cancel(self.timer_id)
            self.timer_id = None
        self.timer_label.config(text="")
    
    def _check_for_resume_task(self):
        if os.path.exists(RESUME_FILE):
            try:
                with open(RESUME_FILE, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                file_name = os.path.basename(data.get('current_file', 'unknown file'))
                paragraph_index = data.get('last_paragraph_index', -1)
                
                if messagebox.askyesno("Unfinished Task Found", 
                                       f"An unfinished task for '{file_name}' (stopped at paragraph {paragraph_index + 1}) was found.\n\nDo you want to resume?"):
                    self._load_resume_state(data)
                else:
                    os.remove(RESUME_FILE)
            except Exception as e:
                log_error(f"Failed to read resume file: {e}")
                os.remove(RESUME_FILE)
    
    def _load_resume_state(self, data):
        self.resume_data = data
        self.selected_files = data.get('all_files', [])
        self.file_listbox.delete(0, tk.END)
        for f in self.selected_files:
            self.file_listbox.insert(tk.END, os.path.basename(f))
        
        self._update_status(f"Ready to resume. {len(self.selected_files)} files loaded.", "blue")
        messagebox.showinfo("Resume Ready", "The previous task has been loaded. Click 'Start Processing' to continue.")
    
    def _save_resume_state(self, current_file, last_index, translated_paras, all_files):
        state = {
            'current_file': current_file,
            'last_paragraph_index': last_index,
            'translated_paragraphs': translated_paras,
            'all_files': all_files
        }
        try:
            with open(RESUME_FILE, 'w', encoding='utf-8') as f:
                json.dump(state, f, indent=4)
        except Exception as e:
            log_error(f"Failed to save resume state: {e}")
    
    def _start_processing(self):
        if not self.selected_files: return messagebox.showerror("Error", "Please select TXT files first.")
        if not self._get_current_api_key(): return messagebox.showerror("Error", "API Key cannot be empty.")
        if not self.model_name_var.get().strip(): return messagebox.showerror("Error", "Model Name cannot be empty.")
        if not self.prompt_text.get("1.0", tk.END).strip(): return messagebox.showerror("Error", "Prompt content cannot be empty.")
    
        self.is_processing = True
        self.stop_requested.clear()
        self.process_button.config(text="Stop Processing", command=self._stop_processing, style="Stop.TButton")
        self._update_status("Processing, please wait...", "orange")
    
        threading.Thread(target=self._processing_task, args=(self.resume_data,), daemon=True).start()
        self.resume_data = None
    
    def _stop_processing(self):
        self.stop_requested.set()
        self._cancel_timer()
        self._update_status("Stopping...", "orange")
    
    def _processing_task(self, resume_data=None):
        try:
            model_name = self.model_name_var.get().strip()
            user_prompt_template = self.prompt_text.get("1.0", tk.END).strip()
            context_before = self.settings.get('context_before', 1)
            context_after = self.settings.get('context_after', 1)
            max_tokens_value = self.settings.get('max_tokens', 8000)
    
            client = self._create_client()
    
            total_files = len(self.selected_files)
            start_file_index = 0
            if resume_data:
                try:
                    start_file_index = self.selected_files.index(resume_data.get('current_file'))
                except ValueError:
                    log_error(f"Resumed file '{resume_data.get('current_file')}' not found in selection.")
    
            for i in range(start_file_index, total_files):
                file_path = self.selected_files[i]
                file_name = os.path.basename(file_path)
                dir_name = os.path.splitext(file_name)[0]
                output_dir = os.path.join(os.path.dirname(file_path), dir_name)
                os.makedirs(output_dir, exist_ok=True)
                
                self.after(0, self._update_status, f"[{i+1}/{total_files}] Reading: {file_name}", "orange")
    
                with open(file_path, 'r', encoding='utf-8') as f: original_text = f.read()
                
                paragraphs = split_text_into_paragraphs(original_text)
                if not paragraphs:
                    log_error(f"File {file_name} is empty or contains no valid paragraphs, skipped.")
                    continue
    
                translated_paragraphs, total_paragraphs = [], len(paragraphs)
                start_paragraph_index = 0
    
                if resume_data and file_path == resume_data.get('current_file'):
                    start_paragraph_index = resume_data.get('last_paragraph_index', -1) + 1
                    translated_paragraphs = resume_data.get('translated_paragraphs', [])
                    resume_data = None
                
                for j in range(start_paragraph_index, total_paragraphs):
                    if self.stop_requested.is_set():
                        self._save_resume_state(file_path, j - 1, translated_paragraphs, self.selected_files)
                        self.after(0, self._update_status, f"Processing stopped. Progress for '{file_name}' saved.", "blue")
                        return
    
                    self.after(0, self._update_status, f"[{i+1}/{total_files}] Translating {file_name} paragraph ({j+1}/{total_paragraphs})", "orange")
                    
                    start_time = time.time()
                    self.after(0, self._update_timer, start_time)
    
                    context_parts = []
                    start = max(0, j - context_before)
                    if start < j: context_parts.extend(["[Previous Context]"] + paragraphs[start:j] + [""])
                    
                    context_parts.extend(["[Text to Translate]", paragraphs[j]])
                    
                    end = min(total_paragraphs, j + 1 + context_after)
                    if j + 1 < end: context_parts.extend(["\n[Next Context]"] + paragraphs[j+1:end])
    
                    full_prompt = user_prompt_template.format(context="\n".join(context_parts))
                    translated_para = translate_single_paragraph(client, model_name, full_prompt, max_tokens_value)
                    
                    self.after(0, self._cancel_timer)
                    translated_paragraphs.append(translated_para)
    
                full_translated_text = "\n\n".join(translated_paragraphs)
                translated_file_path = os.path.join(output_dir, f"{dir_name}_translated.txt")
                with open(translated_file_path, 'w', encoding='utf-8') as f: f.write(full_translated_text)
    
                self.after(0, self._update_status, f"[{i+1}/{total_files}] Generating Excel file...", "orange")
                df = pd.DataFrame({'Source': paragraphs, 'Translation': translated_paragraphs})
                df.to_excel(os.path.join(output_dir, f"{dir_name}_corpus.xlsx"), index=False, engine='openpyxl')
    
            if os.path.exists(RESUME_FILE):
                os.remove(RESUME_FILE)
    
            save_settings(self.settings)
    
            self.after(0, self._update_status, "Processing complete! All files have been saved in their respective folders.", "green")
    
        except Exception as e:
            error_message = f"Processing failed: {e}"
            log_error(f"A critical error occurred, processing interrupted. Error: {e}")
            self.after(0, self._update_status, error_message, "red")
            self.after(0, messagebox.showerror, "An Error Occurred", f"{e}\n\nDetailed information has been logged to error_log.txt")
        
        finally:
            self.is_processing = False
            self.after(0, lambda: self.process_button.config(text="Start Processing", command=self._start_processing, style="TButton"))
            self.after(0, self._cancel_timer)

if __name__ == "__main__":
    app = TranslationApp()
    app.mainloop()