import os
import re
import csv
import json
import threading
import datetime
import traceback
import tkinter as tk
from tkinter import ttk, filedialog, messagebox, simpledialog, scrolledtext

import openai
import pandas as pd



class TermEditDialog(tk.Toplevel):

    def __init__(self, parent, title, source_term="", target_term=""):
        super().__init__(parent)
        self.transient(parent)
        self.title(title)
        self.parent = parent
        self.result = None
    
        body = ttk.Frame(self)
        self.initial_focus = self._create_widgets(body, source_term, target_term)
        body.pack(padx=15, pady=15)
    
        self._create_buttons()
    
        self.grab_set()
        if not self.initial_focus:
            self.initial_focus = self
    
        self.protocol("WM_DELETE_WINDOW", self._cancel)
        self.geometry(f"+{parent.winfo_rootx()+50}+{parent.winfo_rooty()+50}")
        self.initial_focus.focus_set()
        self.wait_window(self)
    
    def _create_widgets(self, master, source_term, target_term):
        ttk.Label(master, text="Source Term:").grid(row=0, column=0, sticky="w", padx=5, pady=5)
        self.source_entry = ttk.Entry(master, width=30)
        self.source_entry.grid(row=0, column=1, sticky="ew", padx=5, pady=5)
        self.source_entry.insert(0, source_term)
    
        ttk.Label(master, text="Target Term:").grid(row=1, column=0, sticky="w", padx=5, pady=5)
        self.target_entry = ttk.Entry(master, width=30)
        self.target_entry.grid(row=1, column=1, sticky="ew", padx=5, pady=5)
        self.target_entry.insert(0, target_term)
        
        return self.source_entry
    
    def _create_buttons(self):
        button_frame = ttk.Frame(self)
        
        ok_button = ttk.Button(button_frame, text="OK", command=self._ok, style="Accent.TButton")
        ok_button.pack(side="left", padx=5, pady=5)
        
        cancel_button = ttk.Button(button_frame, text="Cancel", command=self._cancel)
        cancel_button.pack(side="left", padx=5, pady=5)
        
        button_frame.pack()
        
        self.bind("<Return>", self._ok)
        self.bind("<Escape>", self._cancel)
    
    def _ok(self, event=None):
        source = self.source_entry.get().strip()
        target = self.target_entry.get().strip()
        if not source or not target:
            messagebox.showwarning("Input Error", "Source term and target term cannot be empty.", parent=self)
            return
    
        self.result = (source, target)
        self.destroy()
    
    def _cancel(self, event=None):
        self.destroy()

class TermAnnotatorApp:

    def __init__(self, root):
        self.root = root
        self.current_terms = {}
        self.source_file_path = tk.StringVar()
    
        self._setup_window()
        self._setup_styles()
        self._create_widgets()
        self._load_terminologies()
    
    def _setup_window(self):
        self.root.title("Source Text Term Annotator")
        self.root.geometry("1000x700")
        self.root.minsize(800, 600)
        self.root.protocol("WM_DELETE_WINDOW", self._on_closing)
    
    def _setup_styles(self):
        self.style = ttk.Style(self.root)
        self.style.theme_use("clam")
        self.title_font = ("Segoe UI", 12, "bold")
        self.default_font = ("Segoe UI", 10)
        self.status_font = ("Segoe UI", 9)
        self.accent_font = ("Segoe UI", 11, "bold")
        self.style.configure("TLabel", font=self.default_font)
        self.style.configure("TButton", font=self.default_font, padding=5)
        self.style.configure("TEntry", font=self.default_font)
        self.style.configure("TCombobox", font=self.default_font)
        self.style.configure("TLabelframe", font=self.default_font, padding=10)
        self.style.configure("TLabelframe.Label", font=self.title_font, foreground="#333")
        self.style.configure("Accent.TButton", font=self.accent_font, padding=(10, 8), background="#0078D7", foreground="white")
        self.style.map("Accent.TButton", background=[("active", "#005a9e"), ("pressed", "#004578"), ("disabled", "#a0a0a0")])
        self.style.configure("Status.TLabel", font=self.status_font, padding=5)
        self.style.configure("Ready.Status.TLabel", foreground="gray")
        self.style.configure("Info.Status.TLabel", foreground="blue")
        self.style.configure("Processing.Status.TLabel", foreground="orange")
        self.style.configure("Success.Status.TLabel", foreground="green")
        self.style.configure("Error.Status.TLabel", foreground="red")
    
    def _create_widgets(self):
        main_frame = ttk.Frame(self.root, padding=10)
        main_frame.pack(expand=True, fill=tk.BOTH)
        main_frame.rowconfigure(1, weight=1)
        main_frame.columnconfigure(0, weight=1)
    
        top_controls_frame = self._create_top_controls(main_frame)
        top_controls_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
    
        text_area_frame = self._create_text_areas(main_frame)
        text_area_frame.grid(row=1, column=0, sticky="nsew")
    
        bottom_frame = ttk.Frame(main_frame)
        bottom_frame.grid(row=2, column=0, sticky=(tk.W, tk.E), pady=(10, 0))
        bottom_frame.columnconfigure(0, weight=1)
    
        self.annotate_button = ttk.Button(
            bottom_frame, text="Start Annotation", style="Accent.TButton", command=self._start_annotation
        )
        self.annotate_button.grid(row=0, column=0, columnspan=2, sticky=(tk.W, tk.E), ipady=5)
    
        self.status_label = ttk.Label(
            main_frame, text="Ready", anchor=tk.W, style="Ready.Status.TLabel"
        )
        self.status_label.grid(row=3, column=0, sticky=(tk.W, tk.E), pady=(10, 0))
    
    def _create_top_controls(self, parent):
        frame = ttk.LabelFrame(parent, text="Settings")
        frame.columnconfigure(1, weight=1)
    
        ttk.Label(frame, text="Select Terminology:").grid(row=0, column=0, padx=5, pady=5, sticky=tk.W)
        self.term_db_combo = ttk.Combobox(frame, state="readonly", font=self.default_font)
        self.term_db_combo.grid(row=0, column=1, padx=5, pady=5, sticky=(tk.W, tk.E))
        self.term_db_combo.bind("<<ComboboxSelected>>", self._on_term_db_selected)
    
        ttk.Label(frame, text="Current Terms:").grid(row=1, column=0, padx=5, pady=5, sticky=(tk.W, tk.N))
        term_list_frame = ttk.Frame(frame)
        term_list_frame.grid(row=1, column=1, rowspan=2, padx=5, pady=5, sticky="nsew")
        term_list_frame.rowconfigure(0, weight=1)
        term_list_frame.columnconfigure(0, weight=1)
        
        self.term_listbox = tk.Listbox(term_list_frame, font=self.default_font, height=5)
        self.term_listbox.grid(row=0, column=0, sticky="nsew")
        
        scrollbar = ttk.Scrollbar(term_list_frame, orient=tk.VERTICAL, command=self.term_listbox.yview)
        scrollbar.grid(row=0, column=1, sticky="ns")
        self.term_listbox.config(yscrollcommand=scrollbar.set)
        
        frame.rowconfigure(1, weight=1)
    
        term_actions_frame = ttk.Frame(frame)
        term_actions_frame.grid(row=2, column=0, padx=5, pady=5, sticky=tk.W)
        self.add_term_button = ttk.Button(term_actions_frame, text="Add", command=self._add_term, state=tk.DISABLED)
        self.add_term_button.pack(side=tk.LEFT, padx=(0, 5))
        self.modify_term_button = ttk.Button(term_actions_frame, text="Modify", command=self._modify_term, state=tk.DISABLED)
        self.modify_term_button.pack(side=tk.LEFT, padx=(0, 5))
        self.delete_term_button = ttk.Button(term_actions_frame, text="Delete", command=self._delete_term, state=tk.DISABLED)
        self.delete_term_button.pack(side=tk.LEFT)
    
        ttk.Label(frame, text="Select Source File:").grid(row=3, column=0, padx=5, pady=5, sticky=tk.W)
        entry = ttk.Entry(frame, textvariable=self.source_file_path, state="readonly")
        entry.grid(row=3, column=1, padx=5, pady=5, sticky=(tk.W, tk.E))
        browse_button = ttk.Button(frame, text="Browse...", command=self._browse_source_file)
        browse_button.grid(row=3, column=2, padx=5, pady=5, sticky=tk.E)
    
        return frame
    
    def _create_text_areas(self, parent):
        frame = ttk.LabelFrame(parent, text="Text Content")
        frame.rowconfigure(1, weight=1)
        frame.columnconfigure(0, weight=1)
        frame.columnconfigure(1, weight=1)
    
        ttk.Label(frame, text="Source Text", font=self.title_font).grid(row=0, column=0, padx=5, pady=5)
        source_text_frame = ttk.Frame(frame)
        source_text_frame.grid(row=1, column=0, sticky="nsew", padx=(0, 5))
        source_text_frame.rowconfigure(0, weight=1)
        source_text_frame.columnconfigure(0, weight=1)
        
        self.source_text = tk.Text(source_text_frame, wrap=tk.WORD, font=self.default_font, undo=True)
        self.source_text.grid(row=0, column=0, sticky="nsew")
        source_scrollbar = ttk.Scrollbar(source_text_frame, orient=tk.VERTICAL, command=self.source_text.yview)
        source_scrollbar.grid(row=0, column=1, sticky="ns")
        self.source_text.config(yscrollcommand=source_scrollbar.set)
    
        ttk.Label(frame, text="Annotated Text", font=self.title_font).grid(row=0, column=1, padx=5, pady=5)
        annotated_text_frame = ttk.Frame(frame)
        annotated_text_frame.grid(row=1, column=1, sticky="nsew", padx=(5, 0))
        annotated_text_frame.rowconfigure(0, weight=1)
        annotated_text_frame.columnconfigure(0, weight=1)
    
        self.annotated_text = tk.Text(annotated_text_frame, wrap=tk.WORD, font=self.default_font, undo=True, state=tk.DISABLED)
        self.annotated_text.grid(row=0, column=0, sticky="nsew")
        annotated_scrollbar = ttk.Scrollbar(annotated_text_frame, orient=tk.VERTICAL, command=self.annotated_text.yview)
        annotated_scrollbar.grid(row=0, column=1, sticky="ns")
        self.annotated_text.config(yscrollcommand=annotated_scrollbar.set)
        
        export_button = ttk.Button(frame, text="Export as .txt", command=self._export_annotated_text)
        export_button.grid(row=2, column=1, sticky=tk.E, padx=5, pady=(10, 0))
    
        return frame
    
    def _update_status(self, text, level="info"):
        style_map = {
            "ready": "Ready.Status.TLabel", "info": "Info.Status.TLabel",
            "processing": "Processing.Status.TLabel", "success": "Success.Status.TLabel",
            "error": "Error.Status.TLabel"
        }
        self.status_label.config(text=text, style=style_map.get(level.lower(), "Info.Status.TLabel"))
        self.root.update_idletasks()
    
    def _load_terminologies(self):
        term_dir = "terminology"
        if not os.path.exists(term_dir):
            os.makedirs(term_dir)
            messagebox.showinfo("Info", f"The 'terminology' folder has been created.\nPlease put your CSV terminology files in it.", parent=self.root)
            self._update_status("Terminology folder created. Please add files.", level="info")
            return
    
        try:
            csv_files = [f for f in os.listdir(term_dir) if f.endswith('.csv')]
            self.term_db_combo['values'] = csv_files
            if csv_files:
                self.term_db_combo.current(0)
                self._on_term_db_selected(None)
                self._update_status(f"Loaded {len(csv_files)} terminologies.", level="info")
            else:
                self._update_status("No .csv files found in the 'terminology' folder.", level="error")
        except Exception as e:
            messagebox.showerror("Error", f"Error loading terminologies: {e}", parent=self.root)
            self._update_status(f"Failed to load terminologies: {e}", level="error")
    
    def _on_term_db_selected(self, event):
        filename = self.term_db_combo.get()
        if not filename: return
        
        filepath = os.path.join("terminology", filename)
        self.current_terms = {}
        self.term_listbox.delete(0, tk.END)
    
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                reader = csv.reader(f)
                for i, row in enumerate(reader):
                    if len(row) >= 2 and row[0] and row[1]:
                        source_term, target_term = row[0].strip(), row[1].strip()
                        self.current_terms[source_term] = target_term
                    else:
                        print(f"Warning: Skipping invalid row {i+1} in file '{filename}': {row}")
            self._update_term_listbox()
            self._update_status(f"Successfully loaded terminology '{filename}' with {len(self.current_terms)} terms.", level="success")
            for btn in [self.add_term_button, self.modify_term_button, self.delete_term_button]:
                btn.config(state=tk.NORMAL)
        except FileNotFoundError:
            messagebox.showerror("Error", f"File '{filename}' not found.", parent=self.root)
            self._update_status(f"File not found: {filename}", level="error")
        except Exception as e:
            messagebox.showerror("Error", f"Error reading file '{filename}': {e}", parent=self.root)
            self._update_status(f"Failed to read file '{filename}'", level="error")
    
    def _update_term_listbox(self):
        self.term_listbox.delete(0, tk.END)
        for source, target in sorted(self.current_terms.items()):
            self.term_listbox.insert(tk.END, f"{source} → {target}")
    
    def _save_current_terms(self):
        filename = self.term_db_combo.get()
        if not filename:
            self._update_status("Error: No terminology file selected for saving.", level="error")
            return False
        
        filepath = os.path.join("terminology", filename)
        try:
            with open(filepath, 'w', encoding='utf-8', newline='') as f:
                writer = csv.writer(f)
                for source, target in sorted(self.current_terms.items()):
                    writer.writerow([source, target])
            self._update_status(f"Terminology '{filename}' saved automatically.", level="success")
            return True
        except Exception as e:
            messagebox.showerror("Save Failed", f"Could not save terminology '{filename}':\n{e}", parent=self.root)
            self._update_status(f"Failed to save terminology: {e}", level="error")
            return False
    
    def _add_term(self):
        dialog = TermEditDialog(self.root, "Add New Term")
        if dialog.result:
            source, target = dialog.result
            if source in self.current_terms:
                if not messagebox.askyesno("Term Exists", f"Source term '{source}' already exists. Do you want to overwrite it?", parent=self.root):
                    return
            
            self.current_terms[source] = target
            if self._save_current_terms():
                self._update_term_listbox()
                self._update_status(f"Added term: {source} → {target}", level="success")
    
    def _modify_term(self):
        selected_indices = self.term_listbox.curselection()
        if not selected_indices:
            messagebox.showwarning("Invalid Operation", "Please select a term to modify from the list first.", parent=self.root)
            return
    
        selected_item = self.term_listbox.get(selected_indices[0])
        try:
            old_source, old_target = [s.strip() for s in selected_item.split('→')]
        except ValueError:
            messagebox.showerror("Format Error", "Could not parse the selected term line.", parent=self.root)
            return
    
        dialog = TermEditDialog(self.root, "Modify Term", old_source, old_target)
        if dialog.result:
            new_source, new_target = dialog.result
            del self.current_terms[old_source]
            self.current_terms[new_source] = new_target
            
            if self._save_current_terms():
                self._update_term_listbox()
                self._update_status(f"Modified term: {new_source} → {new_target}", level="success")
            else:
                del self.current_terms[new_source]
                self.current_terms[old_source] = old_target
    
    def _delete_term(self):
        selected_indices = self.term_listbox.curselection()
        if not selected_indices:
            messagebox.showwarning("Invalid Operation", "Please select a term to delete from the list first.", parent=self.root)
            return
            
        selected_item = self.term_listbox.get(selected_indices[0])
        if messagebox.askyesno("Confirm Deletion", f"Are you sure you want to delete the following term?\n\n{selected_item}", parent=self.root):
            try:
                source_to_delete = selected_item.split('→')[0].strip()
                if source_to_delete in self.current_terms:
                    del self.current_terms[source_to_delete]
                    if self._save_current_terms():
                        self._update_term_listbox()
                        self._update_status(f"Deleted term: {source_to_delete}", level="success")
            except Exception as e:
                messagebox.showerror("Deletion Failed", f"An error occurred during deletion: {e}", parent=self.root)
    
    def _browse_source_file(self):
        filepath = filedialog.askopenfilename(
            title="Please select the source text file",
            filetypes=(("Text files", "*.txt"), ("All files", "*.*")),
            parent=self.root  
        )
        if filepath:
            self.source_file_path.set(filepath)
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    self.source_text.delete("1.0", tk.END)
                    self.source_text.insert("1.0", f.read())
                self._update_status(f"Loaded source file: {os.path.basename(filepath)}", level="info")
            except Exception as e:
                messagebox.showerror("File Read Error", f"Could not read file: {e}", parent=self.root)
                self._update_status(f"File read failed: {e}", level="error")
    
    def _export_annotated_text(self):
        content = self.annotated_text.get("1.0", tk.END).strip()
        if not content:
            messagebox.showwarning("Invalid Operation", "No annotated text to export.", parent=self.root)
            return
        
        source_path = self.source_file_path.get()
        default_filename = "annotated_text.txt"
        if source_path:
            base, ext = os.path.splitext(os.path.basename(source_path))
            default_filename = f"{base}_annotated{ext}"
    
        filepath = filedialog.asksaveasfilename(
            title="Export Annotated Text",
            defaultextension=".txt",
            filetypes=(("Text files", "*.txt"), ("All files", "*.*")),
            initialfile=default_filename,
            parent=self.root
        )
    
        if filepath:
            try:
                with open(filepath, 'w', encoding='utf-8') as f:
                    f.write(content)
                self._update_status(f"File successfully exported to: {os.path.basename(filepath)}", level="success")
            except Exception as e:
                messagebox.showerror("Export Failed", f"Could not write to file: {e}", parent=self.root)
                self._update_status(f"File export failed: {e}", level="error")
    
    def _perform_annotation(self, source_text, term_dict):
        sorted_terms = sorted(term_dict.keys(), key=len, reverse=True)
        annotated_text = source_text
        for source_term in sorted_terms:
            target_term = term_dict[source_term]
            annotation_tag = f"{source_term}{{{target_term}}}"
            annotated_text = annotated_text.replace(source_term, annotation_tag)
        return annotated_text
    
    def _start_annotation(self):
        source_text = self.source_text.get("1.0", tk.END).strip()
        if not self.current_terms:
            messagebox.showwarning("Invalid Operation", "Please select and load a valid terminology first.", parent=self.root)
            return
        if not source_text:
            messagebox.showwarning("Invalid Operation", "Source text content cannot be empty.", parent=self.root)
            return
    
        self.annotate_button.config(state=tk.DISABLED)
        self._update_status("Annotating, please wait...", level="processing")
        
        try:
            result = self._perform_annotation(source_text, self.current_terms)
            self.annotated_text.config(state=tk.NORMAL)
            self.annotated_text.delete("1.0", tk.END)
            self.annotated_text.insert("1.0", result)
            self.annotated_text.config(state=tk.DISABLED)
            self._update_status("Annotation complete!", level="success")
        except Exception as e:
            self._update_status(f"An error occurred during annotation: {e}", level="error")
            messagebox.showerror("Annotation Failed", f"An unknown error occurred: {e}", parent=self.root)
        finally:
            self.annotate_button.config(state=tk.NORMAL)
    
    def _on_closing(self):
        self.root.destroy()





SETTINGS_FILE = "settings.json"
ERROR_LOG_FILE = "error_log.txt"
API_PROVIDERS = {
    "DeepSeek": "https://api.deepseek.com",
    "SiliconFlow": "https://api.siliconflow.cn/v1",
    "OpenAI": "https://api.openai.com/v1"
}


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
        "api_keys": {},
        "model_names": ["deepseek-chat", "deepseek-reasoner"],
        "prompts": {
            "Default Translation Prompt": (
                "You are a professional, accurate, and faithful translator. "
                "Please translate the text from the \"[Text to Translate]\" section into American English.\n"
                "Directly output the translated content of that section ONLY. "
                "Do not provide any explanations, annotations, or any other extraneous text.\n\n"
                "{context}"
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


class TranslationApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.settings = load_settings()
        self.selected_files = []
        self.annotator_window = None
    

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
        self.title("AI-Powered Translation Aligner (AI-PTA) v0.7")
        self.geometry("800x850") 
        self.minsize(600, 700)
    
        self.menu_bar = tk.Menu(self)
        self.config(menu=self.menu_bar)
        
        tools_menu = tk.Menu(self.menu_bar, tearoff=0)
        self.menu_bar.add_cascade(label="Tools", menu=tools_menu)
        tools_menu.add_command(label="Term Annotator", command=self._open_annotator)
    
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
        self.api_provider_var = tk.StringVar(value="DeepSeek")
        ttk.Combobox(settings_frame, textvariable=self.api_provider_var, values=list(API_PROVIDERS.keys()), state="readonly").grid(row=2, column=1, columnspan=3, sticky="ew", padx=5, pady=5)
        
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
        ttk.Button(api_btn_frame, text="Save", command=self._save_api_key, width=5).pack(side=tk.LEFT, padx=2)
        ttk.Button(api_btn_frame, text="Delete", command=self._delete_api_key, width=5).pack(side=tk.LEFT, padx=2)
    
        ttk.Label(settings_frame, text="Model Name (Optional):").grid(row=4, column=0, sticky="w", padx=5, pady=5)
        model_frame = ttk.Frame(settings_frame)
        model_frame.grid(row=4, column=1, columnspan=3, sticky="ew", padx=5, pady=5)
        model_frame.columnconfigure(0, weight=1)
        self.model_name_var = tk.StringVar()
        self.model_name_combo = ttk.Combobox(model_frame, textvariable=self.model_name_var)
        self.model_name_combo.grid(row=0, column=0, sticky="ew")
        model_btn_frame = ttk.Frame(model_frame)
        model_btn_frame.grid(row=0, column=1, padx=(5,0))
        ttk.Button(model_btn_frame, text="Save", command=self._save_model_name, width=5).pack(side=tk.LEFT, padx=2)
        ttk.Button(model_btn_frame, text="Delete", command=self._delete_model_name, width=5).pack(side=tk.LEFT, padx=2)
    
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
    
    def _post_ui_setup(self):
        self._update_prompt_combo()
        if self.settings['prompts']:
            first_prompt_name = list(self.settings['prompts'].keys())[0]
            self.prompt_var.set(first_prompt_name)
            self._on_prompt_select()
        
        self._update_api_key_combo()
        self._update_model_name_combo()
        if self.settings['model_names']:
            self.model_name_var.set(self.settings['model_names'][0])
    
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
            base_url = API_PROVIDERS.get(provider_name)
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