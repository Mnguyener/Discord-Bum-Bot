import random

import discord

import re

import sqlite3

from datetime import datetime  # reference to the class instead of just the module

import asyncio # for timeout error

con = sqlite3.connect("messages.db")
cur = con.cursor()
print("Connected to SQLite")
cur.execute("""CREATE TABLE IF NOT EXISTS reactions (id INTEGER PRIMARY KEY AUTOINCREMENT, server INTEGER NOT NULL, c_id INTEGER NOT NULL, c_name INTEGER NOT NULL, key TEXT, 
value TEXT, time DATETIME)""")

def insert_rxn(_server, _c_id,_c_name, _key, _value, _time):
    try:
        cur.execute("""INSERT into reactions (server, c_id, c_name, key, value, time) VALUES (?,?,?,?,?,?)""",
                    [_server, _c_id, _c_name, _key, _value, _time])  # tuple
        con.commit()  # save changes
        print("inserted")
        return 0

    except sqlite3.Error as error:
        print(error)
        return 1
def view_react(_server, _key = None)-> tuple:
    try:
        key_list = []
        if _key:
            result_set = cur.execute("""SELECT id, c_id, key, value, time FROM reactions WHERE key = ? AND server = ?""",[_key, _server])
            rows_fetched = result_set.fetchall()
        else:
            result_set = cur.execute("""SELECT id, c_id, key, value, time FROM reactions WHERE server = ?""", [_server])
            rows_fetched = result_set.fetchall()
        if not rows_fetched:
            return
        for row in rows_fetched:
                key_list.append(row)
        return key_list  
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
        if len(args) == 0: # ignore empty messages
            return 
        if args[0] == "$del":
            if len(args) < 2: 
                await message.reply("Please specify a key to delete.")
            else:
                server = message.guild.id 
                result_set = cur.execute("""SELECT id, key, value FROM reactions WHERE key = ? AND server = ?""", [args[1], server])
                return_list = result_set.fetchall()
                view_list = view_react(server, args[1])
                listings = ""
               
                if return_list:
                    if len(return_list) == 1:
                        cur.execute("""DELETE FROM reactions WHERE key = ? AND server = ?""", [args[1], server])
                        con.commit()  # save changes
                        my_embed = discord.Embed(title="Deletion",
                                         description=f"{return_list[0][1]}:{return_list[0][2]}",
                                         colour=0xC0C0F2)
                        await message.reply(embed=my_embed)
                    else:
                        for pairs in view_list:
                            print(pairs)
                            listings += "[" + str(pairs[0]) + "] " + pairs[2] + ": " + pairs[3] +"\n"
                        my_embed = discord.Embed(title="Choose which number row to delete.",
                                         description=f"{listings}",
                                         colour=0xC0C0F2)
                        await message.reply (embed=my_embed)
                        # This will make sure that the response will only be registered if the following
                        # conditions are met:
                        index_list = []
                        for i in view_list: # this is a tuple
                                index = i[0]
                                index_list.append(index)
                        def check(msg):                        
                            return int(msg.content) in index_list
                        try:
                            usr_msg = await client.wait_for("message", check=check, timeout=30)  # returns message OBJECT
                            row = cur.execute("""SELECT key, value FROM reactions WHERE id = ?""", [usr_msg.content])
                            fetch_deleted = row.fetchall()
                            cur.execute("""DELETE FROM reactions WHERE id = ?""", [int(usr_msg.content)])
                            con.commit()  # save changes
                            my_embed = discord.Embed(title="Deletion",
                                         description=f"{fetch_deleted[0][0]}: {fetch_deleted[0][1]}",
                                         colour=0xC0C0F2)
                            await message.reply(embed=my_embed)
                        except asyncio.TimeoutError:
                            await message.reply("Deletion canceled: you timed out.")
                        except sqlite3.Error as error:
                            print(error)
                else:
                    await message.reply("The key could not be found in the table to delete.")
                    
        # adding reactions to the table
        if args[0] == "$add": 
            msg_stripped = message.content[len("$add"):]
            comma_idx = msg_stripped.find(",")
            if comma_idx != -1:
                server = message.guild.id 
                c_id = str(message.author.id)
                c_name = message.author.name
                print(f"this is my id: {c_id} and my server id: {server}")
                key = msg_stripped[1:comma_idx]
                value = msg_stripped[comma_idx + 1:]
                print(f"key:{key} value:{value}")
                time = datetime.today().strftime("%a, %b %d, %Y")
                print(f"time is {time}")
                success = insert_rxn(server, c_id, c_name, key, value, time)
                if success == 0:
                    await message.reply("Reaction added!")
                else:
                    await message.reply("Error: value has already been added!")
            else:
                await message.reply("Syntax error.") 
        if args[0] == "$view": 
            server = message.guild.id
            if len(args) < 2:
                await message.reply("Please include 'all' or a specific key.")
                return
            elif args[1] == "all":
                pair_list = view_react(server) 
            else:
                pair_list = view_react(server, args[1])
            if not pair_list:
                await message.reply("Error: cannot be viewed in the table.")
                return
            listings = ""
            for pairs in pair_list:
                # grab col: 1,2,3,4
                _c_id = str(pairs[1])
                _key = pairs[2]
                _val= pairs[3]
                listings += "<@" +_c_id + ">\n" + "**" + _key + ":" + "**" + _val + "\n"
            my_embed = discord.Embed(title="Available Pairings",
                                        description=f"{listings}",
                                        colour=0xd2e5d0)
            await message.reply(embed=my_embed)
        # this is where the bot reacts
        for i in args: 
            usr_server_id = message.guild.id
            result_set = cur.execute("""SELECT value FROM reactions WHERE key = ? AND server = ?""", [i, usr_server_id])
            total_list = result_set.fetchall()
            if total_list:
                rand = random.choice(total_list)[0]
                await message.reply(rand)
                return
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