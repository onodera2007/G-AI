import discord
import random
from openai import AsyncOpenAI
from googleapiclient.discovery import build
import os
from discord.ext import commands
import traceback
import yt_dlp
import aiohttp
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
    @bot.tree.command(name="play_youtube", description="播放音乐(YouTube)→弃")
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

            # 第一步：用API搜索视频
            youtube = build("youtube", "v3", developerKey="AIzaSyAGByEES4phlLYo6G2pG_DfIsPHTFG0BRI")
            search_response = youtube.search().list(
                q=query,
                part="id,snippet",
                maxResults=1,
                type="video"
            ).execute()

            if not search_response.get("items"):
                await interaction.followup.send("❌ 找不到视频")
                return

            video_id = search_response["items"][0]["id"]["videoId"]
            title = search_response["items"][0]["snippet"]["title"]

            # 第二步：用yt-dlp获取音频流（不触发验证）
            ydl_opts = {
                'format': 'bestaudio/best',
                'quiet': True,
                'no_warnings': True,
                'extract_flat': False,
                'socket_timeout': 30
            }

            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(f"https://youtu.be/{video_id}", download=False)
                url = info['url']
                print(f"音频流URL: {url}")

            # 播放设置
            ffmpeg_options = {
                'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5',
                'options': '-vn -acodec libopus -b:a 96k'
            }

            vc.stop()
            source = discord.FFmpegOpusAudio(url, **ffmpeg_options)
            vc.play(source)

            await interaction.followup.send(f"🎵 正在播放: **{title}**")

        except Exception as e:
            await interaction.followup.send(f"❌ 播放失败: {str(e)}")
            print(f"完整错误: {traceback.format_exc()}")
    @bot.tree.command(name="play_bilibili", description="播放音乐(Bilibili)")
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



