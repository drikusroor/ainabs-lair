from random import randrange
import asyncio

class Player:

  def __init__(self, game, author, name, hp = 20, ap = 5):
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
      await asyncio.sleep(2)
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
