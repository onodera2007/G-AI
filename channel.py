def main(bot):
    @bot.event
    async def on_message(message):
        if message.author == bot.user:
            return  # 不响应自己
        if message.channel.name != "ai-chat":
            return  # 只响应 ai-chat 频道
        await message.channel.send(f"你在 ai-chat 说了：{message.content}")
        # 确保其他命令仍然可用
        await bot.process_commands(message)