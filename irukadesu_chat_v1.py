import json
import os
import tkinter as tk
from tkinter import ttk
from ttkthemes import ThemedTk
from tkinter import messagebox, simpledialog
import openai
import threading
from datetime import datetime

# グローバル変数の設定
SETTINGS_FILE = "settings.txt"  # 設定ファイルのパスを指定

DEFAULT_SETTINGS = {
    "API_KEY": "Your OpenAI API Key",
    "chatbot_name": "イルカです",
    "user_name": "あなた",
    "bg_color": "#ffffff",  # 背景色
    "fg_color": "#2f7dcc",  # フォントカラー
    "font_name": "メイリオ",
    "theme_name": "arc",  # ttkthemesのテーマ名
    "system_message": "あなたはとても賢くて親切なAIイルカアシスタントです。ビジネス、マーケティング、戦略、分析、データサイエンスが得意だと思っています。口調は、外資系コンサルタント風のカタカナの略語やビジネス用語を多用します",
    "temperature_setting": 0.8,
    "max_tokens_setting": 500,
    "chat_models": "gpt-3.5-turbo",
}


# 設定をロード
if os.path.exists(SETTINGS_FILE):
    with open(SETTINGS_FILE, "r", encoding='utf-8') as f:
        settings = json.load(f)
        for key, value in settings.items():
            if key in DEFAULT_SETTINGS:
                DEFAULT_SETTINGS[key] = value

def save_settings():
    """保存設定"""
    with open(SETTINGS_FILE, "w", encoding='utf-8') as f:
        json.dump(DEFAULT_SETTINGS, f, ensure_ascii=False)

API_KEY = DEFAULT_SETTINGS["API_KEY"]
chatbot_name = DEFAULT_SETTINGS["chatbot_name"]
user_name = DEFAULT_SETTINGS["user_name"]
bg_color = DEFAULT_SETTINGS["bg_color"]
fg_color = DEFAULT_SETTINGS["fg_color"]
font_name = DEFAULT_SETTINGS["font_name"]
theme_name = DEFAULT_SETTINGS["theme_name"]
system_message = DEFAULT_SETTINGS["system_message"]
temperature_setting = DEFAULT_SETTINGS["temperature_setting"]
max_tokens_setting = DEFAULT_SETTINGS["max_tokens_setting"]
chat_models = DEFAULT_SETTINGS["chat_models"]



hour = datetime.now().hour
if 5 <= hour < 10:
    greeting = "おはようございます"
elif 10 <= hour < 18:
    greeting = "こんにちは"
else:
    greeting = "こんばんは"

start_message = f"{greeting}、" + user_name + "さん。私は親切で賢いAIイルカアシスタントです！\n何について調べますか？"


temperature_setting = 0.8
max_tokens_setting = 500
window_height = 500
window_width = 270
chatbox_height = 5  # チャットボックスの高さ

# OpenAI GPT-3設定
openai.api_key = API_KEY
chat_models = "gpt-3.5-turbo"

# メッセージ履歴を保持するリスト
message_list = [{"role": "system", "content": system_message}]

def change_API_KEY():
    global API_KEY
    API_KEY = simpledialog.askstring("API KEY", "あなたのOpenAI API KEYを入力してください:")
    openai.api_key = API_KEY
    DEFAULT_SETTINGS["API_KEY"] = API_KEY
    save_settings()

def change_user_name():
    global user_name
    user_name = simpledialog.askstring("ユーザー名", "新しいuser nameを入力してください:")
    DEFAULT_SETTINGS["user_name"] = user_name
    save_settings()

def change_chatbot_name():
    global chatbot_name
    chatbot_name = simpledialog.askstring("チャットボット名", "新しいchatbot nameを入力してください:")
    DEFAULT_SETTINGS["chatbot_name"] = chatbot_name
    save_settings()

def change_system_message():
    global system_message
    system_message = simpledialog.askstring("システムメッセージ", "新しいsystem messageを入力してください:")
    message_list[0]['content'] = system_message
    DEFAULT_SETTINGS["system_message"] = system_message
    save_settings()

def change_temperature_setting():
    global temperature_setting
    temperature_setting = simpledialog.askfloat("温度設定", "新しいtemperatureを入力してください:")
    DEFAULT_SETTINGS["temperature_setting"] = temperature_setting
    save_settings()

def change_max_tokens_setting():
    global max_tokens_setting
    max_tokens_setting = simpledialog.askinteger("最大トークン設定", "新しいmax tokenを入力してください:")
    DEFAULT_SETTINGS["max_tokens_setting"] = max_tokens_setting
    save_settings()

def change_chat_models():
    global chat_models
    chat_models = simpledialog.askstring("チャットモデル", "新しいchat modelを入力してください:")
    DEFAULT_SETTINGS["chat_models"] = chat_models
    save_settings()





def fetch_gpt_response(message):
    message_list.append({"role": "user", "content": message})
    # GPTが考え中であることを表示
    chatbox.config(state="normal")
    chatbox.insert(tk.END, f"{chatbot_name} is thinking...\n\n")
    chatbox.config(state="disabled")
    chatbox.see(tk.END)
    try:
        response = openai.ChatCompletion.create(
            model=chat_models,
            messages=message_list,
            max_tokens=max_tokens_setting,
            temperature=temperature_setting,
            top_p=1
        )
        message_list.append({"role": "assistant", "content": response['choices'][0]['message']['content']})
        on_new_response()
    except Exception as e:
        messagebox.showerror("エラー", f"エラーが発生しました: {str(e)}")

def on_submit():
    user_input = user_input_entry.get()
    if user_input:
        chatbox.config(state="normal")
        chatbox.insert(tk.END, f"{user_name}: {user_input}\n\n")
        chatbox.config(state="disabled")
        user_input_entry.delete(0, tk.END)
        threading.Thread(target=fetch_gpt_response, args=(user_input,)).start()

def on_new_response():
    chatbox.config(state="normal")
    chatbox.delete('end-3l', 'end-1l')  # "thinking"メッセージを削除
    chatbox.insert(tk.END, f"{chatbot_name}: {message_list[-1]['content']}\n\n")
    chatbox.config(state="disabled")
    chatbox.see(tk.END)

def on_close():
    with open("chat_history.txt", "w", encoding="utf-8") as f:
        for message in message_list:
            role = message['role']
            if role == "system":
                role = chatbot_name
            else:
                role = user_name if role == "user" else chatbot_name
            f.write(f"{role}: {message['content']}\n")
    root.quit()

# ウィンドウ作成
root = ThemedTk(theme=theme_name)
root.title('DeepDolphin Dialogues: AI Chat Companion')
root.geometry(f"{window_width}x{window_height}")
root.configure(bg=bg_color)
root.protocol("WM_DELETE_WINDOW", on_close)

# メニューバー作成
menubar = tk.Menu(root)
root.config(menu=menubar)
settingsmenu = tk.Menu(menubar, tearoff=0)
menubar.add_cascade(label="⚙", menu=settingsmenu)
settingsmenu.add_command(label="API KEYを変更", command=change_API_KEY)
settingsmenu.add_command(label="ユーザー名を変更", command=change_user_name)
settingsmenu.add_command(label="チャットボット名を変更", command=change_chatbot_name)
settingsmenu.add_command(label="システムメッセージを変更", command=change_system_message)

settingsmenu.add_command(label="温度設定を変更", command=change_temperature_setting)
settingsmenu.add_command(label="最大トークン設定を変更", command=change_max_tokens_setting)
settingsmenu.add_command(label="チャットモデルを変更", command=change_chat_models)



# チャットボットアイコン画像
chatbot_icon = tk.PhotoImage(file="chatboticon.png")
chatbot_label = tk.Label(root, image=chatbot_icon, bg=bg_color)
chatbot_label.pack(pady=10)

# チャット欄
chat_frame = tk.Frame(root, bg=bg_color)
chat_frame.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)

# スクロールバー
scrollbar = ttk.Scrollbar(chat_frame)
scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

# チャットボックス
chatbox = tk.Text(chat_frame, bg=bg_color, fg=fg_color, font=(font_name, 11), wrap="word", yscrollcommand=scrollbar.set, height=chatbox_height, relief=tk.GROOVE, bd=0)
chatbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
chatbox.insert(tk.END, f"{chatbot_name}: {start_message}\n\n")
chatbox.config(state="disabled")
scrollbar.config(command=chatbox.yview)

# ユーザー入力欄
user_input_entry = tk.Entry(root, bg=bg_color, fg=fg_color, font=(font_name, 10), relief=tk.GROOVE, bd=1)
user_input_entry.pack(padx=10, pady=10, fill=tk.X, expand=True)
user_input_entry.bind("<Return>", lambda e: on_submit())

# 送信ボタン
#submit_button = tk.Button(root, text=f"会話する🐬", command=on_submit, bg=bg_color, fg=fg_color, font=(font_name, 8), relief=tk.RAISED, bd=0)
#submit_button.pack(padx=10, pady=10, fill=tk.X, expand=True)




root.mainloop()
