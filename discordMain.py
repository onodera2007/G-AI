# 标准库
import json
import os
import random
import traceback
import tempfile
# 第三方库
import discord
from discord.ext import commands
from discord.errors import ConnectionClosed
import yt_dlp
from openai import OpenAI
# 本地模块
from musicCache import get_or_download

ga = False
try:
    from dotenv import load_dotenv
except ImportError:
    print("检测到使用github action")
    ga=True
if (ga!=True):
    load_dotenv()
bot = commands.Bot(
    command_prefix='!',
    intents=discord.Intents.all()
)
AI_CHAT_CHANNEL_IDS = {1408292710011502632,1408292850294198332}
CACHE_FILE = "music.json"
MUSIC_FOLDER = "music" 
if os.path.exists(CACHE_FILE):
    with open(CACHE_FILE, "r", encoding="utf-8") as f:
        music_cache = json.load(f)
else:
    music_cache = {}
user_histories = {}
SYSTEM_PROMPT = {
    1408292710011502632: "你是一个乐于助人的 Discord 聊天机器人",
    1408292850294198332: "你是一个猫娘"
}
def commands(bot):
    @bot.tree.command(name="meme_cn", description="梗")
    async def meme_cn(interaction: discord.Interaction):
        # 定义消息列表
        messages = [
            ":raised_hand: :rofl: :raised_back_of_hand:",
            ":raised_hand: <:emoji_name:1401903542377381998> :raised_back_of_hand: ",
            ":raised_hand: :sob: :raised_back_of_hand: ",
            "那一天的🦑，🦑起来！",
            "你待会会掉这么长的血.jpg"
        ]
        random_message = random.choice(messages)
        await interaction.response.send_message(random_message)
    @bot.tree.command(name="meme", description="meme")
    async def meme_en(interaction: discord.Interaction):
        # 定义消息列表
        messages = [
            ":raised_hand: :rofl: :raised_back_of_hand:",
            ":raised_hand: <:emoji_name:1401903542377381998> :raised_back_of_hand: ",
            ":raised_hand: :sob: :raised_back_of_hand: ",
        ]
        random_message = random.choice(messages)
        await interaction.response.send_message(random_message)
    @bot.tree.command(name="play_youtube", description="播放音乐(YouTube)→可缓存播放")
    async def play(interaction: discord.Interaction, query: str):
        await interaction.response.send_message(f"🔍 正在搜索: {query}")
        ydl_opts = {
            "quiet": True,
            "default_search": "ytsearch1",
            "skip_download": True,
        }
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(query, download=False)
            if "entries" in info:
                info = info["entries"][0]
            title = info["title"]
            url = info["webpage_url"]

        # 缓存 / 下载
        filepath = get_or_download(title, url, source="youtube")

        # 播放
        voice_client = interaction.guild.voice_client
        if not voice_client:
            if interaction.user.voice:
                channel = interaction.user.voice.channel
                await channel.connect()
                voice_client = interaction.guild.voice_client
            else:
                await interaction.followup.send("❌ 你需要先加入一个语音频道！")
                return

        if voice_client.is_playing():
            voice_client.stop()

        voice_client.play(discord.FFmpegPCMAudio(filepath))
        await interaction.followup.send(f"▶️ 正在播放: **{title}** （缓存支持）")
    @bot.tree.command(name="play_bilibili", description="播放音乐(Bilibili)→弃")
    async def play(interaction: discord.Interaction, query: str):
        if not interaction.user.voice:
            await interaction.response.send_message("⚠️ 请先加入语音频道")
            return

        try:
            # 加入语音频道
            channel = interaction.user.voice.channel
            vc = interaction.guild.voice_client or await channel.connect()
            if vc.channel != channel:
                await vc.move_to(channel)

            await interaction.response.send_message(f"🔍 搜索中: {query}")

            # 创建临时目录存放下载文件
            with tempfile.TemporaryDirectory() as tmpdir:

                ydl_opts = {
                    "format": "bestvideo+bestaudio/best",
                    "outtmpl": os.path.join(tmpdir, "%(title)s.%(ext)s"),
                    "cookies": "cookies.txt",
                    "quiet": False,
                    "no_warnings": False,
                    "verbose": True,
                    "postprocessors": [
                        {
                            "key": "FFmpegExtractAudio",
                            "preferredcodec": "mp3",
                            "preferredquality": "192",
                        }
                    ],
                }

                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    # 判断输入类型：BV号或关键字
                    if query.startswith("BV") and len(query) == 12:
                        video_url = f"https://www.bilibili.com/video/{query}"
                        info = ydl.extract_info(video_url, download=True)
                    else:
                        info = ydl.extract_info(f"bilisearch:{query}", download=True)
                        if not info or "entries" not in info or len(info["entries"]) == 0:
                            await interaction.followup.send("❌ 没有找到视频")
                            return
                        info = info["entries"][0]

                # 获取 mp3 文件路径
                mp3_filename = ydl.prepare_filename(info)
                mp3_filename = os.path.splitext(mp3_filename)[0] + ".mp3"

                vc.stop()
                source = discord.FFmpegOpusAudio(mp3_filename)
                vc.play(source)

                await interaction.followup.send(f"🎵 正在播放: **{info.get('title','未知标题')}**")

        except Exception as e:
            await interaction.followup.send(f"❌ 播放失败: {str(e)}")
            import traceback
            print(f"完整错误: {traceback.format_exc()}")
    @bot.tree.command(name="stop", description="停止播放并离开频道")
    async def stop(interaction: discord.Interaction):
        try:
            await interaction.response.send_message("⏳ 正在停止播放...")

            vc = interaction.guild.voice_client
            if not vc:
                await interaction.followup.send("⚠️ 机器人未连接至语音频道")
                return

            # 停止播放
            vc.stop()

            # 断开连接
            await vc.disconnect(force=False)

            await interaction.followup.send("⏹️ 已停止播放并退出频道")

        except Exception as e:
            error_msg = f"❌ 停止时发生错误: {str(e)}"
            print(f"{error_msg}\n{traceback.format_exc()}")

            # 尝试强制断开
            try:
                if interaction.guild.voice_client:
                    await interaction.guild.voice_client.disconnect(force=True)
            except:
                pass

            await interaction.followup.send(error_msg)
    @bot.tree.command(name="play_musicfile", description="播放本地或上传的音频文件(极不稳定！)")
    async def play_musicFile(interaction: discord.Interaction, file: discord.Attachment):
        """播放用户上传的音频文件"""
        try:
            # 检查用户是否在语音频道
            if not interaction.user.voice:
                await interaction.response.send_message("⚠️ 请先加入语音频道")
                return

            # 连接语音频道
            channel = interaction.user.voice.channel
            vc = interaction.guild.voice_client or await channel.connect()
            if vc.channel != channel:
                await vc.move_to(channel)

            await interaction.response.send_message(f"🎵 正在播放文件: **{file.filename}**")

            # 下载文件到临时路径（可选，也可以直接使用 URL）
            file_path = f"./temp_{file.filename}"
            await file.save(file_path)

            source = discord.FFmpegPCMAudio(file_path)
            vc.play(source)
        except Exception as e:
            await interaction.followup.send(f"❌ 播放失败: {str(e)}")
            print(f"完整错误: {traceback.format_exc()}")
    @bot.tree.command(name="list_music", description="显示已缓存的音乐列表")
    async def list_music(interaction: discord.Interaction):
        if not music_cache:
            await interaction.response.send_message("⚠️ 当前没有缓存的曲子")
            return

        # 提取 title 字段
        titles = [item["title"] for item in music_cache if "title" in item]

        music_list = "\n".join(f"{i+1}. {title}" for i, title in enumerate(titles))
        if len(music_list) > 1900:  # Discord 消息长度限制
            music_list = music_list[:1900] + "\n…"

        await interaction.response.send_message(f"🎵 已缓存的曲子标题:\n{music_list}")
    @bot.tree.command(name="play_cache", description="播放已缓存的音乐")
    async def play_cache(interaction: discord.Interaction, title: str):
        await interaction.response.defer(thinking=True)
        # 检查用户是否在语音频道
        if not interaction.user.voice:
            await interaction.followup.send("⚠️ 请先加入语音频道")
            return

        # 查找对应缓存
        matched = next((item for item in music_cache if item.get("title") == title), None)
        if not matched:
            await interaction.followup.send(f"❌ 未找到标题为 '{title}' 的缓存曲子")
            return

        # 构建文件路径
        file_path = os.path.join(MUSIC_FOLDER, matched.get("file", matched.get("title"))) 

        if not os.path.exists(file_path):            
            # 重写路径
            filename_with_ext = os.path.basename(file_path)
            filename_with_ext = filename_with_ext.split("music")[-1]
            file_path = file_path.replace("/", "").replace("\\", "")
            file_path = os.path.join("music", filename_with_ext)
            file_path = file_path.replace("\\", "")
            await interaction.followup.send(f"{file_path}")
            
        try:
            # 加入语音频道
            if not interaction.user.voice:
                await interaction.followup.send("⚠️ 请先加入语音频道")
                return

            channel = interaction.user.voice.channel
            vc = interaction.guild.voice_client or await channel.connect()
            if vc.channel != channel:
                await vc.move_to(channel)

            if vc.is_playing():
                vc.stop()
            source = discord.FFmpegPCMAudio(file_path)
            await interaction.followup.send(f"🎵 正在播放缓存曲子: **{title}**")
            vc.play(source)

        except Exception as e:
            # 只发一次错误消息，避免重复 webhook
            await interaction.followup.send(f"❌ 播放失败:\n```{traceback.format_exc()}```")
    @bot.tree.command(name="reset_ai", description="重置 AI 聊天")
    async def reset_ai(interaction: discord.Interaction):
        user_id = interaction.user.id  # ✅ 使用 user 而不是 author
        if user_id in user_histories:
            del user_histories[user_id]
        await interaction.response.send_message("✅ AI 历史已重置。")
def channel(bot):
    client = OpenAI(
        api_key=os.getenv("OPENAI_API_KEY"),
        base_url="https://ai.nengyongai.cn/v1"
        #api_key=os.getenv("OPENAI_API_KEY2"),
        #base_url="https://openrouter.ai/api/v1",
    )

    @bot.event
    async def on_message(message: discord.Message):
        if message.author == bot.user:
            return

        if message.channel.id not in AI_CHAT_CHANNEL_IDS:
            return

        user_id = message.author.id
        channel_id = message.channel.id
        user_input = message.content

        # 初始化用户历史（按用户+频道）
        if user_id not in user_histories:
            user_histories[user_id] = {}
        if channel_id not in user_histories[user_id]:
            user_histories[user_id][channel_id] = [
                {"role": "system", "content": SYSTEM_PROMPT.get(channel_id, "你是一个乐于助人的机器人")}
            ]

        # 添加用户消息到该频道历史
        user_histories[user_id][channel_id].append({"role": "user", "content": user_input})

        try:
            # 一次性生成文本，不使用流式
            response = client.chat.completions.create(
                model="o4-mini",
                #model="deepseek/deepseek-r1-0528:free",
                messages=user_histories[user_id][channel_id]
            )

            reply = response.choices[0].message.content.strip()

            # 添加 AI 回复到该频道历史
            user_histories[user_id][channel_id].append({"role": "assistant", "content": reply})

            await message.channel.send(reply)

        except Exception as e:
            await message.channel.send(f"出错了：{e}")

        await bot.process_commands(message)














