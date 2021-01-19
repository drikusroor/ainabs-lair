import asyncio

from modules.player import Player
from modules.enemy import Enemy
from modules import template

game_state = { "NEW": "NEW", "PLAYING": "PLAYING", "ENDED": "ENDED" }

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

  async def add_player(self, ctx, player):
      self.players.append(player)

      if ctx:
        msg = "{name} has entered the game.".format(name=player.name)
        await ctx.channel.send(msg)
        await asyncio.sleep(.5)

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
    await asyncio.sleep(2)
    if player.type == "NPC":
      await player.attack(ctx)
      await asyncio.sleep(2)
      self.mark_next_player_active()
      await self.next_turn(ctx)

    return

  async def init_template(self, ctx, name):
    await template.init_template(ctx, self, name)