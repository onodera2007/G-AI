import discord
import random
from openai import AsyncOpenAI
from googleapiclient.discovery import build
import os
from discord.ext import commands
import traceback
import yt_dlp
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
YOUTUBE_API_KEY = "AIzaSyAGByEES4phlLYo6G2pG_DfIsPHTFG0BRI"
AI_CHAT_CHANNEL_ID = 1401852954910130176
ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
cookies_path = os.path.join(ROOT_DIR, "cookies.txt")
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
    @bot.tree.command(name="play", description="播放音乐")
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
            youtube = build("youtube", "v3", developerKey=YOUTUBE_API_KEY)
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


    @bot.tree.command(name="stop", description="停止播放并离开频道")
    async def stop(interaction: discord.Interaction):
        if interaction.guild.voice_client:
            await interaction.guild.voice_client.disconnect()
            await interaction.response.send_message("⏹ 已停止播放并退出频道")
        else:
            await interaction.response.send_message("⚠️ 我不在语音频道里")


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



