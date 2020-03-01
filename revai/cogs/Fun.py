import discord, os, sys, random
from discord.ext import commands
from PIL import Image, ImageOps
from io import BytesIO

class Fun(commands.Cog):
    """Random commands."""
    def __init__(self, client):
        self.client = client

def setup(client):
    client.add_cog(Fun(client))
