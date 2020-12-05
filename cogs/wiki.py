import discord
from discord.ext import commands
import random
import wikipedia


class WikiCog(commands.Cog, name="wiki"):

    """If you need definitions - there is your wikipedia module."""

    def __init__(self, client):
        self.client = client

    @commands.command(name="askWikiPL", aliases=["askpl"], description="Use wikipedia to find definition using Polish. You must also type the topic using quote. Wikipedia will find the random definition from the ones that match the most for your topic.")
    async def askWikiPL(self, ctx, *, topic):
        #channel wikiPL
        wiki_channelPL = self.client.get_channel(784439983666102282)
        wikipedia.set_lang("pl")

        try:
            definition = wikipedia.summary(topic, sentences=25, chars=100, auto_suggest=True, redirect=True)
            embed=discord.Embed(title=wikipedia.page(topic).title, description=definition, url=wikipedia.page(topic).url)
            embed.add_field(name='\u200b', value='\u200b', inline=True)
        except wikipedia.DisambiguationError as e:
            r = random.choice(e.options)
            tp = wikipedia.page(r)
            embed=discord.Embed(title="", description=tp.content, url="")
            embed.add_field(name='\u200b', value='\u200b', inline=True)
            
        await wiki_channelPL.send(embed=embed)

    @commands.command(name="askWikiEN", aliases=["asken"], description="Use wikipedia to find definition using English. You must also type the topic using quote. Wikipedia will find one random definition from the ones that match the most for your topic.")
    async def askWikiEN(self, ctx, *, topic):
        #channel wikiEN
        wiki_channelEN = self.client.get_channel(784440024174166096)
        wikipedia.set_lang("en")

        try:
            definition = wikipedia.summary(topic, sentences=25, chars=100, auto_suggest=True, redirect=True)
            embed=discord.Embed(title=wikipedia.page(topic).title, description=definition, url=wikipedia.page(topic).url)
            embed.add_field(name='\u200b', value='\u200b', inline=True)
        except wikipedia.DisambiguationError as e:
            r = random.choice(e.options)
            tp = wikipedia.page(r)
            embed=discord.Embed(title="", description=tp.content, url="")
            embed.add_field(name='\u200b', value='\u200b', inline=True)
                
        await wiki_channelEN.send(embed=embed)

def setup(client):
    client.add_cog(WikiCog(client))
    print("Wiki is loaded.")