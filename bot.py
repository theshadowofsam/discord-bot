"""
bot.py
Samuel Lee
4/12/2021

a bot for a discord server
very early initial prototype
i added way too many comments because this is just an internal
project that i am using to learn the discord api
"""
import random
import os
import discord
import re
import configparser as cp

from discord.ext import commands
from dotenv import load_dotenv
from threading import Thread

# the next 33 lines are all global variables which is why
# they arent in a function. I should make this a class

# loads config file using configparser module
config = cp.ConfigParser()
config.read("config.ini")

# intitalizes config file values as global vars
# also prints them to python console for confirmation
TOTAL_MESSAGES_SENT = config.getint('STATS', 'total_messages_sent')
BOT_MENTIONS = config.getint('STATS', 'bot_mentions')
LAST_SHUTDOWN_GRACEFUL = config.getboolean('STATS', 'last_shutdown_graceful')

print("local values:")
print(f"TOTAL_MESSAGES_SENT = {TOTAL_MESSAGES_SENT}")
print(f"BOT_MENTIONS = {BOT_MENTIONS}")
print(f"LAST_SHUTDOWN_GRACEFUL = {LAST_SHUTDOWN_GRACEFUL}")

TOKEN = config['ENV']['TOKEN']
GUILD = config['ENV']['GUILD']
PREFIX = config['ENV']['PREFIX']

print(f"TOKEN = {TOKEN}")
print(f"GUILD = {GUILD}")
print(f"PREFIX = {PREFIX}")


# creating intents for the bot 
# my understanding is that these are more specialized permissions???
intents = discord.Intents.default()
intents.members = True # not sure what this is for look up the documentation later


# creates the discord bot object
bot = commands.Bot(command_prefix = '!', intents = intents)


# on_ready() is called when the bot connects apparently so everything
# in here will run 
@bot.event
async def on_ready():
    
    # check and response for an abrupt previous shutdown
    global LAST_SHUTDOWN_GRACEFUL
    if not LAST_SHUTDOWN_GRACEFUL:
        print("\nThe previous shutdown was NOT graceful!\nSome data has been lost!\n")


    config['STATS']['LAST_SHUTDOWN_GRACEFUL'] = "False"
    with open("config.ini", 'w') as conf:
        config.write(conf)
    
    
    # I designed the bot for the GUILD env variable guild 
    # coincidentally this is the first time I have used a lambda function
    # this sets the guild to be the guild in bot.guilds of name GUILD
    guild = discord.utils.find(lambda g: g.name == GUILD, bot.guilds)

    # setting some global variables
    global main_text_channel 
    main_text_channel = guild.get_channel(311217930522066944)
    
    global emojis
    emojis = {}
    
    global emoji_list
    emoji_list = []
    
    # keywords that on_message() uses
    global words_list
    words_list = [
        "nerd",
        "ape",
        "smoothbrain"
    ]

    # creates easy to use emojis for the bot
    for emoji in guild.emojis:
        if emoji.animated:
            emojis[emoji.name] = f"<a:{emoji.name}:{emoji.id}>"
        else:
            emojis[emoji.name] = f"<:{emoji.name}:{emoji.id}>"

    for emoji in emojis.values():
        emoji_list.append(emoji)

    # cute header with guild and self info
    print("*"*35)
    print(f"{bot.user} has successfully connected to Discord!")
    if guild.name == GUILD:
            print("In correct guild.")
    print(f"{bot.user} is connected to: \n{guild.name}(id: {guild.id})")
    print("*"*35)    

    # prints a list of guild members attached to their nicknames
    print("Guild Memebers: ")
    for member in guild.members:
        if member.nick != None:
            print(f" - {member.name} has the nickname {member.nick}")
        else:
            print(f" - {member.name}")
    
    #prints a message in discord when the bot comes online
    await main_text_channel.send("Successfuly Joined")


# a function to parse messages
@bot.event
async def on_message(message):

    # random emoji used in some replies
    rand_emoji = random.choice(emoji_list)
    # skips bad recursion
    if message.author == bot.user:
        return
    
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
            await channel.send(f'{author.mention} was naughty and deleted the following message:\n\n"{payload.cached_message.content}"')
            break


# responds to !gay
@bot.command()
async def gay(ctx):
    print("!gay called")
    emoji = "noog"
    await ctx.send(f"@everyone is a {emojis[emoji]}")


# makes fun of rythm bot
@bot.command()
async def play(ctx):
    print("!play called")
    emoji = "noog"
    
    await ctx.send(f"<@235088799074484224> is a {emojis[emoji]}")


# alias for play()
@bot.command()
async def p(ctx):
    await play(ctx)


@bot.command()
async def ping(ctx):
    await ctx.send("What does a battle rifle have in common with a microwave?")


@bot.command()
async def pong(ctx):
    await ctx.send("They both go 'ping' when they're done.")


# creates a graceful shutdown of this bot
# writes new config stats using configparser
@bot.command()
async def close(ctx):
    if ctx.author.name != "theshadowofsam":
        return
    await ctx.send("Starting Graceful Shutdown...")

    config['STATS']['TOTAL_MESSAGES_SENT'] = str(TOTAL_MESSAGES_SENT)
    config['STATS']['BOT_MENTIONS'] = str(BOT_MENTIONS)
    config['STATS']['LAST_SHUTDOWN_GRACEFUL'] = "True"

    with open("config.ini", 'w') as conf:
        config.write(conf)

    await ctx.send("Done!")
    await bot.close()


# runs the bot object and connects
# prints a shutdown message and a separator
bot.run(TOKEN)
print("Shutdown")
print("*"*35 + "\n\n\n")
