import discord
from discord.ext import commands
from revai.database import *

class Events(commands.Cog):
    """Random commands."""
    def __init__(self, client):
        self.client = client

    @commands.Cog.listener()
    async def on_ready(self):
        for guild in self.client.guilds:
            await add_guild(guild)
            for channel in guild.channels:
                await add_channel(channel)
        for user in self.client.users:
            await add_member(user)
        print(f'{self.client.user.name} is now online.')

    @commands.Cog.listener()
    async def on_message(self, message):
        if not message.author.bot:
            await add_message(message)

    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):
        if type(error) == commands.CommandNotFound:
            await ctx.send('Sorry, that is not a command!')
        elif type(error) == commands.MissingRequiredArgument:
            if ctx.command.usage:
                await ctx.send(ctx.command.usage)
            else:
                await ctx.send('Missing arguments!')
        elif type(error) == commands.MissingPermissions:
            await ctx.send('You do not have the permissions to use this command!')

    @commands.Cog.listener()
    async def on_guild_update(self, before, after):
        await update_guild(after)

    @commands.Cog.listener()
    async def on_channel_update(self, before, after):
        await update_channel(after)

    @commands.Cog.listener()
    async def on_member_update(self, before, after):
        await update_member(after)

def setup(client):
    client.add_cog(Events(client))
