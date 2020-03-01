import discord, arrow, typing, os
from pony.orm import *

db = Database()

class Guild(db.Entity):
    id = PrimaryKey(str)
    name = Required(str)
    channels = Set('Channel')

class Channel(db.Entity):
    id = PrimaryKey(str)
    name = Required(str)
    guild = Required(Guild)

class Member(db.Entity):
    id = PrimaryKey(str)
    name = Required(str)

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

db.bind(provider='postgres', user='postgres', password=os.environ['DB_PWD'], database='revai')
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
async def add_meetup(organizer: discord.Member, name: str, date: arrow.Arrow, invitations: typing.List[discord.Member], reason: str):
    """Creates a new meetup for the database"""
    if not Meetup.exists(organizer=str(organizer.id)):
        Meetup(organizer=str(organizer.id), name=name, date=str(date), invitations=[str(mem.id) for mem in invitations], reason=reason)

@db_session
async def add_attendee(name: str, attendee: discord.Member):
    """Adds an attendee to the given meetup."""
    if Meetup.exists(name=name):
        meet = Meetup.get(name=name)
        meet.attendees.append(attendee.id)
        return "We will remind you before the meetup!"
    else:
        return "It doesn't seem like that is a meetup!"

@db_session
async def add_contributor(name: str, contributor: discord.Member, contribution: str):
    if Meetup.exists(name=name):
        try:
            Contribution(contributor=str(contributor.id), contributing=[contribution], meetup=Meetup.get(name=name))
            return "Thanks for contributing!"
        except:
            return "You need to be attending first silly!"
    else:
        return "It doesn't seem like that is a meetup!"

@db_session
async def update_contribution(name: str, contributor: discord.Member, contribution: str):
    if Meetup.exists(name=name):
        meet = Meetup.get(name=name)
        if Contribution.exists(contributor=str(contributor.id), meetup=meet):
            contr = Contribution.get(contributor=str(contributor.id), meetup=meet)
            contr.contributing.append(contribution)
            return "Thanks for adding to your contribution!"
        else:
            return "It doesn't seem like you're in a meetup!"
    else:
        return "It doesn't seem like that is a meetup!"

@db_session
async def remove_meetup(name):
    if Meetup.exists(name=name):
        Meetup.get(name=name).delete()

@db_session
async def update_guild(guild: discord.Guild):
    """Updates a guild when it is changed."""
    upd_guild = Guild.get(id=str(guild.id))
    upd_guild.name = guild.name

@db_session
async def update_channel(channel: discord.TextChannel):
    """Updates a channel when it is changed."""
    upd_channel = Channel.get(id=str(channel.id))
    upd_channel.name = channel.name

@db_session
async def update_member(member: discord.User):
    upd_member = Member.get(id=str(member.id))
    upd_member.name = member.name
