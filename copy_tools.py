from copy import copy
from fileinput import close
from genericpath import exists
from importlib.resources import path
from PIL import ImageGrab, Image
import pyperclip
import win32.win32clipboard as clip
import win32.win32console as win32con
from io import BytesIO
import json
import hashlib
import asyncio
import datetime
import os
import shutil

pre_hash = None


def add_data(new_data):
    with open("history_data.json", "r", encoding="utf-8") as f:
        old_data = json.load(f)
        old_data.insert(0, new_data)

    with open("history_data.json", "w", encoding="utf-8") as f:
        json.dump(old_data, f, indent=2, ensure_ascii=False)


def get_text(cur):
    return cur


def get_img(cur, data, nowTime):
    cur_hash = hashlib.md5(data.tobytes()).hexdigest()
    cur["hash"] = cur_hash
    cur["type"] = "img"
    img_dir = os.path.join(os.path.dirname(__file__),"img")
    if not os.path.exists(img_dir):
        os.mkdir(img_dir)
    if pre_hash == cur_hash:
        return cur
    data.save(os.path.join(img_dir,f"{nowTime}.png"))
    cur["content"] = os.path.join(img_dir,f"{nowTime}.png")
    return cur


def get_file(cur,data,nowTime):
    file_hash = hashlib.md5(data.tobytes()).hexdigest()
    cur["type"] = "file"
    for i in data:
        cur["content"] = os.path.join(os.path.dirname(__file__),"files",f"{nowTime}_{os.path.basename(i)}")
        cur["hash"] = file_hash(cur["content"],hashlib.md5)
        file_dir = os.path.join(os.path.dirname(__file__),"img")
        if not os.path.exists(file_dir):
            os.os.mkdir(file_dir)
        shutil.copy(i,os.path.join(file_dir,f"{nowTime}_{os.path.basename(i)}"))
        return cur


def setImage(data):
    #打开剪贴板
    clip.OpenClipboard()
    #清空剪贴板
    clip.EmptyClipboard()
    #将图片放入
    clip.SetClipboardData(win32con.CF_DIB,data)
    clip.CloseClipboard()


def set_clipboard_img(path):
    img = Image.open(path)
    output_img = BytesIO()
    img.save(output_img,"BMP")
    data = output_img.getvalue()[14:]
    output_img.close()
    setImage(data)

async def get_clipboard_contents():
    global pre_hash

    while 1:
        await asyncio.sleep(0.5)
        content = pyperclip.paste()
        nowTime = datetime.datetime.now().strftime(r'%Y-%m-%d-%H-%M-%S')

        cur = {
            "type": "text",
            "content": content,
            "create_time": nowTime,
            "hash": hashlib.md5(content.encode("utf8")).hexdigest()
        }
    
        if content:
            cur = get_text(cur)
        else:
            try:
                data = ImageGrab.grabclipboard()
            except:
                continue
            if isinstance(data,list):
                cur = get_file(cur,data,nowTime)
            elif isinstance(data,Image.Image):
                cur = get_img(cur,data,nowTime)
            else:
                continue
        if pre_hash == cur["hash"]:continue
        pre_hash = cur["hash"]
        add_data(cur)
        yield cur

if __name__ == '__main__':
    get_clipboard_contents()
