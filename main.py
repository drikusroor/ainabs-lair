import discord
import os
import requests
import json
import random
from replit import db

client = discord.Client()

game_state = { "NEW": "NEW", "PLAYING": "PLAYING", "ENDED": "ENDED" }

games = []

class Player:

  def __init__(self, author, name, hp = 20, ap = 20):
    self.author = author
    self.max_hp = hp
    self.hp = hp
    self.max_ap = ap
    self.ap = ap

    if (name):
      self.name = name
    else:
      self.name = author.name

class Game:

  def __init__(self, guild, channel):
    self.players = []
    self.guild = guild
    self.channel = channel
    self.state = game_state["NEW"]

  def get_player(self, author):
    for i, o in enumerate(self.players):
      if o.author == author:
        return self.players[i]
    return None

  def kick_player(self, player):
    for i, o in enumerate(self.players):
      if o == player:
        del self.players[i]
        break
    return

  def get_readable_player_status(self, player):
    return "{name} {hp}/{max_hp}HP {ap}/{max_ap}AP".format(
      name=player.name,
      hp=player.hp,max_hp=player.max_hp,
      ap=player.ap,
      max_ap=player.max_ap
      )

  def get_game_status(self):
    statuses = []
    for i, o in enumerate(self.players):
      statuses.append(self.get_readable_player_status(o))
    return "\n".join(statuses)

def get_quote():
  response = requests.get("https://zenquotes.io/api/random")
  json_data = json.loads(response.text)
  quote = json_data[0]['q'] + " -" + json_data[0]['a']
  return(quote)

def update_encouragements(encouraging_message):
  if "encouragements" in db.keys():
    encouragements = db["encouragements"]
    encouragements.append(encouraging_message)
    db["encouragements"] = encouragements
  else:
    db["encouragements"] = [encouraging_message]

def delete_encouragment(index):
  encouragements = db["encouragements"]
  if len(encouragements) > index:
    del encouragements[index]
  db["encouragements"] = encouragements

@client.event
async def on_ready():
  print('We have logged in as {0.user}'.format(client))

@client.event
async def on_message(message):

  guild = message.guild
  channel = message.channel

  def get_game():
    for i, o in enumerate(games):
      if o.guild.id == guild.id and o.channel.id == channel.id:
        return games[i]
    return None

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
    if "encouragements" in db.keys():
      options = db["encouragements"]
      if len(options) > 0:
        await message.channel.send(random.choice(options))
        return

    no_cheerz = "No cheerz be availables :cry:"
    await message.channel.send(no_cheerz)
    return

  if cmd.startswith("list cheer"):
    encouragements = []
    if "encouragements" in db.keys():
      encouragements_raw = db["encouragements"]
      for idx, val in enumerate(encouragements_raw):
        encouragements.append("#{i} - {val} ".format(i = idx, val = val))
    await message.channel.send('\n'.join(encouragements))
    return
  
  if cmd.startswith("new cheer"):
    encouraging_message = cmd.split("new cheer ",1)[1]
    update_encouragements(encouraging_message)
    await message.channel.send("New encouraging message added.")
    return

  if cmd.startswith("del cheer"):
    encouragements = []
    if "encouragements" in db.keys():
      index = int(cmd.split("del cheer",1)[1])
      delete_encouragment(index)
      encouragements = db["encouragements"]
    await message.channel.send(encouragements)
    return

  if cmd.startswith("new game"):
    for game in games:
      if game.guild.id == guild.id and game.channel.id == channel.id:
        msg = "There is already a game in this channel (#{channel}). Please end the game before start a new one. You can use the `kill game` command to end a game.".format(channel = channel.name)
        await message.channel.send(msg)
        return

    new_game = Game(message.guild, message.channel)
    games.append(new_game)
    msg = "A new has been created in #{channel}".format(channel = channel)
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
    game = get_game()
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
      player = Player(message.author, name)
      game.players.append(player)
      msg = "Player {name} has joined the game! :fist:".format(name = player.name)
      await message.channel.send(msg)
      return

  if cmd.startswith("leave game"):
    game = get_game()
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
    game = get_game()
    msg = game.get_game_status()

    if not msg:
      msg = "Game is fookin' empty mate. Nothing to see here..."

    await message.channel.send(msg)
    return

  await message.channel.send(cmd)

client.run(os.getenv('TOKEN'))