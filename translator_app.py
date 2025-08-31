import os
import re
import threading
import tkinter as tk
from tkinter import ttk, filedialog, messagebox, simpledialog, scrolledtext
import datetime
import traceback
import json 

import openai
import pandas as pd

# --- 全局配置 ---

# 文件名常量

SETTINGS_FILE = "settings.json"
ERROR_LOG_FILE = "error_log.txt"

# API 服务商配置

API_PROVIDERS = {
    "DeepSeek": "https://api.deepseek.com",
    "SiliconFlow": "https://api.siliconflow.cn/v1",
    "OpenAI": "https://api.openai.com/v1"
}

# --- 错误日志管理逻辑 ---

def log_error(error_message):
    """将错误信息追加到日志文件。"""
    try:
        with open(ERROR_LOG_FILE, 'a', encoding='utf-8') as f:
            timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            full_error = traceback.format_exc()
            f.write(f"--- {timestamp} ---\n")
            f.write(f"{error_message}\n")
            f.write(f"Traceback:\n{full_error}\n\n")
    except Exception as e:
        print(f"写入错误日志失败: {e}")


# --- 设置管理逻辑 (重构) ---

def load_settings():
    """从 settings.json 加载所有设置。如果文件不存在或无效，则返回默认设置。"""
    default_settings = {
        "max_tokens": 2000,
        "context_before": 1,
        "context_after": 1,
        "api_keys": {},
        "model_names": ["deepseek-chat", "deepseek-coder"],
        "prompts": {
            "默认翻译 Prompt": (
                "You are a professional, accurate, and faithful translator. "
                "Please translate the text from the \"[Text to Translate]\" section into American English.\n"
                "Directly output the translated content of that section ONLY. "
                "Do not provide any explanations, annotations, or any other extraneous text.\n\n"
                "{context}" # {context} 将被替换为上下文+待翻译文本
            )
        }
    }
    if not os.path.exists(SETTINGS_FILE):
        return default_settings
    try:
        with open(SETTINGS_FILE, 'r', encoding='utf-8') as f:
            settings = json.load(f)
            # 确保所有键都存在，防止旧版配置文件出错
            for key, value in default_settings.items():
                settings.setdefault(key, value)
            return settings
    except (json.JSONDecodeError, Exception) as e:
        log_error(f"加载 settings.json 失败: {e}. 将使用默认设置。")
        return default_settings

def save_settings(settings):
    """将设置字典保存到 settings.json。"""
    try:
        with open(SETTINGS_FILE, 'w', encoding='utf-8') as f:
            json.dump(settings, f, indent=4, ensure_ascii=False)
    except Exception as e:
        messagebox.showerror("错误", f"保存设置文件失败: {e}")
        log_error(f"保存 settings.json 失败: {e}")


# --- 核心逻辑 (重构) ---

def split_text_into_paragraphs(text):
    """将文本按一个或多个空行拆分为段落列表。"""
    paragraphs = re.split(r'\n\s*\n', text)
    return [p.strip() for p in paragraphs if p.strip()]

# 修改：函数签名增加 max_tokens 参数
def translate_single_paragraph(client, model_name, full_prompt, max_tokens):
    """发送单个请求到 AI 进行翻译。"""
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
            max_tokens=max_tokens  # 新增：将 max_tokens 参数传递给 API
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        error_message = f"API 调用失败: {e}"
        log_error(error_message)
        return f"【翻译失败: {str(e)[:50]}...】"


# --- GUI 应用 ---

class TranslationApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.settings = load_settings()
        self.selected_files = []

        self._setup_style()
        self._setup_ui()
        self._post_ui_setup()
        
        self.protocol("WM_DELETE_WINDOW", self._on_closing)
    
    def _on_closing(self):
        """关闭窗口前保存设置。"""
        # 保存设置时，确保界面上的值被同步
        self.settings['max_tokens'] = self.max_tokens_var.get()
        self.settings['context_before'] = self.context_before_var.get()
        self.settings['context_after'] = self.context_after_var.get()
        save_settings(self.settings)
        self.destroy()
    
    def _setup_style(self):
        self.style = ttk.Style(self)
        self.style.theme_use("clam")
        self.style.configure("Accent.TButton", font=("微软雅黑", 12, "bold"), padding=(10, 5))
        self.style.map("Accent.TButton", background=[("active", "#005f9e"), ("!disabled", "#0078d4")], foreground=[("!disabled", "white")])
        self.style.configure("TLabelFrame.Label", font=("微软雅黑", 11, "bold"))
    
    def _setup_ui(self):
        # 修改：更新程序标题
        self.title("AI-Powered Translation Aligner (AI-PTA) v0.6")
        self.geometry("800x850") 
        self.minsize(600, 700)
    
        # -- 0. 菜单栏 --
        self.menu_bar = tk.Menu(self)
        self.config(menu=self.menu_bar)
        help_menu = tk.Menu(self.menu_bar, tearoff=0)
        self.menu_bar.add_cascade(label="帮助(Help)", menu=help_menu)
        help_menu.add_command(label="关于(About)", command=self._show_about_info)
        help_menu.add_command(label="查看许可证(License)", command=self._show_license_info)
    
        main_frame = ttk.Frame(self, padding="10 10 10 10")
        main_frame.pack(expand=True, fill=tk.BOTH)
        
        main_frame.columnconfigure(0, weight=1)
        main_frame.rowconfigure(2, weight=1)
    
        # -- 1. 文件选择区 --
        files_frame = ttk.LabelFrame(main_frame, text="文件选择", padding="10")
        files_frame.grid(row=0, column=0, sticky="ew", pady=(0, 10))
        files_frame.columnconfigure(0, weight=1)
        self.file_listbox = tk.Listbox(files_frame, height=5, font=("微软雅黑", 10))
        self.file_listbox.grid(row=0, column=0, sticky="ew")
        scrollbar = ttk.Scrollbar(files_frame, orient=tk.VERTICAL, command=self.file_listbox.yview)
        scrollbar.grid(row=0, column=1, sticky="ns")
        self.file_listbox.config(yscrollcommand=scrollbar.set)
        browse_button = ttk.Button(files_frame, text="选择 TXT 文件...", command=self._on_browse_files)
        browse_button.grid(row=1, column=0, columnspan=2, pady=(10, 0), sticky="e")
    
        # -- 2. 参数设置区 --
        settings_frame = ttk.LabelFrame(main_frame, text="参数设置", padding="10")
        settings_frame.grid(row=1, column=0, sticky="ew", pady=5)
        settings_frame.columnconfigure(1, weight=1)
        settings_frame.columnconfigure(3, weight=1) 
    
        ttk.Label(settings_frame, text="最大 Token 数:").grid(row=0, column=0, sticky="w", padx=5, pady=5)
        self.max_tokens_var = tk.IntVar(value=self.settings.get("max_tokens", 2000))
        ttk.Entry(settings_frame, textvariable=self.max_tokens_var, width=10).grid(row=0, column=1, sticky="w", padx=5, pady=5)
    
        ttk.Label(settings_frame, text="上文段落数:").grid(row=1, column=0, sticky="w", padx=5, pady=5)
        self.context_before_var = tk.IntVar(value=self.settings.get("context_before", 1))
        ttk.Entry(settings_frame, textvariable=self.context_before_var, width=10).grid(row=1, column=1, sticky="w", padx=5, pady=5)
        
        ttk.Label(settings_frame, text="下文段落数:").grid(row=1, column=2, sticky="w", padx=20, pady=5)
        self.context_after_var = tk.IntVar(value=self.settings.get("context_after", 1))
        ttk.Entry(settings_frame, textvariable=self.context_after_var, width=10).grid(row=1, column=3, sticky="w", padx=5, pady=5)
    
        ttk.Label(settings_frame, text="API 服务商:").grid(row=2, column=0, sticky="w", padx=5, pady=5)
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
        ttk.Button(api_btn_frame, text="保存", command=self._save_api_key, width=5).pack(side=tk.LEFT, padx=2)
        ttk.Button(api_btn_frame, text="删除", command=self._delete_api_key, width=5).pack(side=tk.LEFT, padx=2)
    
        ttk.Label(settings_frame, text="模型名称 (可选):").grid(row=4, column=0, sticky="w", padx=5, pady=5)
        model_frame = ttk.Frame(settings_frame)
        model_frame.grid(row=4, column=1, columnspan=3, sticky="ew", padx=5, pady=5)
        model_frame.columnconfigure(0, weight=1)
        self.model_name_var = tk.StringVar()
        self.model_name_combo = ttk.Combobox(model_frame, textvariable=self.model_name_var)
        self.model_name_combo.grid(row=0, column=0, sticky="ew")
        model_btn_frame = ttk.Frame(model_frame)
        model_btn_frame.grid(row=0, column=1, padx=(5,0))
        ttk.Button(model_btn_frame, text="保存", command=self._save_model_name, width=5).pack(side=tk.LEFT, padx=2)
        ttk.Button(model_btn_frame, text="删除", command=self._delete_model_name, width=5).pack(side=tk.LEFT, padx=2)
    
        # -- 3. Prompt 管理区 --
        prompt_frame = ttk.LabelFrame(main_frame, text="Prompt 管理", padding="10")
        prompt_frame.grid(row=2, column=0, sticky="nsew", pady=5)
        prompt_frame.columnconfigure(0, weight=1)
        prompt_frame.rowconfigure(1, weight=1)
        prompt_selection_frame = ttk.Frame(prompt_frame)
        prompt_selection_frame.grid(row=0, column=0, sticky="ew", pady=(0, 5))
        prompt_selection_frame.columnconfigure(1, weight=1)
        ttk.Label(prompt_selection_frame, text="选择 Prompt:").grid(row=0, column=0, padx=(0, 5))
        self.prompt_var = tk.StringVar()
        self.prompt_combo = ttk.Combobox(prompt_selection_frame, textvariable=self.prompt_var, state="readonly")
        self.prompt_combo.grid(row=0, column=1, sticky="ew")
        self.prompt_combo.bind("<<ComboboxSelected>>", self._on_prompt_select)
        btn_frame = ttk.Frame(prompt_selection_frame)
        btn_frame.grid(row=0, column=2, padx=(10, 0))
        ttk.Button(btn_frame, text="添加", command=self._add_prompt).pack(side=tk.LEFT, padx=2)
        ttk.Button(btn_frame, text="保存", command=self._save_current_prompt).pack(side=tk.LEFT, padx=2)
        ttk.Button(btn_frame, text="删除", command=self._delete_prompt).pack(side=tk.LEFT, padx=2)
        self.prompt_text = tk.Text(prompt_frame, wrap=tk.WORD, height=8, font=("微软雅黑", 10))
        self.prompt_text.grid(row=1, column=0, sticky="nsew")
        prompt_scrollbar = ttk.Scrollbar(prompt_frame, orient=tk.VERTICAL, command=self.prompt_text.yview)
        prompt_scrollbar.grid(row=1, column=1, sticky="ns")
        self.prompt_text.config(yscrollcommand=prompt_scrollbar.set)
    
        # -- 4. 主操作按钮 --
        self.start_button = ttk.Button(main_frame, text="开始处理", style="Accent.TButton", command=self._start_processing)
        self.start_button.grid(row=3, column=0, pady=10, ipady=5, sticky="ew")
        
        # -- 5. 状态栏 --
        self.status_label = ttk.Label(self, text="准备就绪", padding="5 2", anchor=tk.W)
        self.status_label.pack(side=tk.BOTTOM, fill=tk.X)
        self._update_status("准备就绪", "gray")
    
    def _post_ui_setup(self):
        """UI 创建完成后，加载数据并初始化控件状态"""
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
            "关于",
            "王万涌\n\n"
            "Wanyong Wang\n"
            "Department of Chinese and Bilingual Studies\n"
            "The Hong Kong Polytechnic University\n"
            "Kowloon, Hong Kong, China\n"
            "Email: wangwanyong365@hotmail.com"
        )
    
    def _show_license_info(self):
        license_window = tk.Toplevel(self)
        license_window.title("MIT 许可证 (MIT License)")
        license_window.geometry("600x500")
        text_area = scrolledtext.ScrolledText(license_window, wrap=tk.WORD, font=("微软雅黑", 10))
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


    # --- API Key & Model Name 管理 (重构以增加私密性) ---
    
    def _get_current_api_key(self):
        """
        获取真实的 API Key。
        如果输入框中的是已保存的名称，则返回对应的 Key。
        否则，返回输入框中的内容（视为新 Key）。
        """
        displayed_text = self.api_key_var.get().strip()
        if displayed_text in self.settings['api_keys']:
            return self.settings['api_keys'][displayed_text]
        return displayed_text
    
    def _update_api_key_combo(self):
        self.api_key_combo['values'] = list(self.settings['api_keys'].keys())
    
    def _on_api_key_select(self, event=None):
        selected_name = self.api_key_combo.get()
        if selected_name in self.settings['api_keys']:
            self.api_key_var.set(selected_name)
            self.api_key_combo.config(show="")
    
    def _on_api_key_typed(self, event=None):
        """当用户在 API Key 输入框中打字时触发。"""
        current_text = self.api_key_var.get()
        if current_text not in self.settings['api_keys']:
            self.api_key_combo.config(show="●")
        else:
            self.api_key_combo.config(show="")
    
    def _save_api_key(self):
        key_or_name = self.api_key_var.get().strip()
        if not key_or_name:
            return messagebox.showwarning("警告", "API Key 不能为空。")
    
        if key_or_name in self.settings['api_keys']:
            messagebox.showinfo("提示", "这是一个已保存的 API Key 名称，无需重复保存。")
            return
    
        new_key = key_or_name
        name = simpledialog.askstring("保存 API Key", "请输入该 Key 的一个易记名称:", parent=self)
        
        if name and name.strip():
            name = name.strip()
            if name in self.settings['api_keys']:
                 if not messagebox.askyesno("覆盖确认", f"名称 '{name}' 已存在。要用新 Key 覆盖它吗？"):
                     return
            
            self.settings['api_keys'][name] = new_key
            save_settings(self.settings)
            self._update_api_key_combo()
            
            self.api_key_combo.set(name)
            self.api_key_combo.config(show="")
            messagebox.showinfo("成功", f"API Key '{name}' 已保存。")
    
    def _delete_api_key(self):
        name = self.api_key_combo.get()
        if not name or name not in self.settings['api_keys']:
            return messagebox.showerror("错误", "请先选择一个要删除的 API Key。")
        if messagebox.askyesno("确认删除", f"确定要删除 API Key '{name}' 吗？"):
            del self.settings['api_keys'][name]
            save_settings(self.settings)
            self._update_api_key_combo()
            self.api_key_var.set("")
            self.api_key_combo.config(show="●")
    
    def _update_model_name_combo(self):
        self.model_name_combo['values'] = self.settings.get('model_names', [])
    
    def _save_model_name(self):
        name = self.model_name_var.get().strip()
        if not name: return messagebox.showwarning("警告", "模型名称不能为空。")
        if name not in self.settings['model_names']:
            self.settings['model_names'].append(name)
            save_settings(self.settings)
            self._update_model_name_combo()
            messagebox.showinfo("成功", f"模型 '{name}' 已保存到列表。")
        else:
            messagebox.showinfo("提示", f"模型 '{name}' 已存在于列表中。")
    
    def _delete_model_name(self):
        name = self.model_name_var.get().strip()
        if not name or name not in self.settings['model_names']:
            return messagebox.showerror("错误", "当前输入的模型名称不在列表中。")
        if messagebox.askyesno("确认删除", f"确定要从列表中删除模型 '{name}' 吗？"):
            self.settings['model_names'].remove(name)
            save_settings(self.settings)
            self._update_model_name_combo()
            self.model_name_var.set("")
    
    # --- Prompt 管理 ---
    def _update_prompt_combo(self):
        self.prompt_combo['values'] = list(self.settings['prompts'].keys())
    
    def _on_prompt_select(self, event=None):
        name = self.prompt_var.get()
        if name in self.settings['prompts']:
            self.prompt_text.delete("1.0", tk.END)
            self.prompt_text.insert("1.0", self.settings['prompts'][name])
    
    def _add_prompt(self):
        name = simpledialog.askstring("新 Prompt", "请输入新 Prompt 的名称:", parent=self)
        if name and name.strip():
            name = name.strip()
            if name in self.settings['prompts']: return messagebox.showerror("错误", "该名称已存在！")
            self.settings['prompts'][name] = f"这是 '{name}' 的 Prompt。\n请在此输入指令，并使用 {{context}} 作为占位符。"
            save_settings(self.settings)
            self._update_prompt_combo()
            self.prompt_var.set(name)
            self._on_prompt_select()
    
    def _save_current_prompt(self):
        name = self.prompt_var.get()
        if not name: return messagebox.showerror("错误", "没有选中的 Prompt 可保存。")
        content = self.prompt_text.get("1.0", tk.END).strip()
        if "{context}" not in content:
            if not messagebox.askyesno("警告", "当前 Prompt 未找到占位符 '{context}'。\n这可能导致无法正确插入原文和上下文。\n是否仍要保存？"):
                return
        self.settings['prompts'][name] = content
        save_settings(self.settings)
        messagebox.showinfo("成功", f"Prompt '{name}' 已保存。")
    
    def _delete_prompt(self):
        name = self.prompt_var.get()
        if not name: return messagebox.showerror("错误", "请选择一个要删除的 Prompt。")
        if len(self.settings['prompts']) <= 1: return messagebox.showwarning("警告", "不能删除最后一个 Prompt。")
        if messagebox.askyesno("确认删除", f"确定要删除 Prompt '{name}' 吗？"):
            del self.settings['prompts'][name]
            save_settings(self.settings)
            self._update_prompt_combo()
            first_name = list(self.settings['prompts'].keys())[0]
            self.prompt_var.set(first_name)
            self._on_prompt_select()
    
    # --- 其他 UI 方法 ---
    def _on_browse_files(self):
        files = filedialog.askopenfilenames(title="请选择 TXT 文件", filetypes=[("Text files", "*.txt")])
        if files:
            self.selected_files = list(files)
            self.file_listbox.delete(0, tk.END)
            for file in self.selected_files:
                self.file_listbox.insert(tk.END, os.path.basename(file))
            self._update_status(f"已选择 {len(self.selected_files)} 个文件", "blue")
    
    def _update_status(self, text, color):
        self.status_label.config(text=text, foreground=color)
        self.update_idletasks()
    
    def _start_processing(self):
        api_key = self._get_current_api_key()
        
        if not self.selected_files: return messagebox.showerror("错误", "请先选择 TXT 文件。")
        if not api_key: return messagebox.showerror("错误", "API Key 不能为空。")
        if not self.prompt_text.get("1.0", tk.END).strip(): return messagebox.showerror("错误", "Prompt 内容不能为空。")
    
        self.start_button.config(state=tk.DISABLED)
        self._update_status("正在处理中，请稍候...", "orange")
    
        thread = threading.Thread(target=self._processing_task, daemon=True)
        thread.start()
    
    def _processing_task(self):
        try:
            # 从 UI 获取设置
            provider_name = self.api_provider_var.get()
            api_key = self._get_current_api_key()
            model_name = self.model_name_var.get().strip() or "deepseek-chat"
            base_url = API_PROVIDERS.get(provider_name)
            user_prompt_template = self.prompt_text.get("1.0", tk.END).strip()
            context_before = self.context_before_var.get()
            context_after = self.context_after_var.get()
            max_tokens_value = self.max_tokens_var.get() # 新增：获取 max_tokens 的值
    
            client = openai.OpenAI(api_key=api_key, base_url=base_url)
    
            total_files = len(self.selected_files)
            for i, file_path in enumerate(self.selected_files):
                file_name = os.path.basename(file_path)
                dir_name = os.path.splitext(file_name)[0]
                output_dir = os.path.join(os.path.dirname(file_path), dir_name)
                os.makedirs(output_dir, exist_ok=True)
                
                self.after(0, self._update_status, f"[{i+1}/{total_files}] 正在读取和拆分: {file_name}", "orange")
    
                with open(file_path, 'r', encoding='utf-8') as f:
                    original_text = f.read()
                
                paragraphs = split_text_into_paragraphs(original_text)
                if not paragraphs:
                    log_error(f"文件 {file_name} 为空或不包含有效段落，已跳过。")
                    continue
    
                translated_paragraphs = []
                total_paragraphs = len(paragraphs)
                
                for j, para in enumerate(paragraphs):
                    self.after(0, self._update_status, f"[{i+1}/{total_files}] 翻译 {file_name} 段落 ({j+1}/{total_paragraphs})", "orange")
                    
                    context_text_parts = []
                    start_index = max(0, j - context_before)
                    if start_index < j:
                        context_text_parts.append("[Previous Context]")
                        context_text_parts.extend(paragraphs[start_index:j])
                        context_text_parts.append("") 
                    
                    context_text_parts.append("[Text to Translate]")
                    context_text_parts.append(para)
                    
                    end_index = min(total_paragraphs, j + 1 + context_after)
                    if j + 1 < end_index:
                        context_text_parts.append("\n[Next Context]")
                        context_text_parts.extend(paragraphs[j+1:end_index])
    
                    context_for_prompt = "\n".join(context_text_parts)
                    full_prompt = user_prompt_template.format(context=context_for_prompt)
                    
                    # 修改：将 max_tokens_value 传递给函数
                    translated_para = translate_single_paragraph(client, model_name, full_prompt, max_tokens_value)
                    translated_paragraphs.append(translated_para)
    
                full_translated_text = "\n\n".join(translated_paragraphs)
                translated_file_path = os.path.join(output_dir, f"{dir_name}_translated.txt")
                with open(translated_file_path, 'w', encoding='utf-8') as f: f.write(full_translated_text)
    
                self.after(0, self._update_status, f"[{i+1}/{total_files}] 正在生成 Excel 文件...", "orange")
                
                df = pd.DataFrame({'原文': paragraphs, '译文': translated_paragraphs})
                excel_path = os.path.join(output_dir, f"{dir_name}_corpus.xlsx")
                df.to_excel(excel_path, index=False, engine='openpyxl')
    
            # 处理完成后，保存当前界面上的设置
            self.settings['max_tokens'] = self.max_tokens_var.get()
            self.settings['context_before'] = self.context_before_var.get()
            self.settings['context_after'] = self.context_after_var.get()
            save_settings(self.settings)
    
            self.after(0, self._update_status, "处理完成！所有文件已保存在各自的文件夹中。", "green")
    
        except Exception as e:
            error_message = f"处理失败：{e}"
            log_error(f"发生严重错误，处理流程中断. 错误: {e}")
            self.after(0, self._update_status, error_message, "red")
            self.after(0, messagebox.showerror, "发生错误", f"{e}\n\n详细信息已记录到 error_log.txt")
        
        finally:
            self.after(0, lambda: self.start_button.config(state=tk.NORMAL))

if __name__ == "__main__":
    app = TranslationApp()
    app.mainloop()