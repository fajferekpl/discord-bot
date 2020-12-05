from cogs.somerandomapi import SomeRandomApiCog
from cogs.moderation import ModCog
from cogs.wiki import WikiCog
from cogs.reddit import RedditCog
import discord
from cogs.music import MusicCog
from discord.ext import commands



class HelpCog(commands.Cog, name="help"):

    """Type `.help` and specify the module you need."""


    def __init__(self, client):
        self.client = client
        self.client.remove_command("help")

    @commands.command(name="help")
    async def help_command(self, ctx, cmd=None):

        if cmd is None:
            embed = discord.Embed(title="How can I help you, sir? Type `.help` and choose the module.", color=3066993)
            cog_desc = ""
            for x in self.client.cogs:
                cog_desc += f'```{x}``` {self.client.cogs[x].__doc__}\n'
            embed.add_field(name="Modules:", value=cog_desc, inline=False)
            await ctx.send(embed=embed)

        if (cmd == "music"):
            embed = discord.Embed(title="Do you need some help with music part of Admin The Cat?", color=3066993)
            for command in MusicCog.walk_commands(MusicCog):
                embed.add_field(name=f"`{command}`", value=command.description, inline=False)
            await ctx.send(embed=embed)

        elif (cmd == "reddit"):
            embed = discord.Embed(title="Let's talk about some Reddit stuff. How can I help you?", color=3066993)
            for command in RedditCog.walk_commands(RedditCog):
                embed.add_field(name=f"`{command}`", value=command.description, inline=False)
            await ctx.send(embed=embed)

        elif (cmd == "wiki"):
            embed = discord.Embed(title="Definition needed? Use the wikipedia module.", color=3066993)
            for command in WikiCog.walk_commands(WikiCog):
                embed.add_field(name=f"`{command}`", value=command.description, inline=False)
            await ctx.send(embed=embed)

        elif (cmd == "fact"):
            embed = discord.Embed(title="Some random facts about animals.", color=3066993)
            for command in SomeRandomApiCog.walk_commands(SomeRandomApiCog):
                embed.add_field(name=f"`{command}`", value=command.description, inline=False)
            await ctx.send(embed=embed)

        elif (cmd == "moderation"):
            embed = discord.Embed(title="Do you need help with moderation? Try to type these commands, but remember - you must have permissions to use these commands.", color=3066993)
            for command in ModCog.walk_commands(ModCog):
                embed.add_field(name=f"`{command}`", value=command.description, inline=False)
            await ctx.send(embed=embed)

    @commands.Cog.listener()
    async def on_ready(self):
        if not self.client.ready:
            self.client.cogs_ready.ready_up("help")

def setup(client):
    client.add_cog(HelpCog(client))
    print("Help is loaded.")