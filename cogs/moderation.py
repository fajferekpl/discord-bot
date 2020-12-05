import discord
from discord.ext import commands


class ModCog(commands.Cog, name="moderation"):

    """Commands for moderators. Only members with permission can use these."""

    def __init__(self, client):
        self.client = client

        #Delete messages
    @commands.command(name="clear", description="Delete some messages. You must specify how many.")
    async def clear(self, ctx, *, number:int=None):
        if ctx.message.author.guild_permissions.manage_messages:
            try:
                if number is None:
                    await ctx.send("You must input a number.")
                else:
                    deleted = await ctx.message.channel.purge(limit=number)
                    await ctx.send(f"Messages deleted by {ctx.message.author.mention}: {len(deleted)}")
            except:
                await ctx.send("I can't purge messages here.")
        else:
            await ctx.send("You don't have permissions to use this command.")

        #Kick command
    @commands.command(name="kick", description="Kick that user. Use @ to specify the member. You can also type a reason.")
    async def kick(self, ctx, user : discord.Member, *, reason=None):
        bye_channel = self.client.get_channel(784588815934816277)
        if user.guild_permissions.manage_messages:
            await ctx.send("I can't kick this user.")
        elif ctx.message.author.guild_permissions.kick_members:
            if reason is None:
                await ctx.guild.kick(user=user, reason ="None")
                await bye_channel.send(f"{user} has been kicked.")
            else:
                await ctx.guild.kick(user=user, reason=reason)
                await bye_channel.send(f"{user} has been kicked.")
        else:
            await ctx.send("You don't have permissions to use this command.")

        #Ban command
    @commands.command(name="ban", description="Ban members using @ to specify the member. You can also type a reason.")
    async def ban(self, ctx, user:discord.Member, *, reason=None):
        bye_channel = self.client.get_channel(784588815934816277)
        if user.guild_permissions.manage_messages:
            await ctx.send("I can't ban this user.")
        elif ctx.message.author.guild_permissions.ban_members:
            if reason is None:
                await ctx.guild.ban(user=user, reason ="None")
                await bye_channel.send(f"{user} has been banned.")
            else:
                await ctx.guild.ban(user=user, reason=reason)
                await bye_channel.send(f"{user} has been banned.")
        else:
            await ctx.send("You don't have permissions to use this command.")

        #Unban command
    @commands.command(name="unban", description="You want to unban someone? No problem, do it by using member name and discriminator.")
    async def unban(self, ctx, *, member):
        banned_users = await ctx.guild.bans()
        member_name, member_discriminator = member.split('#')

        for ban_entry in banned_users:
            user = ban_entry.user

            if (user.name, user.discriminator) == (member_name, member_discriminator):
                await ctx.guild.unban(user)
                await ctx.send(f'{user.mention} has been unbanned.')
                return

def setup(client):
    client.add_cog(ModCog(client))
    print("Moderation is loaded.")
