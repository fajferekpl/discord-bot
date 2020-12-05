from __future__ import annotations
import asyncio
import datetime as dt
import re
import discord
import wavelink
from discord.ext import commands
import typing as t
import random
from enum import Enum
import azapi


URL_REGEX = r"(?i)\b((?:https?://|www\d{0,3}[.]|[a-z0-9.\-]+[.][a-z]{2,4}/)(?:[^\s()<>]+|\(([^\s()<>]+|(\([^\s()<>]+\)))*\))+(?:\(([^\s()<>]+|(\([^\s()<>]+\)))*\)|[^\s`!()\[\]{};:'\".,<>?«»“”‘’]))"
OPTIONS = {
    "1️⃣": 0,
    "2⃣": 1,
    "3⃣": 2,
    "4⃣": 3,
    "5⃣": 4,
}

class AlreadyConnectedToChannel(commands.CommandError):
    pass

class NoVoiceChannel(commands.CommandError):
    pass

class QueueIsEmpty(commands.CommandError):
    pass

class NoTrackFound(commands.CommandError):
    pass

class PlayerIsAlreadyPaused(commands.CommandError):
    pass

class PlayerIsAlreadyPlaying(commands.CommandError):
    pass

class NoMoreTracks(commands.CommandError):
    pass

class NoPreviousTracks(commands.CommandError):
    pass

class InvalidRepeatMode(commands.CommandError):
    pass

class RepeatMode(Enum):
    NONE = 0
    ONE = 1
    ALL = 2

class Queue():
    def __init__(self):
        self._queue = []
        self.position = 0
        self.repeat_mode = RepeatMode.NONE

    @property
    def is_empty(self):
        return not self._queue

    @property
    def current_track(self):
        if not self._queue:
            raise QueueIsEmpty
        if self.position <= len(self._queue) - 1:
            return self._queue[self.position]
    
    @property
    def upcoming(self):
        if not self._queue:
            raise QueueIsEmpty

        return self._queue[self.position + 1:]

    @property
    def history(self):
        if not self._queue:
            raise QueueIsEmpty

        return self._queue[:self.position + 1:]

    @property
    def length(self):
        return len(self._queue)

    def add(self, *args):
        self._queue.extend(args)

    def get_next_track(self):
        if not self._queue:
            raise QueueIsEmpty

        self.position += 1

        if self.position < 0:
            return None
        elif self.position > len(self._queue) - 1:
            if self.repeat_mode == RepeatMode.ALL:
                self.position = 0
            else:
                return None

        return self._queue[self.position]

    def shuffle(self):
        if not self._queue:
            raise QueueIsEmpty
        
        upcoming = self.upcoming
        random.shuffle(upcoming)
        self._queue = self._queue[:self.position + 1]
        self._queue.extend(upcoming)

    def set_repeat_mode(self, mode):
        if mode == "none":
            self.repeat_mode = RepeatMode.NONE
        elif mode == "1":
            self.repeat_mode = RepeatMode.ONE
        elif mode == "all":
            self.repeat_mode = RepeatMode.ALL


    def empty(self):
        self._queue.clear()
        self.position = 0 #probably should be here

class Player(wavelink.Player):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.queue = Queue()

    async def connect(self, ctx, channel=None):
        if self.is_connected:
            raise AlreadyConnectedToChannel
    
        channel = getattr(ctx.author.voice, "channel", channel)
        if channel is None:
            raise NoVoiceChannel

        await super().connect(channel.id)
        return channel

    async def teardown(self):
        try:
            await self.destroy()
        except KeyError:
            pass

    async def add_tracks(self, ctx, tracks):
        if not tracks:
            raise NoTrackFound

        if isinstance(tracks, wavelink.TrackPlaylist):
            self.queue.add(*tracks.tracks)
        elif len(tracks) == 1:
            self.queue.add(tracks[0])
            await ctx.send(f"<:musical_note:780816884073234464> `Added {tracks[0].title} to the queue.`")
        else:
            track = await self.choose_track(ctx, tracks)
            if track is not None:
                self.queue.add(track)
                await ctx.send(f"<:musical_note:780816884073234464> `Added {track.title} to the queue.`")
                track_title = track.title

        if not self.is_playing and not self.queue.is_empty:
            await self.start_playback()

    async def choose_track(self, ctx, tracks):
        def _check(r, u):
            return (
                r.emoji in OPTIONS.keys()
                and u == ctx.author
                and r.message.id == msg.id
            )

        embed = discord.Embed(
            title = "Choose a song",
            description=(
                "\n".join(
                    f"**{i+1}.** {t.title} ({t.length//60000}:{str(t.length%60).zfill(2)})"
                    for i, t in enumerate(tracks[:5])
                )
            ),
            color = ctx.author.color,
            timestamp=dt.datetime.utcnow()
        )
        embed.set_author(name="Query Results")
        embed.set_footer(text=f"Invoked by {ctx.author.display_name}", icon_url=ctx.author.avatar_url)

        msg = await ctx.send(embed=embed)
        for emoji in list(OPTIONS.keys())[:min(len(tracks), len(OPTIONS))]:
            await msg.add_reaction(emoji)

        try:
            reaction, _ = await self.bot.wait_for("reaction_add", timeout=60.0, check=_check)
        except asyncio.TimeoutError:
            await msg.delete()
            await ctx.message.delete()
        else:
            await msg.delete()
            return tracks[OPTIONS[reaction.emoji]]

    async def start_playback(self):
        await self.play(self.queue.current_track)

    async def advance(self):
        try:
            track = self.queue.get_next_track()
            if track is not None:
                await self.play(track)
        except QueueIsEmpty:
            pass

    async def repeat_track(self):
        await self.play(self.queue.current_track)

class MusicCog(commands.Cog, wavelink.WavelinkMixin, name="music"):

    """Admin The Cat can also be a music bot. Wanna try?"""
    
    def __init__(self, client):
        self.client = client
        self.wavelink = wavelink.Client(bot=client)
        self.client.loop.create_task(self.start_nodes())

    @commands.Cog.listener()
    async def on_voice_state_update(self, member, before, after):
        if not member.bot and after.channel is None:
            if not [m for m in before.channel.members if not m.bot]:
                await self.get_player(member.guild).teardown()

    @wavelink.WavelinkMixin.listener()
    async def on_node_ready(self, node):
        print(f"Wavelink node '{node.identifier}' ready.")

    @wavelink.WavelinkMixin.listener("on_track_stuck")
    @wavelink.WavelinkMixin.listener("on_track_end") 
    @wavelink.WavelinkMixin.listener("on_track_exception")
    async def on_player_stop(self, node, payload):
        if payload.player.queue.repeat_mode == RepeatMode.ONE:
            await payload.player.repeat_track()
        else:
            await payload.player.advance()

    async def cog_check(self, ctx):
        if isinstance(ctx.channel, discord.DMChannel):
            await ctx.send("Music commands are not available in DMs.")
            return False

        return True

    async def start_nodes(self):
        await self.client.wait_until_ready()

        nodes = {
            "MAIN": {
                "host": "127.0.0.1",
                "port": 2333,
                "rest_uri": "http://127.0.0.1:2333",
                "password": "youshallnotpass",
                "identifier": "MAIN",
                "region": "europe"
            }
        }

        for node in nodes.values():
            await self.wavelink.initiate_node(**node)
    
    def get_player(self, obj):
        if isinstance(obj, commands.Context):
            return self.wavelink.get_player(obj.guild.id, cls=Player, context=obj)
        elif isinstance(obj, discord.Guild):
            return self.wavelink.get_player(obj.id, cls=Player)

    @commands.command(name="connect", aliases=["join"], description="Use this to connect bot to the voice channel. You can also specify the channel id.")
    async def connect_command(self, ctx, *, channel: t.Optional[discord.VoiceChannel]):
        player = self.get_player(ctx)
        channel = await player.connect(ctx, channel)
        await ctx.send(f"`Connected to {channel.name}.`")

    @connect_command.error
    async def connect_command_error(self, ctx, exc):
        if isinstance(exc, AlreadyConnectedToChannel):
            await ctx.send("`Already connected to a voice channel.`")
        elif isinstance(exc, NoVoiceChannel):
            await ctx.send("`No voice channel found.`")

    @commands.command(name="disconnect", aliases=["leave", "dc"], description="Disconnect bot from voice channel.")
    async def disconnect_command(self, ctx):
        player = self.get_player(ctx)
        await player.teardown()
        await ctx.send("`Disconnected.`")

    @commands.command(name="lyrics", description="Find lyrics for that specific song. You have to input the title.")
    async def lyr_command(self, ctx, title):

        channel_lyrics = self.client.get_channel(784434857445949490)

        await channel_lyrics.send("<:mag_right:782771344726687764> `Searching for the lyrics...`")
        API = azapi.AZlyrics('google', accuracy=0.5)

        # API.artist = artist
        API.title = title

        #get and/or save the lyrics
        lyrics = API.getLyrics()
        
        lyrics1 = lyrics[:1995]
        lyrics2 = lyrics[1995:]

        await channel_lyrics.send(f"`{lyrics1}`")
        await channel_lyrics.send(f"`{lyrics2}`")        

    @commands.command(name="play", description="Use this command to turn the music on or resume it after pause.")
    async def play_command(self, ctx, *, query: t.Optional[str]):
        player = self.get_player(ctx)

        if not player.is_connected:
            await player.connect(ctx)

        if query is None:
            if player.queue.is_empty:
                raise QueueIsEmpty

            await player.set_pause(False)
            await ctx.send("<:arrow_forward:780820834125742131> `Playback resumed.`")
        
        else:
            query = query.strip("''")
            if not re.match(URL_REGEX, query):
                query = f"ytsearch:{query}"

            await player.add_tracks(ctx, await self.wavelink.get_tracks(query))

    @play_command.error
    async def play_command_error(self, ctx, exc):
        if isinstance(exc, QueueIsEmpty):
            await ctx.send("`No songs to play as the queue is empty.`")
        elif isinstance(exc, NoVoiceChannel):
            await ctx.send("`No suitable voice channel was provided.`")

    @commands.command(name="pause", description="Just pause. Nothing more.")
    async def pause_command(self, ctx):
        player = self.get_player(ctx)

        if player.is_paused:
            raise PlayerIsAlreadyPaused

        await player.set_pause(True)
        await ctx.send("<:pause_button:780819848804564992> `Playback paused.`")

    @pause_command.error
    async def pause_command_error(self, ctx, exc):
        if isinstance(exc, PlayerIsAlreadyPaused):
            await ctx.send("<:pause_button:780819848804564992> `Already paused.`")
    
    @commands.command(name="stop",description="Stop the whole queue.")
    async def stop_command(self, ctx):
        player = self.get_player(ctx)
        player.queue.empty()
        await player.stop()
        await ctx.send("<:stop_button:780821206387523596> `Playback stopped.`")

    @commands.command(name="next", aliases=["skip"], description="Skip current track and play next song in the queue.")
    async def next_command(self, ctx):
        player = self.get_player(ctx)

        if not player.queue.upcoming:
            raise NoMoreTracks

        await player.stop()
        await ctx.send("<:fast_forward:780821390222819398> `Playing next track in queue.`")

    @next_command.error
    async def next_command_error(self, ctx, exc):
        if isinstance(exc, QueueIsEmpty):
            await ctx.send("`This could not be executed as the queue is currently empty.`")
        elif isinstance(exc, NoMoreTracks):
            await ctx.send("`There are no more tracks in the queue.`")

    @commands.command(name="previous", description="Play previous song in the queue.")
    async def previous_command(self, ctx):
        player = self.get_player(ctx)

        if not player.queue.history:
            raise NoPreviousTracks

        player.queue.position -= 2
        await player.stop()
        await ctx.send("<:rewind:780821595035664394> `Playing previous track in queue.`")

    @previous_command.error
    async def previous_command_error(self, ctx, exc):
        if isinstance(exc, QueueIsEmpty):
            await ctx.send("`This could not be executed as the queue is currently empty.`")
        elif isinstance(exc, NoPreviousTracks):
            await ctx.send("`There are no previous tracks in the queue.`")

    @commands.command(name="shuffle", description="Shake it, babe. Just mix the queue.")
    async def shuffle_command(self, ctx):
        player = self.get_player(ctx)
        player.queue.shuffle()
        await ctx.send("<:twisted_rightwards_arrows:780821887542231121> `Queue shuffled.`")

    @shuffle_command.error
    async def shuffle_command_error(self, ctx, exc):
        if isinstance(exc, QueueIsEmpty):
            await ctx.send("`The queue could not be shuffled as it is currently empty.`")

    @commands.command(name="repeat", aliases=["loop"], description="Loop whole queue, one song or turn it off. Type: all, 1 or none.")
    async def repeat(self, ctx, mode: str):
        if mode not in ("none", "1", "all"):
            raise InvalidRepeatMode

        player = self.get_player(ctx)
        player.queue.set_repeat_mode(mode)

        if mode=="none":
            await ctx.send("<:zzz:780830284400295946> `The loop mode is off.`")
        elif mode=="1":
            await ctx.send("<:repeat_one:780829875811516436> `Loop mode for that one song.`")
        elif mode=="all":
            await ctx.send("<:repeat:780830095727394842> `Loop mode for the queue.`")

    @commands.command(name="queue", aliases=["np"], description="Shows you whole queue and currently playing track.")
    async def queue_command(self, ctx, *, show: t.Optional[int] = 10):
        player = self.get_player(ctx)
        
        if player.queue.is_empty:
            raise QueueIsEmpty

        embed = discord.Embed(
            title="Queue",
            description=f"Showing up to next {show} tracks",
            color = ctx.author.color,
            timestamp=dt.datetime.utcnow()
        )
        embed.set_author(name="Queue Results")
        embed.set_footer(text=f"Requested by {ctx.author.display_name}", icon_url=ctx.author.avatar_url)
        embed.add_field(name="Currently playing", 
                        value=getattr(player.queue.current_track, "title", "No tracks currently playing."), 
                        inline=False)
        upcoming = player.queue.upcoming
        if upcoming:
            embed.add_field(
                name="Next up",
                value="\n".join(t.title for t in upcoming[:show]),
                inline=False
            )

        msg = await ctx.send(embed=embed)

    @queue_command.error
    async def queue_command_error(self, ctx, exc):
        if isinstance(exc, QueueIsEmpty):
            await ctx.send("`The queue is currently empty.`")

def setup(client):
    client.add_cog(MusicCog(client))
    print("Music is loaded.")