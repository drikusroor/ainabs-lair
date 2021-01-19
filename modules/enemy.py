from random import randrange

class Enemy:
  def __init__(self, game, name, hp = 20, ap = 5):
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
 