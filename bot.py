import discord
from discord.ext import commands
import os
import discordMain
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
discordMain.commands(bot)
discordMain.channel(bot)
@bot.event
async def on_ready():
    print(f'✅ 已登录为 {bot.user} (ID: {bot.user.id})')
    
    # 同步命令
    try:
        synced = await bot.tree.sync()
        print(f"已同步命令: {[cmd.name for cmd in synced]}")
    except Exception as e:
        print(f"命令同步错误: {e}")
if not os.path.exists('cookies.txt'):
    print("❌ cookies.txt 不存在！")
else:
    print("✅ cookies.txt 已找到，开始运行...")
# 运行机器人
bot.run(os.getenv('DISCORD_TOKEN'))
