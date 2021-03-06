import discord, arrow, typing
from Crypto.Cipher import AES
from pony.orm import *
from revai.conf import DB_PWD, key

db = Database()

class Guild(db.Entity):
    id = PrimaryKey(str)
    name = Required(str)
    channels = Set('Channel')

class Channel(db.Entity):
    id = PrimaryKey(str)
    name = Required(str)
    guild = Required(Guild)
    messages = Set('Message')

class Member(db.Entity):
    id = PrimaryKey(str)
    name = Required(str)
    messages = Set('Message')

class Message(db.Entity):
    id = PrimaryKey(str)
    author = Required(Member)
    channel = Required(Channel)
    content = Required(bytes)
    nonce = Required(bytes)
    tag = Required(bytes)

class Meetup(db.Entity):
    organizer = PrimaryKey(str)
    name = Required(str)
    date = Required(str)
    invitations = Required(StrArray)
    attendees = Optional(StrArray)
    contributions = Set('Contribution')
    reason = Required(str)

class Contribution(db.Entity):
    id = PrimaryKey(int, auto=True)
    contributor = Required(str)
    contributing = Required(StrArray)
    meetup = Required(Meetup)

db.bind(provider='postgres', user='postgres', password=DB_PWD, database='revai')
db.generate_mapping(create_tables=True)

@db_session
async def add_guild(guild: discord.Guild):
    """Adds a new guild to the database."""
    if not Guild.exists(id=str(guild.id)):
        Guild(id=str(guild.id), name=guild.name)
        print('Added new guild')

@db_session
async def add_channel(channel: typing.Union[discord.TextChannel, discord.VoiceChannel]):
    """Adds a new channel to the database."""
    if not Channel.exists(id=str(channel.id)) and type(channel) in [discord.TextChannel, discord.VoiceChannel]:
        Channel(id=str(channel.id), name=channel.name, guild=Guild.get(id=str(channel.guild.id)))
        print('Added new channel')

@db_session
async def add_member(member: discord.User):
    """Adds a new Member to the database."""
    if not Member.exists(id=str(member.id)):
        Member(id=str(member.id), name=member.name)
        print('Added new user')

@db_session
async def add_message(message: discord.Message):
    if not Message.exists(id=str(message.id)):
        cipher = AES.new(key, AES.MODE_EAX)
        content, tag = cipher.encrypt_and_digest(message.content.encode())
        Message(id=str(message.id), author=Member.get(id=str(message.author.id)), channel=Channel.get(id=str(message.channel.id)), content=content, nonce=cipher.nonce, tag=tag)

@db_session
async def add_meetup(organizer: discord.Member, name: str, date: arrow.Arrow, invitations: typing.List[discord.Member], reason: str):
    """Creates a new meetup for the database"""
    if not Meetup.exists(organizer=str(organizer.id)):
        Meetup(organizer=str(organizer.id), name=name, date=str(date), invitations=[str(mem.id) for mem in invitations], reason=reason)

@db_session
async def add_attendee(ctx, name: str, attendee: discord.Member):
    """Adds an attendee to the given meetup."""
    if Meetup.exists(name=name):
        meet = Meetup.get(name=name)
        meet.attendees.append(str(attendee.id))
        db.commit()
        await ctx.send("Thank you for attending! We will remind you of the meetup 30 minutes before.")
    else:
        await ctx.send("That doesn't seem to be an ongoing meetup, sorry!")

@db_session
async def add_contributor(ctx, name: str, contributor: discord.Member, contribution: str):
    """Adds or updates a contribution to the given meetup."""
    if Meetup.exists(name=name):
        meet = Meetup.get(name=name)
        if str(contributor.id) in meet.attendees:
            if Contribution.exists(contributor=str(contributor.id), meetup=meet):
                contr = Contribution.get(contributor=str(contributor.id), meetup=meet)
                contr.contributing.append(contribution)
                db.commit()
                await ctx.send("Thank you for adding to your contribution!")
            else:
                Contribution(contributor=str(contributor.id), contributing=[contribution], meetup=meet)
                db.commit()
                await ctx.send("Thank you for contributing!")
        else:
            await ctx.send("You must be attending the meetup first!")
    else:
        await ctx.send("That doesn't seem to be an ongoing meetup, sorry!")

@db_session
async def remove_meetup(ctx, name: str):
    """Removes the given meetup."""
    if Meetup.exists(name=name):
        meet = Meetup.get(name=name)
        for contr in meet.contributions:
            contr.delete()
        meet.delete()
        db.commit()
        await ctx.send("Successfully removed meetup.")
    else:
        await ctx.send("Meetup does not exist.")

@db_session
async def update_guild(guild: discord.Guild):
    """Updates a guild when it is changed."""
    upd_guild = Guild.get(id=str(guild.id))
    upd_guild.name = guild.name
    print('Updated guild')

@db_session
async def update_channel(channel: discord.TextChannel):
    """Updates a channel when it is changed."""
    upd_channel = Channel.get(id=str(channel.id))
    upd_channel.name = channel.name
    print('Updated channel')

@db_session
async def update_member(member: discord.User):
    upd_member = Member.get(id=str(member.id))
    if upd_member.name != member.name:
        upd_member.name = member.name
        print('Updated member', member.name)
