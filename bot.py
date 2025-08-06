import discord
from discord import app_commands
from discord.ext import commands
import os
import commandsFunction

bot = commands.Bot(
    command_prefix='!',
    intents=discord.Intents.all()
)
commandsFunction.commands(bot)
@bot.event
async def on_ready():
    print(f'✅ 已登录为 {bot.user} (ID: {bot.user.id})')
    
    # 同步命令
    try:
        synced = await bot.tree.sync()
        print(f"已同步命令: {[cmd.name for cmd in synced]}")
    except Exception as e:
        print(f"命令同步错误: {e}")

# 运行机器人
bot.run(os.getenv('DISCORD_TOKEN'))