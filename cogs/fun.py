from discord.ext import commands
import traceback
import discord
import logging
import random
import re

log = logging.getLogger(__name__)

class Fun(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
        self.ball_answers = {}
        self.ball = ['It is certain', 'It is decidedly so', 'Without a doubt', 'Yes definitely', 'You may rely on it',
                     'As I see it, yes', 'Most likely', 'Outlook good', 'Yes', 'Signs point to yes',
                     'Reply hazy try again',
                     'Ask again later', 'Better not tell you now', 'Cannot predict now', 'Concentrate and ask again',
                     'Don\'t count on it', 'My reply is no', 'My sources say no', 'Outlook not so good',
                     'Very doubtful']

    @commands.command(pass_context=True, aliases=['pick'])
    async def choose(self, ctx, *, choices: str):
        """Choose randomly from the options you give. [p]choose this | that"""
        await ctx.send('I choose: ``{}``'.format(random.choice(choices.split("|"))))

    @commands.command(pass_context=True, aliases=['8ball'])
    async def ball8(self, ctx, *, msg: str):
        """Let the 8ball decide your fate. Ex: [p]8ball Will I get good?"""
        if ctx.message.author.id in self.ball_answers and msg in self.ball_answers[ctx.message.author.id]:
            answer = self.ball_answers[ctx.message.author.id][msg]
        else:
            answer = random.randint(0, 19)
            if ctx.message.author.id in self.ball_answers:
                self.ball_answers[ctx.message.author.id][msg] = answer
            else:
                self.ball_answers[ctx.message.author.id] = {}
                self.ball_answers[ctx.message.author.id][msg] = answer
        permissions = ctx.channel.permissions_for(ctx.me)
        if permissions.embed_links:
            if answer < 10:
                color = 0x008000
            elif 10 <= answer < 15:
                color = 0xFFD700
            else:
                color = 0xFF0000
            em = discord.Embed(color=color)
            em.add_field(name='\u2753 Question', value=msg)
            em.add_field(name='\ud83c\udfb1 8ball', value=self.ball[answer], inline=False)
            await ctx.send(content=None, embed=em)
        else:
            await ctx.send(f'\ud83c\udfb1 ``{self.ball[answer]}``')

    @commands.command()
    async def dice(self, ctx, *, msg="1"):
        """Roll dice. Optionally input # of dice and # of sides. Ex: [p]dice 5 12"""
        invalid = f'Invalid syntax. Ex: `{ctx.prefix}dice 4` - roll four normal dice. `{ctx.prefix}dice 4 12` - roll four 12 sided dice.'
        dice_rolls = []
        dice_roll_ints = []
        try:
            dice, sides = re.split("[d\s]", msg)
        except ValueError:
            dice = msg
            sides = "6"
        try:
            for roll in range(int(dice)):
                result = random.randint(1, int(sides))
                dice_rolls.append(str(result))
                dice_roll_ints.append(result)
        except ValueError:
            return await ctx.send(invalid)
        embed = discord.Embed(title="Dice rolls:", description=' '.join(dice_rolls))
        embed.add_field(name="Total:", value=sum(dice_roll_ints))
        await ctx.send(embed=embed)

def setup(bot):
    return
    f = Fun(bot)
    bot.add_cog(f)
