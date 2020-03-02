import discord
from discord.ext import commands

class Fun(commands.Cog):
    """Random commands."""
    def __init__(self, client):
        self.client = client

    @commands.command()
    async def ping(self, ctx):
        await ctx.send(f'Ping: {(self.client.latency*1000):.2f}ms')

def setup(client):
    client.add_cog(Fun(client))
