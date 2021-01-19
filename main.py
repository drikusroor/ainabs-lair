import discord
import requests
import json
import random
from random import randrange
from decouple import config
from modules.insult_generator import insult_generator

TOKEN = config('TOKEN')

client = discord.Client()

game_state = { "NEW": "NEW", "PLAYING": "PLAYING", "ENDED": "ENDED" }

games = []

class Player:

  def __init__(self, game, author, name, hp = 20, ap = 20):
    self.game = game
    self.type = "PLAYER"
    self.team = "PLAYERS"
    self.author = author
    self.max_hp = hp
    self.hp = hp
    self.max_ap = ap
    self.ap = ap

    if (name):
      self.name = name
    else:
      self.name = author.name

  async def attack(self, ctx, enemy_name):
    enemy = self.game.get_npc_by_name(enemy_name)

    if enemy:
      dmg = randrange(6)
      enemy.hp = enemy.hp - dmg
      msg = "{name} attacks {target} and deals {dmg} damage. {target} has {hp} hit points left.".format(
        name = self.name,
        target = enemy.name,
        dmg = dmg,
        hp = enemy.hp
        )
      await ctx.channel.send(msg)
      self.game.mark_next_player_active()
      await self.game.next_turn(ctx)
      return
    else:
      msg = "{name} wants to attack {enemy_name} but it does not existz! {name} therefore is a Doofus.".format(
        name = self.name,
        enemy_name = enemy_name
        )
      await ctx.channel.send(msg)
      return

class Enemy:
  def __init__(self, game, name, hp = 20, ap = 20):
    self.game = game
    self.type = "NPC"
    self.team = "MONSTERS"
    self.max_hp = hp
    self.hp = hp
    self.max_ap = ap
    self.ap = ap
    self.name = name

  async def attack(self, ctx):
    target = None
    for player in self.game.players:
      if player.team == "PLAYERS":
        target = player

    if target:
      dmg = randrange(5)
      target.hp = target.hp - dmg
      msg = "{name} attacks {target} and deals {dmg} damage. {target} has {hp} hit points left.".format(
        name = self.name,
        target = target.name,
        dmg = dmg,
        hp = target.hp
        )
      await ctx.channel.send(msg)
      return

    else:
      msg = "{name} has no one to attack...".format(name = player.name)
      await ctx.channel.send(msg)
      return
      

class Game:

  def __init__(self, guild, channel):
    self.players = []
    self.guild = guild
    self.channel = channel
    self.state = game_state["NEW"]
    self.active = None

  def get_player(self, author):
    for i, o in enumerate(self.players):
      if o.type == "PLAYER" and o.author == author:
        return self.players[i]
    return None

  def get_npc_by_name(self, name):
    for i, o in enumerate(self.players):
      if o.type == "NPC" and o.name == name:
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

  async def start(self, ctx):
    self.state = game_state["PLAYING"]
    self.active = 0
    await self.next_turn(ctx)
    return

  def mark_next_player_active(self):
    if self.active == len(self.players) - 1:
      self.active = 0
    else:
      self.active += 1

  async def next_turn(self, ctx):
    player = self.players[self.active]
    msg = "It is {name}'s turn.".format(name=player.name)
    await ctx.channel.send(msg)
    if player.type == "NPC":
      await player.attack(ctx)
      self.mark_next_player_active()
      await self.next_turn(ctx)

    return

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
      player = Player(game, message.author, name)
      game.players.append(player)
      msg = "Player {name} has joined the game! :fist:".format(name = player.name)
      await message.channel.send(msg)
      return

  if cmd.startswith("leave game"):
    game = get_game()
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
    game = get_game()
    msg = game.get_game_status()

    if not msg:
      msg = "Game is fookin' empty mate. Nothing to see here..."

    await message.channel.send(msg)
    return
  
  if cmd.startswith("add enemy"):
    game = get_game()
    name = cmd.split("add enemy ",1)[1]
    enemy = Enemy(game, name, 20, 20)
    game.players.append(enemy)
    msg = "An enemy {name} was added to the game! :japanese_goblin:".format(name = name)
    await message.channel.send(msg)
    return

  if cmd.startswith("start game"):
    game = get_game()

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

  if cmd.startswith("attack enemy"):
    game = get_game()
    name = cmd.split("attack enemy ",1)[1]
    player = game.get_player(message.author) 
    await player.attack(message, name)
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