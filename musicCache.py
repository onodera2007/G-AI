import os
import json
import subprocess

CACHE_FILE = "music.json"
MUSIC_DIR = os.path.join(os.getcwd(), "music")  # 根目录/music

# 确保目录存在
os.makedirs(MUSIC_DIR, exist_ok=True)

def load_cache():
    """加载缓存"""
    if os.path.exists(CACHE_FILE):
        with open(CACHE_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return []

def save_cache(data):
    """保存缓存"""
    with open(CACHE_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def find_in_cache(title: str):
    """查找缓存中是否有该曲子"""
    cache = load_cache()
    for item in cache:
        if item["title"] == title:
            return item
    return None

def download_music(title: str, url: str, source: str) -> str:
    """
    下载音乐并写入缓存
    返回下载后的文件路径
    """
    # 文件名安全化
    safe_title = "".join(c for c in title if c.isalnum() or c in (" ", "_", "-")).rstrip()
    filepath = os.path.join(MUSIC_DIR, f"{safe_title}.mp3")

    # yt-dlp 下载
    command = [
        "yt-dlp", "-x", "--audio-format", "mp3",
        "-o", filepath,
        url
    ]
    print("运行命令:", " ".join(command))
    subprocess.run(command, check=True)

    # 写入缓存
    cache = load_cache()
    cache.append({
        "title": title,
        "file": filepath,
        "source": source,
        "url": url
    })
    save_cache(cache)
    return filepath

def get_or_download(title: str, url: str, source: str) -> str:
    """
    如果缓存有 -> 返回缓存文件路径
    没有 -> 下载并写入缓存
    """
    item = find_in_cache(title)
    if item:
        print(f"[缓存命中] {title}")
        return item["file"]
    else:
        print(f"[未缓存，下载] {title}")
        return download_music(title, url, source)
