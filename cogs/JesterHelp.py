"""
Samuel Lee
12/20/2021
JesterHelp.py

This is a cog for Jester.py, the discord bot
it contains the Help command and all related functions/commands

UNUSED CURRENTLY
"""
import discord
from discord.ext import commands
import config


class JesterHelp(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    
    @commands.command(aliases=["h"])
    async def help(self, ctx):
        print(self.bot.cogs)
        response = ''
        for cogname, cog in self.bot.cogs.items():
            response += f"'{cogname}' has commands:\n"
            commandlist = cog.get_commands()
            for c in commandlist:
                if len(c.aliases)>0:
                    response += f"\t-{c.name} has aliases: {' '.join(c.aliases)}\n"
                else:
                    response += f"\t-{c.name}\n"
        await ctx.author.send(response)
        

async def setup(bot):
    await bot.add_cog(JesterHelp(bot))
