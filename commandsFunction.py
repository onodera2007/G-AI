import discord
from discord import app_commands
from discord.ext import commands
import os
import asyncio
import random

def commands(bot):
    @bot.tree.command(name="test", description="测试命令")
    async def test(interaction: discord.Interaction):
        await interaction.response.send_message("🔄 测试成功！")
    @bot.tree.command(name="meme_cn", description="梗")
    async def meme_cn(interaction: discord.Interaction):
    # 定义消息列表
        messages = [
        ":raised_hand: :rofl: :raised_back_of_hand:",
        ":raised_hand: <:emoji_name:1401903542377381998> :raised_back_of_hand: ",
        ":raised_hand: :sob: :raised_back_of_hand: ",
        "那一天的🦑，🦑起来！"
        ]
    
    # 随机选择一条消息
        random_message = random.choice(messages)
        await interaction.response.send_message(random_message)