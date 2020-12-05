import discord, os, sys
from discord.ext import commands
import random
import praw

if not os.path.isfile("config.py"):
	sys.exit("'config.py' not found! Please add it and try again.")
else:
	import config

class RedditCog(commands.Cog, name="reddit"):

    """We all love reddit. Admin The Cat can help you with some commands."""

    def __init__(self, client):
        self.client = client

    @commands.command(name="post", aliases=["p", "reddit"], description="Shows posts from Reddit. Specify the subreddit, sir. For example: `.post deadbydaylight` or `.post books`.")
    async def post(self, ctx, subreddit: str):

        reddit = praw.Reddit(client_id = config.CLIENT_ID, 
                     client_secret = config.CLIENT_SECRET, 
                     username = config.USERNAME, 
                     password = config.PASSWORD, 
                     user_agent= config.USER_AGENT)

        dbd_channel = self.client.get_channel(784440370715951175)
        fifa_channel = self.client.get_channel(784440629967061043)
        memes_channel = self.client.get_channel(784440751513796668)
        all_channel = self.client.get_channel(784440853988769872)
        reddit_channel = self.client.get_channel(784539430387974144)

        subreddit = subreddit.lower()

        subreddit = reddit.subreddit(subreddit)

        if subreddit == "dbd":
            subreddit = reddit.subreddit("deadbydaylight")
        elif subreddit == "fifa":
            subreddit = reddit.subreddit("fifa21")
        elif subreddit == "meme":
            subreddit = reddit.subreddit("memes")

        all_subs = []

        top = subreddit.top(limit=100)
        for submission in top:
            all_subs.append(submission)
        
        random_sub = random.choice(all_subs)
        name = random_sub.title
        url = random_sub.url
            
        em = discord.Embed(title = name)
        em.set_image(url = url)

        if len(url) > 31:
            if subreddit == "deadbydaylight":
                await dbd_channel.send(embed = em)
            elif subreddit == "fifa21":
                await fifa_channel.send(embed = em)
            elif subreddit == "memes":
                await memes_channel.send(embed = em)
            elif subreddit == "all":
                await all_channel.send(embed = em)
            else:
                await reddit_channel.send(embed = em)
        else:
            if subreddit == "deadbydaylight":
                await dbd_channel.send(url)
            elif subreddit == "fifa21":
                await fifa_channel.send(url)
            elif subreddit == "memes":
                await memes_channel.send(url)
            elif subreddit == "all":
                await all_channel.send(url)
            else:
                await reddit_channel.send(url) 

def setup(client):
    client.add_cog(RedditCog(client))
    print("Reddit is loaded.")