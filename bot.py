"""
bot.py
Samuel Lee
4/12/2021

a bot for a discord server
very early initial prototype
I added way too many comments because this is just an internal
project that I'm using to learn the discord.py api
"""
import config
import random
import os
import discord
import re
import json
import sys
import datetime

from discord.ext import commands

# checks for and creates logs/messages/ and logs/bot/ directory
os.makedirs(os.path.join(os.getcwd(), os.path.dirname("logs/messages/")), exist_ok=True)
os.makedirs(os.path.join(os.getcwd(), os.path.dirname("logs/bot/")), exist_ok=True)

#sets up bot
intents = discord.Intents.default()
intents.members = True
bot = commands.Bot(command_prefix = config.prefix, intents = intents)


# on_ready() is called when the bot connects and is readied
@bot.event
async def on_ready():
    if not config.on_ready_ran:
        eventlog("on_ready called", "READY")
        startup()
        await config.operator_channel.send("Connected Successfully!")
        config.on_ready_ran = True
        eventlog("on_ready finish", "READY")
    else:
        print("Bot Reconnected")
        eventlog("Bot Reconnected", "READY")


# a function to parse messages
@bot.event
async def on_message(message):
    # skips bad recursion
    if message.author == bot.user:
        return
    
    # logs messages in the relative servers message log
    if config.message_logging:
        logdir = f"logs/messages/{message.guild.id}/{message.channel.name}.txt"
        mentions = ""
        if len(message.mentions) != 0:
            for user in message.mentions:
                mentions += f"\n\t{user.name} : {user.id}"
        else:
            mentions = "\n\tNone"
        with open(os.path.join(os.getcwd(), logdir), mode="a") as log:
            lines = f"\nMessage ID: {message.id}\nAuthor: {message.author}\nTime: {message.created_at}\nMentions: {mentions}\nContents:\n" + "-"*35 + f"\n{message.content}\n" + "-"*35 + "\n"
            log.write(lines)

    # records bot mentions
    if f"<@{bot.user.id}>" in message.content or f"<@!{bot.user.id}>" in message.content:
        config.mentions += 1
        print("Bot was mentioned")
        await message.channel.send(f"{message.author.mention} no you.")

    #increment stat
    config.messages += 1
    print(f"New message sent: total = {config.messages}")

    # checks for keywords and replies
    for word in config.words_list:
        if message.content.find(word) != -1:
            rand_emoji = random.choice(config.emoji_list)
            await message.channel.send(rand_emoji)
            break
        
    await bot.process_commands(message)


# records deletion of known messages
@bot.event
async def on_message_delete(message):
    if message.author == bot.user:
        return
    
    if message.guild.name in config.bound_text_channels.keys():
        timestamp = datetime.datetime
        record = ""
        record += f"Author Name: {message.author.name}\nAuthor ID: {message.author.id}\n"
        record += f"Channel Name: {message.channel.name}\nChannel ID: {message.channel.id}\n"
        record += f"Time Created: {str(message.created_at)}\nDeleted at: {str(timestamp.now())}\n"
        if len(message.attachments) > 0:
            record += "Attachments:\n"
            for attach in message.attachments:
                record += "\t" + str(attach) + "\n"
        record += "Content:\n"
        record += "\t" + message.content

        await message.guild.get_channel(config.bound_text_channels[message.guild.name]).send(record)


# sets a main channel for the guild and channel this command was called in
@bot.command()
async def set_default_channel(ctx):
    print("!set_default_channel called")
    if not ctx.author.guild_permissions.administrator:
        print("Unauthorized user called set_default_channel")
        eventlog(f"Unauthorized set_default_channel called by {ctx.author.name}", "ERR")
        return
    config.bound_text_channels[f"{ctx.guild}"] = ctx.message.channel.id
    print(f"{ctx.guild} = {ctx.message.channel.id}")
    await ctx.send(f"This channel was bound as {ctx.guild}'s Jester_ channel!")


# makes fun of rythm bot
@bot.command()
async def play(ctx):
    print("!play called")
    rand_emoji = random.choice(config.emoji_list)
    await ctx.send(f"<@235088799074484224> is a {rand_emoji}")
    eventlog("play command called", "CMD")


# alias for play()
@bot.command()
async def p(ctx):
    await play(ctx)


# cute take on ping and pong
@bot.command()
async def ping(ctx):
    await ctx.send("What does a battle rifle have in common with a microwave?")
    eventlog("ping command called", "CMD")


# cute tak on ping and pong
@bot.command()
async def pong(ctx):
    await ctx.send("They both go 'ping' when they're done.")
    eventlog("pong command called", "CMD")


# clear a text channel of 500 newest messages
@bot.command()
async def jester_purge(ctx):
    if ctx.author.name != config.operator:
        ctx.send("Invalid user")
        return
    await ctx.channel.purge(limit = 500)


# refreshes emojis
@bot.command()
async def refresh(ctx):
    refresh()


# toggles logging of messages
@bot.command()
async def log(ctx, event=None, message=None): 
    if not ctx.author.guild_permissions.administrator:
        print(f"Unauthorized user {ctx.author.name} called log")
        eventlog(f"Unauthorized LOG event called by {ctx.author.name}", "ERR")
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
    
    eventlog("Logging toggled", "CMD")


# creates a graceful shutdown of this bot
# runs the writeout method in config.py
@bot.command()
async def close(ctx):
    if ctx.author.name != config.operator:
        print(f"someone unauthorized tried to close the bot: {ctx.author.name}")
        eventlog(f"Unauthorized CLOSE Event Called by {ctx.author.name}", "ERR")
        return

    await ctx.send("Starting Graceful Shutdown...")

    config.graceful_end = True
    config.writeout()
    
    await ctx.send("Done!")
    
    eventlog("Close Event", "CLOSE")
    
    await bot.close()


# prints some bot related info pulled from config
# does some other things I had in on_ready()
def startup():
    print(f"Total Messages recorded = {config.messages}\nBot mentions = {config.mentions}\nLast Shutdown Graceful = {config.graceful_end}")
    print(f"Bot token = {config.token}\nGuild = {config.main_guild}\nCommand prefix = {config.prefix}")
    print(f"Message logging = {config.message_logging}")
    print(f"Event logging = {config.event_logging}")
    print(f"Operator discord name: {config.operator}")

    for key in config.bound_text_channels.keys():
        print(f"\t{key} : {config.bound_text_channels[key]}")

    for guild in bot.guilds:
            os.makedirs(os.path.join(os.getcwd(), os.path.dirname(f"logs/messages/{guild.id}/")), exist_ok=True)
    
    # check and response for an abrupt previous shutdown
    if not config.graceful_end:
        print("The previous shutdown was NOT graceful!\nSome data has been lost!")
    config.graceful_end = False
    config.writeout()
    
    # creates emojis
    refresh()

    # cute header with guild and self info
    print("*"*35 + "\n")
    print(f"\n{bot.user} has successfully connected to Discord and is readied!")
    if config.main_guild != "None" and config.main_guild in config.bound_text_channels.keys():
        temp_guild = discord.utils.find(lambda g: g.name == config.main_guild, bot.guilds)    
        config.operator_channel = temp_guild.get_channel(config.bound_text_channels[config.main_guild])
    print("*"*35 + "\n")   

    # prints a list of guilds and members attached to their nicknames
    print("Guilds: ")
    for guild in bot.guilds:
        print(f"{guild.name} - Members:")
        for member in guild.members:
            if member.nick != None:
                print(f"\t - '{member.name}' has the nickname '{member.nick}'")
            else:
                print(f"\t - '{member.name}'") 

# creates easy to use emojis for the bot
def refresh():
    for emoji in bot.emojis:
        if emoji.animated:
            config.emojis[emoji.name] = f"<a:{emoji.name}:{emoji.id}>"
        else:
            config.emojis[emoji.name] = f"<:{emoji.name}:{emoji.id}>"
        config.emoji_list.append(config.emojis[emoji.name])


# used by other functions to log what happens when
# not really useful for anyone but me
def eventlog(message, stream):
    if not config.event_logging:
        return
    
    date = datetime.datetime
    timestamp = date.now()
    logdir = f"logs/bot/eventlog.txt"
    
    with open(os.path.join(os.getcwd(), logdir), mode="a") as log:
        log.write(f"{timestamp} {stream}:\t{message}\n")


# runs the bot object and connects
# prints a shutdown message and a separator
if __name__ == "__main__":
    bot.run(config.token)
    print("SHUTDOWN COMPLETE")
    print("*"*35 + "\n\n\n")
