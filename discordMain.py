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
async def play(interaction: discord.Interaction, query: str):
    # 检查用户是否在语音频道
    if not interaction.user.voice:
        await interaction.response.send_message("⚠️ 你需要先加入一个语音频道！")
        return

    # 加入/移动到用户频道
    channel = interaction.user.voice.channel
    vc = interaction.guild.voice_client
    if not vc:
        vc = await channel.connect()
    else:
        await vc.move_to(channel)

    await interaction.response.send_message(f"🔍 正在搜索：{query}")

    # yt-dlp 配置（优化版）
    ydl_opts = {
        'format': 'bestaudio/best',
        'cookiefile': 'cookies.txt',
        'extract_flat': True,
        'quiet': True,  # 减少日志
        'no_warnings': True,
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(f"ytsearch:{query}", download=False)
            if not info or not info['entries']:
                await interaction.followup.send("❌ 找不到视频！")
                return

            entry = info['entries'][0]
            url = entry['url']
            title = entry['title']

        # FFmpeg 配置（带错误处理和重连）
        ffmpeg_options = {
            'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5',
            'options': '-vn -b:a 96k',  # 优化音质和带宽
        }

        # 播放（优先使用原始流，避免探测失败）
        vc.stop()
        source = discord.FFmpegOpusAudio(url, **ffmpeg_options)
        vc.play(source)

        await interaction.followup.send(f"🎵 正在播放：**{title}**")

    except Exception as e:
        await interaction.followup.send(f"❌ 播放失败：{str(e)}")
        print(f"Error: {e}")


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



