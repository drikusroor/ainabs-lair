from modules import enemy
# local modules
from modules.player import Player
from modules.enemy import Enemy

async def init_template(ctx, game, name):
    if name == "one":
        return await template_one(ctx, game)

async def template_one(ctx, game):
    enemy_one = Enemy(game, "Goblino", 20, 5)
    enemy_two = Enemy(game, "Goblina", 15, 6)
    enemy_three = Enemy(game, "Goblinho", 8, 3)

    await game.add_player(ctx, enemy_one)
    await game.add_player(ctx, enemy_two)
    await game.add_player(ctx, enemy_three)
    return