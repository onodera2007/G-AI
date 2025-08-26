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

bot2 = commands.Bot(
    command_prefix='2',
    intents=discord.Intents.all()
)

discordMain.anydesk(bot2)
discordMain.commands2(bot2)

@bot2.event
async def on_ready():
    print(f'✅ 已登录为 {bot2.user} (ID: {bot2.user.id})')
    
    # 同步命令
    try:
        synced = await bot2.tree.sync()
        print(f"已同步命令: {[cmd.name for cmd in synced]}")
    except Exception as e:
        print(f"命令同步错误: {e}")
# 运行机器人
bot2.run(os.getenv('BOT_TOKEN2'))
