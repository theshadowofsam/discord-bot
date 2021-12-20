"""
music_commands.py
Samuel Lee
10/11/2021
"""
from discord import FFmpegPCMAudio
from discord.ext import commands
import asyncio
from async_timeout import timeout
from yt_search import search as ytsearch

#FFmpeg options i found online
FFMPEG_OPTS = {'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5', 'options': '-vn'}


# Music player with loop that runs queue
class MusicPlayer:
    def __init__(self, ctx):
        self.bot = ctx.bot
        self.guild = ctx.guild
        self.queue = asyncio.Queue()
        self.go = asyncio.Event() 
        self.current = None
        self.channel = ctx.channel
        self.cog = ctx.cog
        self.skips = []

        ctx.bot.loop.create_task(self.player_loop())


    async def player_loop(self):
        while not self.bot.is_closed():
            self.go.clear()

            try:
                async with timeout(300):
                    source = await self.queue.get()
            except:
                return self.destroy(self.guild)
            
            self.current = source
            self.guild.voice_client.play(FFmpegPCMAudio(source.source, options=FFMPEG_OPTS), after=lambda _: self.bot.loop.call_soon_threadsafe(self.go.set))
            await self.channel.send(f"Now Playing: \n{source.url}")

            await self.go.wait()

            self.current = None
            self.skips = []


    def destroy(self, guild):
        return self.bot.loop.create_task(self.cog.cleanup(guild))
            
# used for audio sources and info
class Source:
    def __init__(self, ctx, data, url):
        self.name = data['title']
        self.source = url
        self.url = f"https://www.youtube.com/watch?v=" + data['id']
        self.requested = ctx.author.name
        self.full_data = data

# Music Cog
class Music(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.mp = {}


    # connects to active users voice channel
    @commands.command(aliases=["p"])
    async def play(self, ctx, *, source=None):
        voice_client = ctx.voice_client

        if not voice_client:
            await self.join(ctx, voice_client)
        
        player = self.get_player(ctx)

        data, url = ytsearch(source)
        
        source = Source(ctx, data, url)

        await player.queue.put(source)
        print(player.queue)

    # skips currently playing song in ctx.guild also uses vote system if not admin
    @commands.command(aliases=["s"])
    async def skip(self, ctx):
        if not ctx.author.voice:
            return

        vc = ctx.voice_client
        if not vc or not vc.is_connected():
            return

        player = self.get_player(ctx)

        if not ctx.author.id in player.skips:
            player.skips.append(ctx.author.id)
        print(player.skips)
        if (len(player.skips) >= (len(ctx.author.voice.channel.members)-1)/2) or ctx.author.guild_permissions.administrator:
            await ctx.send("Skipping!")
            vc.stop()        
        else:
            print(f"{len(ctx.author.voice.channel.members)-1} voice channel members")
            print((len(ctx.author.voice.channel.members)-1)/2)
            await ctx.send(f"Not enough votes to skip: {len(player.skips)}/{len(ctx.author.voice.channel.members)/2}")


    # disconnects from voice
    @commands.command(aliases=["disconnect"])
    async def dc(self, ctx):
        await self.cleanup(ctx.guild)


    # clear the ctx.channel players queue
    @commands.command()
    async def clear(self, ctx):
        player = self.get_player(ctx)

        player.queue = asyncio.Queue()

        await ctx.send("Queue emptied")


    # used to join a voice client to ctx.author.voice.channel
    async def join(self, ctx, voice):
        channel = ctx.author.voice.channel

        if voice and voice.is_connected():
            await voice.move_to(channel)
            return voice
        else:
            voice = await channel.connect()
            return voice

    
    # disconnects a voice client and deletes the guilds player
    async def cleanup(self, guild):
        try:
            await guild.voice_client.disconnect()
        except:
            pass

        try:
            del self.mp[guild.id]
        except:
            pass


    # returns ctx.guild's player or creates it if none exists
    def get_player(self, ctx):
        try:
            player = self.mp[ctx.guild.id]
        except:
            player = MusicPlayer(ctx)
            self.mp[ctx.guild.id] = player

        return player


def setup(bot):
    bot.add_cog(Music(bot))