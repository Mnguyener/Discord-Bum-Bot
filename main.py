import random

import discord

import re

import sqlite3

from datetime import datetime  # reference to the class instead of just the module

from table2ascii import table2ascii, PresetStyle # may not need
con = sqlite3.connect("messages.db")
cur = con.cursor()
print("Connected to SQLite")
cur.execute("""CREATE TABLE IF NOT EXISTS reactions (server INTEGER NOT NULL, creator INTEGER NOT NULL, key TEXT NOT NULL UNIQUE, 
value TEXT, time DATETIME)""")

def insert_rxn(_server, _creator, _key, _value, _time) -> int:
    try:
        cur.execute("""INSERT into reactions (server, creator, key, value, time) VALUES (?,?,?,?,?)""",
                    [_server, _creator, _key, _value, _time])  # tuple
        con.commit()  # save changes
        print("inserted")
        return 0

    except sqlite3.Error as error:
        print(error)
        return 1
def view_react(_key) -> "list":
    try:
        key_list = []
        rows_returned = cur.execute("""SELECT value FROM reactions WHERE key LIKE ?""", ["%" + _key + "%"])
        for row in rows_returned:
            key_list.append(row[0])
        return key_list
    except sqlite3.Error as error:
        print(error)
def view_all_react() -> "list":
    try:
        key_list = []
        rows_returned = cur.execute("""SELECT creator, key, value, time FROM reactions""")
        for row in rows_returned:
            key_list.append(row)
        return key_list
        output = table2ascii() # oh
    except sqlite3.Error as error:
        print(error)

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

        args = message.content.split()
        if len(args) == 0:
            return # ignore empty messages

        for i in args:
            result_set = cur.execute("""SELECT value FROM reactions WHERE key = ?""", [i])
            total_list = result_set.fetchall()
            if total_list:
                rand = random.choice(total_list)[0]
                await message.reply(rand)
                return

        # adding reactions to the table
        if args[0] == "$add":
            msg_stripped = message.content[len("$add"):]
            comma_idx = msg_stripped.find(",")
            if comma_idx != -1:
                server = message.guild.id
                creator = str(message.author.id)
                print(f"this is my id: {creator} and my server id: {server}")
                key = msg_stripped[1:comma_idx]

                value = msg_stripped[comma_idx + 1:]
                print(f"key:{key} value:{value}")
                time = datetime.today().strftime("%Y-%m-%d %H:%M:%S")
                print(f"time is {time}")
                success = insert_rxn(server, creator, key, value, time)
                if success == 0:
                    await message.reply("Reaction added!")
                else:
                    await message.reply("Error: value has already been added!")
            else:
                await message.reply("Syntax error.")
        if args[0] == "$view":
            if len(args) < 2:
                await message.reply("Please specify all or a specific key.")
                return
            elif args[1] == "all":
                pair_list = view_all_react()
                await message.reply(pair_list)
            else:
                pair_list = view_react(args[1])
                if not pair_list:
                    await message.reply("This key is not present in the table.")
                else:
                    await message.reply(pair_list)
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
                    if num not in range(2, 99):
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

intents = discord.Intents.default()
intents.message_content = True
client = MyClient(intents=intents)
with open("first-bot-token.txt") as f:
    content = f.read()
client.run(content)
