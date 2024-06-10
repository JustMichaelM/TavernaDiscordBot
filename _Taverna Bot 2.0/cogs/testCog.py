import discord
from discord.ext import commands

class ContextMenus(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # Definiowanie context menu dla wiadomości
    @discord.message_command(name="Translate to Pig Latin")
    async def translate_pig_latin(self, ctx: discord.ApplicationContext, message: discord.Message):
        def to_pig_latin(word):
            vowels = "aeiou"
            if word[0] in vowels:
                return word + "way"
            else:
                return word[1:] + word[0] + "ay"
    
        translated_message = ' '.join(to_pig_latin(word) for word in message.content.split())
        await ctx.respond(f"Translated Message: {translated_message}")

    # Definiowanie context menu dla użytkowników
    @discord.user_command(name="Say Hello")
    async def say_hello(self, ctx: discord.ApplicationContext, user: discord.User):
        await ctx.respond(f"Hello, {user.name}!")

async def setup(bot):
    await bot.add_cog(ContextMenus(bot))
