"""
bot.py
Samuel Lee
4/12/2021

a bot for a discord server
very early initial prototype
I added way too many comments because this is just an internal
project that I'm using to learn the discord.py api
"""
import discord
from discord.ext import commands

import config

import json
import random
import os
import re
import sys
import datetime


# checks for and creates logs/messages/ and logs/bot/ directory
os.makedirs(os.path.join(os.getcwd(), os.path.dirname("logs/messages/")), exist_ok=True)
os.makedirs(os.path.join(os.getcwd(), os.path.dirname("logs/messages/private/")), exist_ok=True)
os.makedirs(os.path.join(os.getcwd(), os.path.dirname("logs/bot/")), exist_ok=True)


# sets up bot
intents = discord.Intents.default()
intents.members = True
bot = commands.Bot(command_prefix = config.prefix, intents = intents, help_command=None)


#load cogs
for c in [fn.split(".")[0] for fn in os.listdir(path="cogs") if fn.endswith(".py") and not fn.startswith("TEST")]:
    bot.load_extension(f"cogs.{c}")


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
    
    # stupid reply based on chance if any replies exist
    if config.chancing and message.author.name in config.reply_users.keys():
        if random.random() <= 1/config.random_chance:
            try:
                await message.reply(random.choice(config.reply_users[message.author.name]))
            except Exception as e:
                await message.reply(f"{type(e)}: {e}")

    # logs messages in the relative servers/private message log
    if config.message_logging:
        if message.channel.type == discord.ChannelType.private:
            logdir = f"logs/messages/private/{message.author.name}.txt"
        else:
            logdir = f"logs/messages/{message.guild.name}/{message.channel.name}.txt"

        mentions = ""
        if len(message.mentions) != 0:
            for user in message.mentions:
                mentions += f"\n\t{user.name} : {user.id}"
        else:
            mentions = "\n\tNone"
        try:
            with open(os.path.join(os.getcwd(), logdir), encoding='utf_8', mode='a') as log:
                lines = f"\nMessage ID: {message.id}\nAuthor: {message.author}\nTime: {message.created_at}\nMentions: {mentions}\nContents:\n" + "-"*35 + f"\n{message.content}\n" + "-"*35 + "\n"
                log.write(lines)
        except FileNotFoundError:
            with open(os.path.join(os.getcwd(), logdir), encoding='utf_8', mode='w') as log:
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
        
    try:
        await bot.process_commands(message)
    except Exception as e:
        print(f"ERR:\n{e}")


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


# creates a graceful shutdown of this bot
# runs the writeout method in config.py
@bot.command(aliases=["kill"])
async def close(ctx):
    if ctx.author.name != config.operator:
        print(f"someone unauthorized tried to close the bot: {ctx.author.name}")
        eventlog(f"Unauthorized CLOSE Event Called by {ctx.author.name}", "ERR")
        return

    for voice in bot.voice_clients:
        await voice.disconnect()

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
            os.makedirs(os.path.join(os.getcwd(), os.path.dirname(f"logs/messages/{guild.name}/")), exist_ok=True)
    
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


# used by other functions to log some things when called
# not really useful for anyone but me
# only used in early stages when i could just look at a file
# to see what happened, the message log is actually useful though
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
    print("*"*35 + "\n")