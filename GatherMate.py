import traceback
import discord
import asyncio
import re
import CONFIG
from PIL import Image
import requests
from io import BytesIO
import os


class MyClient(discord.Client):
    async def on_ready(self):
        print('Logged in as')
        print(self.user.name)
        print(self.user.id)
        print('------')

    async def on_guild_emojis_update(self, guild, before, after):
        print("Updating... " + guild.name)
        for emoji in after:
            try:
                await import_emoji(emoji=emoji)
            except:
                print(traceback.format_exc())


    async def on_message(self, message):
        if message.author == self.user:
            print(message.guild.name)
            if message.content.startswith('!!rebuild'):
                await message.delete()
                for emoji in client.emojis:
                    await import_emoji(emoji)


async def import_emoji(emoji):
    try:
        target = None
        guild_name = re.sub('[^\w\-_\. ]', '_', emoji.guild.name)
        for direntry in os.scandir(CONFIG.dir):
            if direntry.is_dir():
                if str(emoji.guild.id) in direntry.name:
                    target = [direntry.name, direntry.path]

        if target:
            target_folder = str(emoji.guild.id) + guild_name

            if target[0] != target_folder:
                os.rename(target[1], target_folder)
                target[1] = target_folder
        else:
            target = (str(emoji.guild.id) + guild_name, os.path.join(CONFIG.dir, guild_name))
            make_dir(os.path.join(CONFIG.dir, target[0]))


        response = requests.get(emoji.url)
        img = Image.open(BytesIO(response.content))
        img_path = os.path.join(target[1], re.sub('[^\w\-_\. ]', '_', emoji.name)+".png")
        if not os.path.exists(img_path):
            try:
                img.save(img_path, "PNG")
            except FileNotFoundError:
                asyncio.sleep(1)
            except:
                print(traceback.format_exc())
    except:
        print(traceback.format_exc())

def make_dir(directory):
    import os
    import errno
    try:
        os.makedirs(directory)
    except OSError as e:
        if e.errno != errno.EEXIST:
            raise

client = MyClient()

client.run(CONFIG.AUTH_TOKEN, bot=False)