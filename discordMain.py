# 标准库
import json
import os
import random
import traceback
# 第三方库
import discord
from discord.ext import commands
import yt_dlp
from openai import AsyncOpenAI
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
AI_CHAT_CHANNEL_ID = 1401852954910130176
SEARCH_PROXY = "https://bilibili-proxy.vercel.app/search"
CACHE_FILE = "music.json"
MUSIC_FOLDER = "music" 
if os.path.exists(CACHE_FILE):
    with open(CACHE_FILE, "r", encoding="utf-8") as f:
        music_cache = json.load(f)
else:
    music_cache = {}

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

        # yt-dlp 搜索
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

            ydl_opts = {
                "format": "bestaudio/best",
                "quiet": True,
                "no_warnings": True,
                "cookies": "cookies.txt",  # 如果需要登录，可提前导出 cookies
            }

            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                # 判断输入类型：BV号或关键字
                if query.startswith("BV") and len(query) == 12:  # BV号长度固定12位
                    video_url = f"https://www.bilibili.com/video/{query}"
                    info = ydl.extract_info(video_url, download=False)
                else:
                    # 关键字搜索
                    info = ydl.extract_info(f"bilisearch:{query}", download=False)
                    if not info or "entries" not in info or len(info["entries"]) == 0:
                        await interaction.followup.send("❌ 没有找到视频")
                        return
                    info = info["entries"][0]

            # 获取音频 URL
            audio_url = info["url"]
            title = info.get("title", "未知标题")
            extractor = info.get("extractor")

            print("网站:", extractor)
            print("标题:", title)
            print("音频 URL:", audio_url)

            # 播放设置
            ffmpeg_options = {
                "before_options": "-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5",
                "options": "-vn -acodec libopus -b:a 96k"
            }

            vc.stop()
            source = discord.FFmpegOpusAudio(audio_url, **ffmpeg_options)
            vc.play(source)

            await interaction.followup.send(f"🎵 正在播放: **{title}**")

        except Exception as e:
            await interaction.followup.send(f"❌ 播放失败: {str(e)}")
            
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
        # 检查用户是否在语音频道
        if not interaction.user.voice:
            await interaction.response.send_message("⚠️ 请先加入语音频道")
            return

        # 查找对应缓存
        matched = next((item for item in music_cache if item.get("title") == title), None)
        if not matched:
            await interaction.response.send_message(f"❌ 未找到标题为 '{title}' 的缓存曲子")
            return

        # 构建文件路径
        file_path = os.path.join(MUSIC_FOLDER, matched.get("file", matched.get("title"))) 

        if not os.path.exists(file_path):
            await interaction.response.send_message(f"❌ 文件不存在: {file_path}，重写中...")
            
            # 重写路径
            filename_with_ext = os.path.basename(file_path)
            await interaction.followup.send(f"{filename_with_ext}")
            filename_with_ext = filename_with_ext.split("music")[-1]
            file_path = file_path.replace("/", "").replace("\\", "")
            file_path = os.path.join("music/", filename_with_ext)
            file_path = file_path.replace("\\", "")
            
        try:
            # 加入语音频道
            channel = interaction.user.voice.channel
            vc = interaction.guild.voice_client or await channel.connect()
            if vc.channel != channel:
                await vc.move_to(channel)

            await interaction.followup.send(f"🎵 正在播放缓存曲子: **{title}**")
            await interaction.followup.send(f"当前路径是**{file_path}**")
            ffmpeg_options = {
                "before_options": "-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5",
                "options": "-vn -acodec libopus -b:a 96k"
            }

            vc.stop()
            source = discord.FFmpegPCMAudio(file_path)
            print(f"正在播放缓存曲子: {file_path}")
            vc.play(source)

        except Exception as e:
            await interaction.followup.send(f"❌ 播放失败: {str(e)}")
            print(f"完整错误: {traceback.format_exc()}")
def channel(bot):
    client = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    @bot.event
    async def on_message(message: discord.Message):
        
        if message.author == bot.user:
            return
        
        # 只在特定频道回复
        if message.channel.id != AI_CHAT_CHANNEL_ID:
            return

        user_input = message.content

        # 使用 ChatGPT 获取回复
        try:
            response = await client.chat.completions.create(
            model="gpt-5-chat-latest",
            messages=[
                {"role": "system", "content": "你是一个乐于助人的 Discord 聊天机器人"},
                {"role": "user", "content": user_input}
            ],
            temperature=0.7,
            max_tokens=200
        )
            reply = response.choices[0].message.content.strip()
        except Exception as e:
            reply = f"出错了：{e}"

        await message.channel.send(reply)

    # 继续处理其他命令

        await bot.process_commands(message)


















