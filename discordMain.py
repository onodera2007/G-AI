import discord
import random
from openai import AsyncOpenAI
import os
from discord.ext import commands
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
    @bot.tree.command(name="play", description="播放音乐 (YouTube 搜索或链接)")
    async def play(interaction: discord.Interaction,query: str):
        if interaction.user.voice is None:
            await interaction.response.send_message("⚠️ 你需要先加入一个语音频道！")
            return

        channel = interaction.user.voice.channel

        # 如果 bot 不在语音频道，就加入
        if interaction.guild.voice_client is None:
            await channel.connect()
        else:
            await interaction.guild.voice_client.move_to(channel)

        await interaction.response.send_message(f"🔍 正在搜索：{query}")

        # yt-dlp 解析音源
        ydl_opts = {
        'format': 'bestaudio/best',
        'cookiefile': 'cookies.txt',  # 直接指向根目录的 cookies.txt
        'extract_flat': True,  # 使用刚写入的 cookies
        }
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(f"ytsearch:{query}", download=False)["entries"][0]
            url = info["url"]
            title = info["title"]

        # 播放
        ffmpeg_options = {"options": "-vn"}
        vc = interaction.guild.voice_client
        vc.stop()  # 停止之前的音乐
        source = await discord.FFmpegOpusAudio.from_probe(url, **ffmpeg_options)
        vc.play(source)

        await interaction.followup.send(f"🎵 正在播放：**{title}**")


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



