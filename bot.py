"""
bot.py
Samuel Lee
4/12/2021

a bot for a discord server
very early initial prototype
I added way too many comments because this is just an internal
project that I'm using to learn the discord.py api
"""
import random
import os
import discord
import re
import json
import sys

from discord.ext import commands


# parsing config and setting global variables
# prints them all to console for confirmation
with open("config.json") as jf:
    config = json.load(jf)

TOTAL_MESSAGES_SENT = config["stats"]["total_messages_sent"]
BOT_MENTIONS = config["stats"]["bot_mentions"]
LAST_SHUTDOWN_GRACEFUL = config["stats"]["last_shutdown_graceful"]
print(f"Total Messages recorded = {TOTAL_MESSAGES_SENT}\nBot mentions = {BOT_MENTIONS}\nLast Shutdown Graceful = {LAST_SHUTDOWN_GRACEFUL}")

TOKEN = config["env"]["token"]
GUILD = config["env"]["guild"]
PREFIX = config["env"]["prefix"]
print(f"Bot Token = {TOKEN}\nGuild = {GUILD}\nCommand Prefix = {PREFIX}")

BOT_TEXT_CHANNELS = config["bot_text_channels"]

LOGGING = config["env"]["logging"]
print(f"LOGGING = {LOGGING}")

OPERATOR = config["operator"]
print(f"Operator discord name: {OPERATOR}")

print(f"Bound Bot Guilds and Channels:")
for key in BOT_TEXT_CHANNELS.keys():
    print(f"\t{key} : {BOT_TEXT_CHANNELS[key]}")

# checks for and creates logs/messages/ directory
os.makedirs(os.path.join(os.getcwd(), os.path.dirname("logs/messages/")), exist_ok=True)


# creating intents for the bot 
intents = discord.Intents.default()
intents.members = True


# creates the discord bot object
bot = commands.Bot(command_prefix = PREFIX, intents = intents)


# on_ready() is called when the bot connects and is readied
@bot.event
async def on_ready():
    

    # check and response for an abrupt previous shutdown
    global LAST_SHUTDOWN_GRACEFUL
    if not LAST_SHUTDOWN_GRACEFUL:
        print("\nThe previous shutdown was NOT graceful!\nSome data has been lost!\n")
    config["stats"]["last_shutdown_graceful"] = False
    with open("config.json", 'w') as conf:
        json.dump(config, conf, separators=(",\n", ":"), indent="")
    LAST_SHUTDOWN_GRACEFUL = False
    

    # sets main_guild to be the guild of name GUILD in the config
    # if one is present
    global main_guild
    global main_guild_exists
    try:
        main_guild = discord.utils.find(lambda g: g.name == GUILD, bot.guilds)
        main_guild_exists = True
    except Exception() as e:
        print(f"A GUILD error occurred: {e}")
        main_guild_exists = False


    # setting some more global variables
    global main_guild_text_channel
    global emojis
    emojis = {}
    global emoji_list
    emoji_list = []    
    if main_guild_exists:
        main_guild_text_channel = main_guild.get_channel(BOT_TEXT_CHANNELS[GUILD])
        print(main_guild)
        print(main_guild_text_channel)

    
    # keywords that on_message() uses
    global words_list
    words_list = [
        "bot",
        "nerd",
        "machine",
    ]


    # creates easy to use emojis for the bot
    for guild in bot.guilds:
        for emoji in guild.emojis:
            if emoji.animated:
                emojis[emoji.name] = f"<a:{emoji.name}:{emoji.id}>"
            else:
                emojis[emoji.name] = f"<:{emoji.name}:{emoji.id}>"
            emoji_list.append(emoji.name)


    # cute header with guild and self info
    print("*"*35 + "\n")
    print(f"\n{bot.user} has successfully connected to Discord and is readied!")
    if main_guild_exists:
        print(f"{bot.user} has access to Main Guild: \n\t{main_guild.name}(id: {main_guild.id})\n")
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
    

    #prints a message in discord when the bot comes online
    if main_guild_exists:
        await main_guild_text_channel.send("Successfuly Joined")


# a function to parse messages
@bot.event
async def on_message(message):
    # skips bad recursion
    if message.author == bot.user:
        return
    

    if LOGGING:
        logdir = f"logs/messages/{message.guild.id}.txt"
        with open(os.path.join(os.getcwd(), logdir), mode="a") as log:
            lines = f"\nMessage ID: {message.id}\nAuthor: {message.author}\nTime: {message.created_at}\nContents:\n" + "-"*35 + f"\n{message.content}\n" + "-"*35 + "\n"
            log.write(lines)

    
    # random emoji used in some replies
    rand_emoji = random.choice(emoji_list)
    

    # records bot mentions
    if f"<@{bot.user.id}>" in message.content or f"<@!{bot.user.id}>" in message.content:
        global BOT_MENTIONS
        BOT_MENTIONS += 1
        print("Bot was mentioned")
        await message.channel.send(f"{message.author.mention} no you.")


    #increment stat
    global TOTAL_MESSAGES_SENT
    TOTAL_MESSAGES_SENT += 1
    print(f"New message sent: total = {TOTAL_MESSAGES_SENT}")

    # checks for keywords and replies
    for word in words_list:
        if message.content.find(word) != -1:
            await message.channel.send(rand_emoji)
            break
    await bot.process_commands(message)


# message delete event with response
@bot.event
async def on_raw_message_delete(payload):
    if payload.cached_message is None:
        return
    guild_id = payload.guild_id
    channel_id = payload.channel_id
    guild = bot.get_guild(guild_id)
    for channel in guild.text_channels:
        if channel.id == channel_id:
            if payload.cached_message.author.bot:
                return
            author = payload.cached_message.author
            await channel.send(f'{author.mention} was naughty and deleted the following message:\n"{payload.cached_message.content}"')
            break


# sets a main channel for the guild and channel this command was called in
@bot.command()
async def set_default_channel(ctx):
    print("!set_default_channel called")
    if not ctx.author.guild_permissions.administrator:
        print("Unauthorized user called set_default_channel")
        return
    global BOT_TEXT_CHANNELS
    BOT_TEXT_CHANNELS[f"{ctx.guild}"] = ctx.message.channel.id
    print(f"{ctx.guild} = {ctx.message.channel.id}")
    await ctx.send(f"This channel was bound as {ctx.guild}'s Jester_ channel!")


# makes fun of rythm bot
@bot.command()
async def play(ctx):
    print("!play called")
    rand_emoji = random.choice(emoji_list)
    await ctx.send(f"<@235088799074484224> is a {rand_emoji}")


# alias for play()
@bot.command()
async def p(ctx):
    await play(ctx)

# cute take on ping and pong
@bot.command()
async def ping(ctx):
    await ctx.send("What does a battle rifle have in common with a microwave?")

# cute tak on ping and pong
@bot.command()
async def pong(ctx):
    await ctx.send("They both go 'ping' when they're done.")


@bot.command()
async def log(ctx):
    global LOGGING
    if not ctx.author.guild_permissions.administrator:
        print(f"Unauthorized user {ctx.author} called log")
        return
    
    if LOGGING:
        LOGGING = False
    else:
        LOGGING = True    
    
    if ctx.guild.name in BOT_TEXT_CHANNELS.keys():
        channel = discord.utils.get(ctx.guild.text_channels, id=BOT_TEXT_CHANNELS[ctx.guild.name])
        if LOGGING:
            await channel.send("Began Logging")
        else:
            await channel.send("Stopped Logging")
    else:
        if LOGGING:
            await ctx.send("Began Logging")
        else:
            await ctx.send("Stopped Logging")


# creates a graceful shutdown of this bot
# writes new config stats
@bot.command()
async def close(ctx):
    if ctx.author.name != OPERATOR:
        print(f"someone unauthorized tried to close the bot: {ctx.author.name}")
        return
    await ctx.send("Starting Graceful Shutdown...")

    config['stats']['total_messages_sent'] = TOTAL_MESSAGES_SENT
    config['stats']['bot_mentions'] = BOT_MENTIONS
    config['stats']['last_shutdown_graceful'] = True
    config['env']['logging'] = LOGGING

    with open("config.json", 'w') as conf:
        json.dump(config, conf, separators=(",\n", ":"), indent="")

    await ctx.send("Done!")
    await bot.close()


# runs the bot object and connects
# prints a shutdown message and a separator
bot.run(TOKEN)
print("SHUTDOWN COMPLETE")
print("*"*35 + "\n\n\n")
