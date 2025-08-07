import discord
from discord.ext import commands
import openai
import os

openai.api_key = os.getenv("OPENAI_API_KEY")
def main(bot):
    @bot.event
    async def on_message(message):
        if message.author == bot.user:
            return  # 忽略自己的消息
        if message.channel.name != "ai-chat":
            return  # 只响应 ai-chat 频道

        # 获取用户的消息
        user_input = message.content

        # 使用 ChatGPT 获取回复
        try:
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "你是一个乐于助人的 Discord 聊天机器人"},
                    {"role": "user", "content": user_input}
                ],
                temperature=0.7,
                max_tokens=200
            )
            reply = response['choices'][0]['message']['content'].strip()
        except Exception as e:
            reply = f"出错了：{e}"

        await message.channel.send(reply)

        # 继续处理其他命令
        await bot.process_commands(message)