import discord
import requests
from discord.ext import commands
import json
from dotenv import load_dotenv
from discord import FFmpegPCMAudio
from discord import Member
from discord.ext.commands import has_permissions, MissingPermissions
import os

load_dotenv()
discord_key = os.getenv("BOT_TOKEN")
joke_key = os.getenv("JOKE_API_TOKEN")
intents = discord.Intents.all()
intents.members = True

queues = {}

def check_queue(ctx, id):
    if queues[id] != []:
        voice = ctx.guild.voice_bot
        source = queues[id].pop(0)
        player = voice.play(source)

bot = commands.Bot(command_prefix = '!',intents = intents)

@bot.event
async def on_ready():   

    print("The bot is now ready for use")
    print("-----------------------------")

@bot.command()
async def hello(ctx):
    await ctx.send("Hello, i am the practice bot")

@bot.event
async def on_member_join(member):
    url = "https://jokeapi-v2.p.rapidapi.com/joke/Any"

    querystring = {"format":"json","contains":"C%23","idRange":"0-150","blacklistFlags":"nsfw"}

    headers = {
        "X-RapidAPI-Key": joke_key,
        "X-RapidAPI-Host": "jokeapi-v2.p.rapidapi.com"
    }

    response = requests.get(url, headers=headers, params=querystring)

    channel = bot.get_channel(939767212716199949)
    await channel.send(f"Welcome {member.display_name}")
    await channel.send(response.json()["setup"])
    await channel.send(response.json()["delivery"])

@bot.event
async def on_member_remove(member):
    channel = bot.get_channel(939767212716199949)
    await channel.send(f"Bye {member.display_name}")

@bot.command()
async def join(ctx):
    if(ctx.author.voice):
        channel = ctx.message.author.voice.channel
        voice = await channel.connect()
        source = FFmpegPCMAudio("birds.wav")
        player = voice.play(source)
    else:
        await ctx.send("You are not in a voice channel, you must be in a voice channel to run this command")

@bot.command()
async def leave(ctx):
    if (ctx.voice_bot):
        voicechannel = ctx.guild.voice_bot
        await voicechannel.disconnect()
        await ctx.send("I left the voice channel")
    else:
        await ctx.send("I am not in a voice channel")

@bot.command()
async def pause(ctx):
    voice = discord.utils.get(bot.voice_bots, guild=ctx.guild)
    if voice.is_playing():
        voice.pause()
    else:
        await ctx.send("There is no audio playing")

@bot.command()
async def resume(ctx):
    voice = discord.utils.get(bot.voice_bots, guild=ctx.guild)
    if voice.is_paused():
        voice.resume()
    else:
        await ctx.send("At the moment no song is paused")

@bot.command()
async def stop(ctx):
    voice = discord.utils.get(bot.voice_bots, guild=ctx.guild)
    voice.stop()

@bot.command()
async def play(ctx, arg):
    voice = ctx.guild.voice_bot
    source = FFmpegPCMAudio(arg + ".wav")
    player = voice.play(source, after=lambda x=None: check_queue(ctx, ctx.message.guild.id))

@bot.command()
async def queue(ctx, arg):
    voice = ctx.guild.voice_bot
    source = FFmpegPCMAudio(arg + ".wav")

    guild_id = ctx.message.guild.id

    if guild_id in queues:
        queues[guild_id].append(source)
    else:
        queues[guild_id] = [source]

    await ctx.send("Added to queue")

@bot.command()
@has_permissions(kick_members=True)
async def kick(ctx, member: discord.member, *, reason = None):
    await member.kick(reason = reason)
    await ctx.send(f'User {member} has been kicked')

@kick.error
async def kick_error(ctx, error):
    if isinstance(error, commands.MissingPermissions):
        await ctx.send("You don't have permission to kick people")

@bot.command()
@has_permissions(ban_members=True)
async def ban(ctx, member: discord.member, *, reason = None):
    await member.ban(reason = reason)
    await ctx.send(f'User {member} has been banned')

@ban.error
async def ban_error(ctx, error):
    if isinstance(error, commands.MissingPermissions):
        await ctx.send("You don't have permission to ban people")

@bot.command()
async def embed(ctx):
    embed = discord.Embed(title="Dog", url="https://google.com", description="We love dogs", color=0x4dff4d)
    embed.set_author(name=ctx.author.display_name, url="", icon_url=ctx.author.avatar)
    await ctx.send(embed=embed)






bot.run(discord_key)