import os
import threading
import tkinter as tk
from tkinter import ttk, filedialog, messagebox, simpledialog, scrolledtext

import openai
import pandas as pd

from app_utils import load_settings, save_settings, log_error, split_text_into_paragraphs, translate_single_paragraph
from ui_tools import TermAnnotatorApp, PostEditingWindow


class TranslationApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.settings = load_settings()
        self.selected_files = []
        self.annotator_window = None
        self.post_editor_window = None
    
        self._setup_style()
        self._setup_ui()
        self._post_ui_setup()
        
        self.protocol("WM_DELETE_WINDOW", self._on_closing)
    
    def _on_closing(self):
        self.settings['max_tokens'] = self.max_tokens_var.get()
        self.settings['context_before'] = self.context_before_var.get()
        self.settings['context_after'] = self.context_after_var.get()
        save_settings(self.settings)
        self.destroy()
    
    def _setup_style(self):
        self.style = ttk.Style(self)
        self.style.theme_use("clam")
        self.style.configure("Accent.TButton", font=("Segoe UI", 12, "bold"), padding=(10, 5))
        self.style.map("Accent.TButton", background=[("active", "#005f9e"), ("!disabled", "#0078d4")], foreground=[("!disabled", "white")])
        self.style.configure("TLabelFrame.Label", font=("Segoe UI", 11, "bold"))
    
    def _setup_ui(self):
        self.title("AI-Powered Translation Aligner (AI-PTA) v0.9")
        self.geometry("800x850") 
        self.minsize(600, 700)
    
        self.menu_bar = tk.Menu(self)
        self.config(menu=self.menu_bar)
        
        tools_menu = tk.Menu(self.menu_bar, tearoff=0)
        self.menu_bar.add_cascade(label="Tools", menu=tools_menu)
        tools_menu.add_command(label="Term Annotator", command=self._open_annotator)
        tools_menu.add_command(label="Post-editing", command=self._open_post_editor)
    
        help_menu = tk.Menu(self.menu_bar, tearoff=0)
        self.menu_bar.add_cascade(label="Help", menu=help_menu)
        help_menu.add_command(label="About", command=self._show_about_info)
        help_menu.add_command(label="View License", command=self._show_license_info)
    
        main_frame = ttk.Frame(self, padding="10 10 10 10")
        main_frame.pack(expand=True, fill=tk.BOTH)
        
        main_frame.columnconfigure(0, weight=1)
        main_frame.rowconfigure(2, weight=1)
    
        files_frame = ttk.LabelFrame(main_frame, text="File Selection", padding="10")
        files_frame.grid(row=0, column=0, sticky="ew", pady=(0, 10))
        files_frame.columnconfigure(0, weight=1)
        self.file_listbox = tk.Listbox(files_frame, height=5, font=("Segoe UI", 10))
        self.file_listbox.grid(row=0, column=0, sticky="ew")
        scrollbar = ttk.Scrollbar(files_frame, orient=tk.VERTICAL, command=self.file_listbox.yview)
        scrollbar.grid(row=0, column=1, sticky="ns")
        self.file_listbox.config(yscrollcommand=scrollbar.set)
        browse_button = ttk.Button(files_frame, text="Select TXT Files...", command=self._on_browse_files)
        browse_button.grid(row=1, column=0, columnspan=2, pady=(10, 0), sticky="e")
    
        settings_frame = ttk.LabelFrame(main_frame, text="Settings", padding="10")
        settings_frame.grid(row=1, column=0, sticky="ew", pady=5)
        settings_frame.columnconfigure(1, weight=1)
        settings_frame.columnconfigure(3, weight=1) 
    
        ttk.Label(settings_frame, text="Max Tokens:").grid(row=0, column=0, sticky="w", padx=5, pady=5)
        self.max_tokens_var = tk.IntVar(value=self.settings.get("max_tokens", 8000))
        ttk.Entry(settings_frame, textvariable=self.max_tokens_var, width=10).grid(row=0, column=1, sticky="w", padx=5, pady=5)
    
        ttk.Label(settings_frame, text="Previous Paragraphs:").grid(row=1, column=0, sticky="w", padx=5, pady=5)
        self.context_before_var = tk.IntVar(value=self.settings.get("context_before", 1))
        ttk.Entry(settings_frame, textvariable=self.context_before_var, width=10).grid(row=1, column=1, sticky="w", padx=5, pady=5)
        
        ttk.Label(settings_frame, text="Next Paragraphs:").grid(row=1, column=2, sticky="w", padx=20, pady=5)
        self.context_after_var = tk.IntVar(value=self.settings.get("context_after", 1))
        ttk.Entry(settings_frame, textvariable=self.context_after_var, width=10).grid(row=1, column=3, sticky="w", padx=5, pady=5)
    
        ttk.Label(settings_frame, text="API Provider:").grid(row=2, column=0, sticky="w", padx=5, pady=5)
        provider_frame = ttk.Frame(settings_frame)
        provider_frame.grid(row=2, column=1, columnspan=3, sticky="ew", padx=5, pady=5)
        provider_frame.columnconfigure(0, weight=1)
        self.api_provider_var = tk.StringVar()
        self.api_provider_combo = ttk.Combobox(provider_frame, textvariable=self.api_provider_var)
        self.api_provider_combo.grid(row=0, column=0, sticky="ew")
        provider_btn_frame = ttk.Frame(provider_frame)
        provider_btn_frame.grid(row=0, column=1, padx=(5,0))
        ttk.Button(provider_btn_frame, text="Save", command=self._save_api_provider, width=6).pack(side=tk.LEFT, padx=2)
        ttk.Button(provider_btn_frame, text="Delete", command=self._delete_api_provider, width=6).pack(side=tk.LEFT, padx=2)
    
        ttk.Label(settings_frame, text="API Key:").grid(row=3, column=0, sticky="w", padx=5, pady=5)
        api_key_frame = ttk.Frame(settings_frame)
        api_key_frame.grid(row=3, column=1, columnspan=3, sticky="ew", padx=5, pady=5)
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
    
        ttk.Label(settings_frame, text="Model Name:").grid(row=4, column=0, sticky="w", padx=5, pady=5)
        model_frame = ttk.Frame(settings_frame)
        model_frame.grid(row=4, column=1, columnspan=3, sticky="ew", padx=5, pady=5)
        model_frame.columnconfigure(0, weight=1)
        self.model_name_var = tk.StringVar()
        self.model_name_combo = ttk.Combobox(model_frame, textvariable=self.model_name_var)
        self.model_name_combo.grid(row=0, column=0, sticky="ew")
        model_btn_frame = ttk.Frame(model_frame)
        model_btn_frame.grid(row=0, column=1, padx=(5,0))
        ttk.Button(model_btn_frame, text="Save", command=self._save_model_name, width=6).pack(side=tk.LEFT, padx=2)
        ttk.Button(model_btn_frame, text="Delete", command=self._delete_model_name, width=6).pack(side=tk.LEFT, padx=2)
    
        prompt_frame = ttk.LabelFrame(main_frame, text="Prompt Management", padding="10")
        prompt_frame.grid(row=2, column=0, sticky="nsew", pady=5)
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
    
        self.start_button = ttk.Button(main_frame, text="Start Processing", style="Accent.TButton", command=self._start_processing)
        self.start_button.grid(row=3, column=0, pady=10, ipady=5, sticky="ew")
        
        self.status_label = ttk.Label(self, text="Ready", padding="5 2", anchor=tk.W)
        self.status_label.pack(side=tk.BOTTOM, fill=tk.X)
        self._update_status("Ready", "gray")
    
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
        
        self._update_api_key_combo()
        self._update_model_name_combo()
        self._update_api_provider_combo()
        if self.settings['model_names']:
            self.model_name_var.set(self.settings['model_names'][0])
        if self.settings.get('api_providers'):
            first_provider = list(self.settings['api_providers'].keys())[0]
            self.api_provider_var.set(first_provider)
    
    def _show_about_info(self):
        messagebox.showinfo(
            "About",
            "王万涌\n"
            "Wanyong Wang\n"
            "Email: wangwanyong365@hotmail.com\n\n"
            "李德超\n"
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

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
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
        return self.settings['api_keys'].get(displayed_text, displayed_text)
    
    def _update_api_key_combo(self):
        self.api_key_combo['values'] = list(self.settings['api_keys'].keys())
    
    def _on_api_key_select(self, event=None):
        selected_name = self.api_key_combo.get()
        if selected_name in self.settings['api_keys']:
            self.api_key_var.set(selected_name)
            self.api_key_combo.config(show="")
    
    def _on_api_key_typed(self, event=None):
        current_text = self.api_key_var.get()
        self.api_key_combo.config(show="" if current_text in self.settings['api_keys'] else "●")
    
    def _save_api_key(self):
        key_or_name = self.api_key_var.get().strip()
        if not key_or_name: return messagebox.showwarning("Warning", "API Key cannot be empty.")
        if key_or_name in self.settings['api_keys']: return messagebox.showinfo("Info", "This is a saved API Key name, no need to save again.")
        
        name = simpledialog.askstring("Save API Key", "Please enter an easy-to-remember name for this Key:", parent=self)
        if name and name.strip():
            name = name.strip()
            if name in self.settings['api_keys'] and not messagebox.askyesno("Confirm Overwrite", f"Name '{name}' already exists. Overwrite with the new Key?"):
                return
            self.settings['api_keys'][name] = key_or_name
            save_settings(self.settings)
            self._update_api_key_combo()
            self.api_key_combo.set(name)
            self.api_key_combo.config(show="")
            messagebox.showinfo("Success", f"API Key '{name}' has been saved.")
    
    def _delete_api_key(self):
        name = self.api_key_combo.get()
        if not name or name not in self.settings['api_keys']: return messagebox.showerror("Error", "Please select an API Key to delete first.")
        if messagebox.askyesno("Confirm Deletion", f"Are you sure you want to delete API Key '{name}'?"):
            del self.settings['api_keys'][name]
            save_settings(self.settings)
            self._update_api_key_combo()
            self.api_key_var.set("")
            self.api_key_combo.config(show="●")
    
    def _update_model_name_combo(self):
        self.model_name_combo['values'] = self.settings.get('model_names', [])
    
    def _save_model_name(self):
        name = self.model_name_var.get().strip()
        if not name: return messagebox.showwarning("Warning", "Model name cannot be empty.")
        if name not in self.settings['model_names']:
            self.settings['model_names'].append(name)
            save_settings(self.settings)
            self._update_model_name_combo()
            messagebox.showinfo("Success", f"Model '{name}' has been saved to the list.")
        else:
            messagebox.showinfo("Info", f"Model '{name}' already exists in the list.")
    
    def _delete_model_name(self):
        name = self.model_name_var.get().strip()
        if not name or name not in self.settings['model_names']: return messagebox.showerror("Error", "The currently entered model name is not in the list.")
        if messagebox.askyesno("Confirm Deletion", f"Are you sure you want to delete model '{name}' from the list?"):
            self.settings['model_names'].remove(name)
            save_settings(self.settings)
            self._update_model_name_combo()
            self.model_name_var.set("")
            
    def _update_api_provider_combo(self):
        self.api_provider_combo['values'] = list(self.settings.get('api_providers', {}).keys())
    
    def _save_api_provider(self):
        url = self.api_provider_var.get().strip()
        if not url:
            messagebox.showwarning("Warning", "API Provider URL cannot be empty.", parent=self)
            return
    
        if url in self.settings['api_providers']:
            messagebox.showinfo("Info", f"'{url}' is already a saved provider name. To add a new one, please enter its full URL in the box.", parent=self)
            return
    
        if not url.startswith(("http://", "https://")):
            messagebox.showwarning("Invalid URL", "Please enter a valid URL, starting with 'http://' or 'https://'.", parent=self)
            return
    
        name = simpledialog.askstring("Save API Provider", "Please enter a name for this provider (e.g., SiliconFlow):", parent=self)
        if not (name and name.strip()):
            return
    
        name = name.strip()
        if name in self.settings['api_providers']:
            if not messagebox.askyesno("Confirm Overwrite", f"The name '{name}' already exists. Do you want to update its URL?", parent=self):
                return
        
        self.settings['api_providers'][name] = url
        save_settings(self.settings)
        
        self._update_api_provider_combo()
        self.api_provider_var.set(name)
        messagebox.showinfo("Success", f"API Provider '{name}' has been saved.", parent=self)
    
    def _delete_api_provider(self):
        name = self.api_provider_var.get().strip()
        if not name or name not in self.settings['api_providers']:
            return messagebox.showerror("Error", "Please select a saved API Provider to delete.")
        if messagebox.askyesno("Confirm Deletion", f"Are you sure you want to delete API Provider '{name}'?"):
            del self.settings['api_providers'][name]
            save_settings(self.settings)
            self._update_api_provider_combo()
            self.api_provider_var.set("")
    
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
    
    def _start_processing(self):
        if not self.selected_files: return messagebox.showerror("Error", "Please select TXT files first.")
        if not self._get_current_api_key(): return messagebox.showerror("Error", "API Key cannot be empty.")
        if not self.prompt_text.get("1.0", tk.END).strip(): return messagebox.showerror("Error", "Prompt content cannot be empty.")
    
        self.start_button.config(state=tk.DISABLED)
        self._update_status("Processing, please wait...", "orange")
    
        threading.Thread(target=self._processing_task, daemon=True).start()
    
    def _processing_task(self):
        try:
            provider_name = self.api_provider_var.get()
            api_key = self._get_current_api_key()
            model_name = self.model_name_var.get().strip() or "deepseek-chat"
            base_url = self.settings['api_providers'].get(provider_name)
            if not base_url:
                self.after(0, messagebox.showerror, "Error", f"Could not find the URL for API Provider '{provider_name}'.\nPlease check your settings.")
                raise ValueError(f"Provider URL not found for '{provider_name}'")
            user_prompt_template = self.prompt_text.get("1.0", tk.END).strip()
            context_before = self.context_before_var.get()
            context_after = self.context_after_var.get()
            max_tokens_value = self.max_tokens_var.get()
    
            client = openai.OpenAI(api_key=api_key, base_url=base_url)
    
            total_files = len(self.selected_files)
            for i, file_path in enumerate(self.selected_files):
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
                
                for j, para in enumerate(paragraphs):
                    self.after(0, self._update_status, f"[{i+1}/{total_files}] Translating {file_name} paragraph ({j+1}/{total_paragraphs})", "orange")
                    
                    context_parts = []
                    start = max(0, j - context_before)
                    if start < j:
                        context_parts.extend(["[Previous Context]"] + paragraphs[start:j] + [""])
                    
                    context_parts.extend(["[Text to Translate]", para])
                    
                    end = min(total_paragraphs, j + 1 + context_after)
                    if j + 1 < end:
                        context_parts.extend(["\n[Next Context]"] + paragraphs[j+1:end])
    
                    full_prompt = user_prompt_template.format(context="\n".join(context_parts))
                    translated_para = translate_single_paragraph(client, model_name, full_prompt, max_tokens_value)
                    translated_paragraphs.append(translated_para)
    
                full_translated_text = "\n\n".join(translated_paragraphs)
                translated_file_path = os.path.join(output_dir, f"{dir_name}_translated.txt")
                with open(translated_file_path, 'w', encoding='utf-8') as f: f.write(full_translated_text)
    
                self.after(0, self._update_status, f"[{i+1}/{total_files}] Generating Excel file...", "orange")
                df = pd.DataFrame({'Source': paragraphs, 'Translation': translated_paragraphs})
                df.to_excel(os.path.join(output_dir, f"{dir_name}_corpus.xlsx"), index=False, engine='openpyxl')
    
            self.settings['max_tokens'] = self.max_tokens_var.get()
            self.settings['context_before'] = self.context_before_var.get()
            self.settings['context_after'] = self.context_after_var.get()
            save_settings(self.settings)
    
            self.after(0, self._update_status, "Processing complete! All files have been saved in their respective folders.", "green")
    
        except Exception as e:
            error_message = f"Processing failed: {e}"
            log_error(f"A critical error occurred, processing interrupted. Error: {e}")
            self.after(0, self._update_status, error_message, "red")
            self.after(0, messagebox.showerror, "An Error Occurred", f"{e}\n\nDetailed information has been logged to error_log.txt")
        
        finally:
            self.after(0, lambda: self.start_button.config(state=tk.NORMAL))

if __name__ == "__main__":
    app = TranslationApp()
    app.mainloop()