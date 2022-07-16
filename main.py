import random

import discord

import re

def roll_die(e):
    if 99 >= e >= 2:
        return random.randrange(1, e + 1)  # rand num


class MyClient(discord.Client):
    async def on_ready(self):
        print('Logged on as {0}!'.format(self.user))

    async def on_message(self, message):
        if message.content.lower().find('deez') != -1:
            img_of_nuts = 'https://peanut-institute.com/wp-content/uploads/2017/08/peanut-home-focus.png'
            response_list = ['nuts', img_of_nuts]
            await message.reply(random.choice(response_list))

        if message.content.lower() == "l":
            await message.reply("+ ratio")
        if message.content.lower().find("tomatos") != -1 or message.content.lower().find("tomato") != -1:
            await message.reply("water spout")

        args = message.content.split()
        if args[0] == "$roll":
            if len(args) == 1:
                # error state: not enough arguments
                await message.reply("Not enough arguments!")
            elif not args[1].startswith("d"):
                # error state: doesn't start with "d"
                await message.reply("Your dice must start with 'd'")
            elif args[1] == "d":
                await message.reply("You forgor the number")
            elif not re.match("d\d+", args[1]):
                await message.reply("Input is not a number.")
            else:
                num_raw = args[1][1:]
                print(num_raw)
                try:
                    num = int(num_raw)
                    if num not in range(2,99):
                        # value out of range
                        return
                    output = roll_die(num)
                    await message.reply(f"Rolling a d{num}: you rolled a {output}!")
                except ValueError:
                    # number could not be parsed
                    await message.reply("Your number could not be parsed.")
                except:
                    await message.reply("Unknown error.")

        print('Message from {0.author}: {0.content}'.format(message))


client = MyClient()
with open("first-bot-token.txt") as f:
    content = f.read()
client.run(content)

