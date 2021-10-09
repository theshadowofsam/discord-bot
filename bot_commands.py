from discord.ext import commands
import config
import Jester


@commands.command()
async def import_test(ctx):
    await ctx.send("PASS")


# sets a main channel for the guild and channel this command was called in
@commands.command()
async def set_default_channel(ctx):
    print("!set_default_channel called")
    if not ctx.author.guild_permissions.administrator:
        print("Unauthorized user called set_default_channel")
        bot.eventlog(f"Unauthorized set_default_channel called by {ctx.author.name}", "ERR")
        return
    config.bound_text_channels[f"{ctx.guild}"] = ctx.message.channel.id
    print(f"{ctx.guild} = {ctx.message.channel.id}")
    await ctx.send(f"This channel was bound as {ctx.guild}'s Jester_ channel!")


# makes fun of rythm bot
@commands.command()
async def play(ctx):
    print("!play called")
    rand_emoji = random.choice(config.emoji_list)
    await ctx.send(f"<@235088799074484224> is a {rand_emoji}")
    Jester.eventlog("play command called", "CMD")


# alias for play()
@commands.command()
async def p(ctx):
    await play(ctx)


# cute take on ping and pong
@commands.command()
async def ping(ctx):
    await ctx.send("What does a battle rifle have in common with a microwave?")
    Jester.eventlog("ping command called", "CMD")


# cute tak on ping and pong
@commands.command()
async def pong(ctx):
    await ctx.send("They both go 'ping' when they're done.")
    Jester.eventlog("pong command called", "CMD")


# clear a text channel of 500 newest messages
@commands.command()
async def jester_purge(ctx):
    if ctx.author.name != config.operator:
        ctx.send("Invalid user")
        return
    await ctx.channel.purge(limit = 500)


# refreshes emojis
@commands.command()
async def refresh(ctx):
    refresh()


# toggles logging of messages
@commands.command()
async def log(ctx, event=None, message=None): 
    if not ctx.author.guild_permissions.administrator:
        print(f"Unauthorized user {ctx.author.name} called log")
        Jester.eventlog(f"Unauthorized LOG event called by {ctx.author.name}", "ERR")
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
    
    Jester.eventlog("Logging toggled", "CMD")



def setup(bot):
    bot.add_command(import_test)
    bot.add_command(set_default_channel)
    bot.add_command(play)
    bot.add_command(p)
    bot.add_command(ping)
    bot.add_command(pong)
    bot.add_command(jester_purge)
    bot.add_command(refresh)
    bot.add_command(log)
