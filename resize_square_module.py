from datetime import date
import traceback
from PIL import Image
from _common import get_path
import os
from glob import glob
import shutil
from tqdm import tqdm
import polars as pl

class REsquare():
    def __init__(self) -> None:
        self.img_dict = {"旧ファイル名":[], "出力パス":[], "幅":[], "高さ":[], "タイプ":[], "対象":[], "出力ファイル名":[], "拡張子変更":[]}
        self.suf_list = ["jpg", "jpeg", "gif", "tif", "tiff", "png"]
        self.unknown = []
        self.resized_img = []
        pass

    def set_folder(self) -> None:
        self.folder_path = get_path.ask_folder("画像フォルダ")
        self.folder_name = os.path.basename(self.folder_path)
        self.files = [_ for _ in glob(os.path.join(self.folder_path, "*")) if not _.endswith(".db") or not _.endswith(".ini")]
    
    def write_dict(self, fn, p, w, h, t, flag, new_fn, suf) -> None:
        self.img_dict["旧ファイル名"].append(fn)
        self.img_dict["出力パス"].append(p)
        self.img_dict["幅"].append(w)
        self.img_dict["高さ"].append(h)
        self.img_dict["タイプ"].append(t)
        self.img_dict["対象"].append(flag)
        self.img_dict["出力ファイル名"].append(new_fn)
        self.img_dict["拡張子変更"].append(suf)
    
    def resize(self, img_in, img_out, output_format=None):
        
        if os.path.splitext(img_in)[-1][1:].lower() not in self.suf_list:
            self.unknown.append(os.path.splitext(img_in)[-1])
        
        # 読み込む
        try:
            img = Image.open(img_in)
            img_format = img.format
        except (OSError, IOError) as e:
            self.write_dict(os.path.basename(img_in), img_out, None, None, os.path.splitext(img_in)[-1][1:], None, None, None)
            # print(f"Error opening image {img_in}: {e}")
            self.img_dict["タイプ"][-1] += "--読み込みエラー"
            return False
        
        # 透明度を持つ画像を白背景のRGBに変換
        if img.mode in ('RGBA', 'LA'):
            alpha = img.split()[3]
        elif img.mode == 'P' and 'transparency' in img.info:
            img = img.convert('RGBA')
            alpha = img.split()[3]
        else:
            img = img.convert('RGB')
            alpha = None

        if alpha is not None:
            background = Image.new('RGB', img.size, (255, 255, 255))  # 白背景
            background.paste(img, mask=alpha)  # アルファチャンネルをマスクとして使用
            img = background
            
        else:
            img = img.convert('RGB')
        # 元の画像サイズを取得
        original_width, original_height = img.size
        if max(original_height, original_width) < 500:
            self.write_dict(os.path.basename(img_in), img_out, original_width, original_height, img_format, False, os.path.basename(img_out), os.path.splitext(img_in)[-1][1:]!="jpg")
        elif original_height == original_width:
            self.write_dict(os.path.basename(img_in), img_out, original_width, original_height, img_format, original_height != original_width, os.path.basename(img_out), os.path.splitext(img_in)[-1][1:]!="jpg")
        else:
            self.write_dict(os.path.basename(img_in), img_out, original_width, original_height, img_format, original_height != original_width, os.path.basename(img_out), os.path.splitext(img_in)[-1][1:]!="jpg")
            self.resized_img.append(img_out)
        
        # 正方形キャンバスのサイズを決定（長い辺を基準）
        max_side = max(original_width, original_height)

        try:
            # 透明度をサポートしないフォーマットの場合
            canvas = Image.new('RGB', (max_side, max_side), (255, 255, 255))
            img_position = ((max_side - original_width) // 2, (max_side - original_height) // 2)
            canvas.paste(img, img_position)
        except OSError:
            self.img_dict["タイプ"][-1] += "破損"
            return False

        # キャンバスが500x500以下の場合、500x500まで拡大
        if max_side < 500:
            canvas = canvas.resize((500, 500), Image.LANCZOS)
        
        # 保存
        canvas.save(img_out, format=output_format)
        return True

if __name__ == "__main__":
    
    print("作業フォルダを指定してください")
    os.chdir(get_path.ask_folder("作業フォルダ(88_作業データ_最新)を指定してください："))
    
    def main_CUI():
        
        print("画像フォルダを指定してください")
        
        resquare = REsquare()
        resquare.set_folder()
        
        print(resquare.folder_path)
        
        while os.path.exists(f"画像_REsize"):
            input("「画像_REsize」は既に存在しています、手動で削除してください。")
        os.mkdir(f"画像_REsize")
                
        for file in tqdm(resquare.files, desc="画像処理中"):

            out_path = os.path.join(f"画像_REsize", os.path.splitext(os.path.basename(file))[0] + ".jpg")
            if not resquare.resize(file, out_path, "jpeg"):
                if not os.path.exists("Error_img"):
                    os.mkdir("Error_img")
                out_path = out_path.replace("画像_REsize", "Error_img")
                shutil.copy2(file, out_path)
        
        df = pl.DataFrame(resquare.img_dict)
        df.write_excel("image_info.xlsx")
        
        print()
        option = input("リサイズ画像を抽出しますか？(Y/N): ")
        
        if option.lower() == "y":
            # オプション：リサイズだけフォルダ作成
            if os.path.exists("REsized_files"):
                shutil.rmtree("REsized_files")
            os.mkdir("REsized_files")
            for file_resize in resquare.resized_img:
                shutil.copy2(file_resize, os.path.join("REsized_files", os.path.basename(file_resize)))
        
        if resquare.unknown != []:
            print(f"\n※注意※想定外の拡張子：{set(resquare.unknown)}")
        
        input("\n完了しました。")

    try:
        main_CUI()
    except Exception as e:
        error_message = str(e)
        with open(f'{date.today()}_error_log.txt', 'a', encoding='utf-8') as f:
            f.write(traceback.format_exc())
        print(e)
        input("未知のエラーが発生しました")
