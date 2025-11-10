import multiprocessing
from dotenv import load_dotenv
from os import environ

import discord
from discord.ext import commands
from discord.ext.commands import errors as DiscordError
from CommandsMain import BaseCommands
from CommandsMain import BaseClose
import Utils

intents_ = discord.Intents.all()
writeDir = "C:\\temp\\JesterMk2\\"
writeFile = "log.txt"

load_dotenv('.env')

class LogClient(commands.Bot):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.name = "LogClient"
        self.WriteThread = Utils.WriteThread(writeDir, writeFile)
        self.WriteProcess = multiprocessing.Process(target=self.WriteThread.run, daemon=False)
        self.WriteProcess.start()
        self.presence = discord.Activity(name="Deep Frying Mobius's Legs", state="In Big Dave's Kitchen", platform="Big Wok, Peanut Oil", type=discord.ActivityType.playing)
        self.ready = False

    async def on_ready(self):
        if self.ready:
            pass
        else:
            print("Ready!")
            await self.change_presence(activity=self.presence)
            await self.add_cog(BaseClose(self))
            self.ready = True
        return 0

    async def on_message(self, message: discord.Message):
        self.WriteThread.emplace(Utils._Msg(message))
        await self.process_commands(message)
        return 0
    
    async def on_command_error(self, context, exception):
        if isinstance(exception, DiscordError.CommandNotFound):
            pass
        else:
            return await super().on_command_error(context, exception)


class CommandClient(commands.Bot):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.name = "CommandClient"
        self.ready = False

    async def on_ready(self):
        if self.ready:
            pass
        else:
            print("Ready!")
            await self.add_cog(BaseCommands(self))
            await self.add_cog(BaseClose(self))
            self.ready = True
        return 0
    
    async def on_message(self, message: discord.Message):
        await self.process_commands(message)
        return 0

    async def on_command_error(self, context, exception):
        if isinstance(exception, DiscordError.CommandNotFound):
            pass
        else:
            return await super().on_command_error(context, exception)
        

class MinecraftClient(commands.Bot):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.name = "MinecraftClient"
        self.ready = False

    async def on_ready(self):
        if self.ready:
            pass
        else:
            print("Ready!")
            await self.add_cog(BaseClose(self))
            self.ready = True
        return 0
    
    async def on_message(self, message: discord.Message):
        await self.process_commands(message)
        return 0
    
    async def on_command_error(self, context, exception):
        if isinstance(exception, DiscordError.CommandNotFound):
            pass
        else:
            return await super().on_command_error(context, exception)


# class SoundClient(commands.bot):
#     def __init__(self, **kwargs):
#         super.__init__(**kwargs)


# class gameClient(commands.bot):
#     def __init__(self, **kwargs):
#         super.__init__(**kwargs)


if __name__ == '__main__':
    app = LogClient(command_prefix='!', intents=intents_)
    app.run(token=environ['DISCORD_TOKEN'])
    print("Closed!")
