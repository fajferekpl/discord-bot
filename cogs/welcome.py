import discord
from discord.ext import commands
import datetime

class WelcomeCog(commands.Cog, name="welcome"):

    """Just welcome!"""

    def __init__(self, client):
        self.client = client

    @commands.Cog.listener()
    async def on_member_join(self, member):
        myEmbed=discord.Embed(title="Welcome", description="Nice to see you in the COW MEME server!", color=3066993)
        myEmbed.set_thumbnail(url=f"{member.avatar_url}")
        myEmbed.set_author(name=f"{member.name}", icon_url=f"{member.avatar_url}")
        myEmbed.set_footer(text=f"Have a nice day, buddy!")
        myEmbed.timestamp = datetime.datetime.utcnow()

        welcome_channel = self.client.get_channel(784439045782634567)
        await welcome_channel.send(embed=myEmbed)

def setup(client):
    client.add_cog(WelcomeCog(client))
    print("Welcome is loaded.")