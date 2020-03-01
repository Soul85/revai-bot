import discord
from discord import utils
from discord.ext import commands

class Owner(commands.Cog):
    """Owner only commands."""
    def __init__(self, client):
        self.client = client

    @commands.command()
    @commands.is_owner()
    async def shutdown(self, context):
        """Shuts down the bot in the event that manual shutdown is necessary."""
        try:
            await self.client.logout()
        except:
            self.client.clear()

def setup(client):
    client.add_cog(Owner(client))
