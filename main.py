import discord
import requests
import json
import random
import asyncio
from decouple import config

# Local imports
from modules import insult_generator
from modules.game import Game, game_state
from modules.player import Player
from modules.enemy import Enemy

TOKEN = config('TOKEN')

client = discord.Client()

games = []     

def get_quote():
  response = requests.get("https://zenquotes.io/api/random")
  json_data = json.loads(response.text)
  quote = json_data[0]['q'] + " -" + json_data[0]['a']
  return(quote)

def update_encouragements(encouraging_message):
  raise Exception("Not yet implemented.")

def delete_encouragment(index):
  raise Exception("Not yet implemented.")

@client.event
async def on_ready():
  print('We have logged in as {0.user}'.format(client))

@client.event
async def on_message(message):
  
  guild = message.guild
  channel = message.channel

  async def get_game(ctx):
    game = None
    for i, o in enumerate(games):
      if o.guild.id == guild.id and o.channel.id == channel.id:
        game = games[i]
    
    if not game:
      insult = insult_generator.generate_insult()
      await message.channel.send("There ain't no game, you {insult}".format(insult=insult))
    return game

  if message.author == client.user:
    return

  if not message.content.startswith('.al '):
    return

  cmd = message.content[4:]

  if cmd.startswith('quote'):
    quote = get_quote()
    await message.channel.send(quote)
    return

  if cmd.startswith('cheer'):
    no_cheerz = "No cheerz be availables :cry:"
    await message.channel.send(no_cheerz)
    return

  if cmd.startswith("list cheer"):
    raise Exception("Not yet implemented.")
  
  if cmd.startswith("new cheer"):
    raise Exception("Not yet implemented.")

  if cmd.startswith("del cheer"):
    raise Exception("Not yet implemented.")

  if cmd.startswith("new game"):
    for game in games:
      if game.guild.id == guild.id and game.channel.id == channel.id:
        msg = "There is already a game in this channel (#{channel}). Please end the game before start a new one. You can use the `kill game` command to end a game.".format(channel = channel.name)
        await message.channel.send(msg)
        return

    new_game = Game(message.guild, message.channel)
    games.append(new_game)
    msg = "A new game has been created in #{channel}".format(channel = channel)
    await message.channel.send(msg)
    return

  if cmd.startswith("kill game"):
    for i, o in enumerate(games):
      if o.guild.id == guild.id and o.channel.id == channel.id:
        del games[i]
        break
    
    msg = "Game has been killed off. Are you happy now? :cry:"
    await message.channel.send(msg)
    return

  if cmd.startswith("join game"):
    game = await get_game(message)
    if not game: return
    name = message.author.name

    try:
      name = cmd.split("join game ",1)[1]
    except:
      print("Player name not supplied")

    if game.get_player(message.author):
      msg = "You have already joined the game, you silly. :joy:"
      await message.channel.send(msg)
      return
    else:
      player = Player(game, message.author, name)
      game.players.append(player)
      msg = "Player {name} has joined the game! :fist:".format(name = player.name)
      await message.channel.send(msg)
      return

  if cmd.startswith("leave game"):
    game = await get_game(message)
    if not game: return
    if game.state == game_state["PLAYING"]:
      msg = "You cannot leave a game once it has started."
      await message.channel.send(msg)
      return
    player = game.get_player(message.author)

    if player:
      msg = "Player {name} has left the game! :door:".format(name = player.name)
      game.kick_player(player)
      await message.channel.send(msg)
      return
    else:
      msg = "You are not in the game, you whackadoodledoo!"
      await message.channel.send(msg)
      return

  if cmd.startswith("game status"):
    game = await get_game(message)
    if not game: return
    msg = game.get_game_status()

    if not msg:
      msg = "Game is fookin' empty mate. Nothing to see here..."

    await message.channel.send(msg)
    return
  
  if cmd.startswith("add enemy"):
    game = await get_game(message)
    if not game: return
    name = cmd.split("add enemy ",1)[1]
    enemy = Enemy(game, name, 20, 5)
    game.players.append(enemy)
    msg = "An enemy {name} was added to the game! :japanese_goblin:".format(name = name)
    await message.channel.send(msg)
    return

  if cmd.startswith("start game"):
    game = await get_game(message)
    if not game: return

    if game.state == game_state["NEW"]:
      msg = "A new adventure begins... :drum:"
      await message.channel.send(msg)
      await game.start(message)
    elif game.state == game_state["PLAYING"]:
      msg = "The adventure is already ongoing, you fool! :dog:"
      await message.channel.send(msg)
    else:
      msg = "The adventure has ended already..."
      await message.channel.send(msg)
    return

  if cmd.startswith("init template"):
    game = await get_game(message)
    if not game: return
    name = cmd.split("init template ",1)[1]
    await game.init_template(message, name)
    await message.channel.send("Template {name} initialized. :white_check_mark: ".format(name=name))
    return

  if cmd.startswith("attack"):
    game = await get_game(message)
    if not game: return
    name = cmd.split("attack ",1)[1]
    player = game.get_player(message.author) 
    await player.attack(message, name)
    return

  if cmd.startswith("insult"):
    game = await get_game(message)
    if not game: return
    name = cmd.split("insult ",1)[1]
    message.channel.send('{name}, you {insult}.'.format(name = name, insult = insult_generator.generate_insult()))
    return

  if cmd.startswith("report status"):
    numbers = [1,2,3,4,5,6,7]
    chosen = random.choice(numbers)
    statuses = [
      "{number}: Injured.".format(number=chosen), 
      "{number}: Where are you?".format(number=chosen),
      "{number}: Low ammo.".format(number=chosen),
      "{author}: Oh no, #{number} is down".format(author=message.author.name, number=chosen)
    ]
    msg = random.choice(statuses)
    await message.channel.send(msg)
    return
  
  await message.channel.send('Not a valid command, {name}. You {insult}.'.format(name = message.author.name, insult = insult_generator.generate_insult()))

client.run(TOKEN)