from discord.ext import commands

class BaseClose(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def close(self, ctx):
        if self.bot.name == 'LogClient':
            self.bot.WriteThread.emplace('CODE_STOP')
            print("WriteProcess Terminated.")
            await self.bot.close()
            return 0
        await ctx.reply("Goodbye!")
        await self.bot.close()
        return 0
    

class BaseCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def ping(self, ctx):
        await ctx.send(f"Pong.")
        return 0
