from tkinter import filedialog

def ask_folder(title="フォルダを選択してください。") -> str:
    folder_path = filedialog.askdirectory(title=title)
    if len(folder_path) == 0:
        return None
    else:
        return folder_path

def ask_file(title="ファイルを選択してください。") -> str:
    file_path = filedialog.askopenfilename(title=title)
    if len(file_path) == 0:
        return None
    else:
        return file_path

def ask_files(title="フファイル(複数)を選択してください。") -> tuple:
    file_path = filedialog.askopenfilenames(title=title)
    if len(file_path) == 0:
        return None
    else:
        return file_path

if __name__ == "__main__":
    print(ask_file())