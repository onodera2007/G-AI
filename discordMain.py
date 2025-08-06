import discord
import random

AI_CHAT_CHANNEL_ID = 1401852954910130176

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
        random_message = random.choice(messages)
        await interaction.response.send_message(random_message)
        
AI_CHAT_CHANNEL_ID = 1401852954910130176  # 替换成你的频道ID

def channel(bot):
    @bot.event
    async def on_message(message: discord.Message):
        if message.author == bot.user:
            return
        
        # 只在特定频道回复
        if message.channel.id != AI_CHAT_CHANNEL_ID:
            return

        await message.channel.send(":thinking: ")
        await bot.process_commands(message)
