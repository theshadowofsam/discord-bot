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
        self.queue = asyncio.Queue(maxsize=100)
        self.queue_items = []
        self.sub_queues = {}
        self.sqi = 0    # sub  queue index
        self.go = asyncio.Event()
        self.current = None
        self.channel = ctx.channel
        self.cog = ctx.cog
        self.skips = []

        ctx.bot.loop.create_task(self.player_loop())


    async def player_loop(self):
        while not self.bot.is_closed():
            self.go.clear() # i dont think i need this but i don't care enough to fuck with it

            try:
                async with timeout(120): # disconnect from guild after 2 mins if nothing is in the queue for time
                    source = await self.queue.get()
            except:
                return self.destroy(self.guild)
            self.queue_items.pop(0)

            self.current = source
            self.guild.voice_client.play(FFmpegPCMAudio(source.source, options=FFMPEG_OPTS), after=lambda _: self.bot.loop.call_soon_threadsafe(self.go.set)) #guild.voice_client.play() spawns a sub-process. doesn't block.
            await self.channel.send(f"Now Playing: \n{source.name} by {source.full_data['uploader']}\nRequested by: {source.requested}")

            await self.go.wait() # await here gives control back to event loop until song ends(after=lambda _)

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
        self.requested = ctx.author.nick if ctx.author.nick else ctx.author.name
        self.full_data = data


# Music Cog
class Music(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.mp = {}


    # hee haw
    @commands.command()
    async def beacon(self, ctx):
        voice_client = ctx.voice_client
        if not voice_client:
            await self.join(ctx, voice_client)
        beacon = Source(ctx, {'title':'Beacon', 'id':'topkek'}, 'bacon.mp3')
        player = self.get_player(ctx)
        player.queue_items.append('Beacon')
        await player.queue.put(beacon)


    # connects to active users voice channel
    @commands.command(aliases=["p"])
    async def play(self, ctx, *, source):
        if not ctx.author.voice:
            await ctx.author.send(f"You cannot play audio in a server you are not connected to.")
            return
        voice_client = ctx.voice_client
        if not voice_client:
            await self.join(ctx, voice_client)
        player = self.get_player(ctx)
        data, url = ytsearch(source)
        source = Source(ctx, data, url)
        await player.queue.put(source)
        player.queue_items.append(data['title'])


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
        if (len(player.skips) >= (len(ctx.author.voice.channel.members)-1//2 + 1)) or ctx.author.guild_permissions.administrator:
            await ctx.send("Skipping!")
            vc.stop()
        else:
            await ctx.send(f"Not enough votes to skip: {len(player.skips)}/{(len(ctx.author.voice.channel.members)-1)//2 + 1}")


    # sends a message with the queue displayed
    @commands.command(aliases=["q"])
    async def queue(self, ctx):
        if not ctx.author.voice or not ctx.voice_client:
            return
        player = self.get_player(ctx)
        if len(player.queue_items) == 0:
            return
        msg = ""
        for i, s in enumerate(player.queue_items):
            msg += f"{i+1}. {s}\n"
        await ctx.send(msg)


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


async def setup(bot):
    await bot.add_cog(Music(bot))