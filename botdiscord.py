import discord, os
import random
from discord.ext import commands, tasks
from itertools import cycle
import sys
import traceback
from wavelink import client
from lxml import html
import requests

if not os.path.isfile("config.py"):
	sys.exit("'config.py' not found! Please add it and try again.")
else:
	import config

intents = discord.Intents.default()
intents.members = True

client = commands.Bot(command_prefix=[".", "!"], intents=intents)

page = requests.get("https://goodmovieslist.com/best-movies/best-250-movies.html")
tree = html.fromstring(page.content)
movies = tree.xpath('//span[@class="list_movie_localized_name Undefined"]/text()')
random_movie = random.sample(movies, 1)[0]

# Change status of movie
status = cycle([random_movie])

@tasks.loop(seconds=3600)
async def change_status():
    await client.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name=next(status)))

@client.event
async def on_ready():
    change_status.start()
    await client.change_presence(status=discord.Status.online)
    print('Bot is ready.')

    initial_extensions = ["cogs.moderation",
                        "cogs.welcome",
                        "cogs.reddit",
                        "cogs.wiki",
                        "cogs.music",
                        "cogs.help",
                        "cogs.somerandomapi"]

    if __name__ == "__main__":
        for extension in initial_extensions:
            try:
                client.load_extension(extension)
            except Exception as e:
                print(f"Failed to load extension {extension}", file=sys.stderr)
                traceback.print_exc()

client.run(config.TOKEN)
