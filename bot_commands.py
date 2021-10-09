from discord.ext import commands

@commands.command()
async def import_test(ctx):
    await ctx.send("PASS")

def setup(bot):
    bot.add_command(import_test)
    