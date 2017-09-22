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
    invite_dicts = {}
    channel_dicts = {"274347674122190848": 360606080256180234}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.invite_updater = self.loop.create_task(self.update_invite_task())

    async def on_ready(self):
        print('Logged in as')
        print(self.user.name)
        print(self.user.id)
        print('------')
        await self.update_invite_dicts()

    async def update_invite_dicts(self):
        for guild in client.guilds:
            self.invite_dicts[str(guild.id)] = await self.parse_invites(guild)

    async def on_member_join(self, member):
        await self.log_invite_use(guild=member.guild, member=member)

    async def on_guild_channel_update(self, before, after):
        print(await before.invites())
        print(await after.invites())

    async def on_message(self, message):
        if message.content == "!!store":
            self.invites = await message.guild.invites()
        if message.content == "!!parse":
            await self.parse_invites(message.guild)
        if message.content == "!!output":
            for invite in self.invites:
                await client.get_channel(360606080256180234).send(str(invite.inviter) + " " + str(invite.uses))

    async def parse_invites(self, guild):
        new_invites = await guild.invites()
        new_invite_dict = {k:v for k,v in zip([invite.id for invite in new_invites], new_invites)}
        print("asdf")
        print(new_invite_dict)
        print("asdf")
        return new_invite_dict

    async def send_invite_log(self, joined, invite):
        time = joined.joined_at.isoformat(" ")[:16]
        # time = time[6:19] + " " + time[0:5]
        log_str = f"`[{time}]` :inbox_tray: `{joined} [{str(joined.id)}] joined from {invite.inviter} [{str(invite.inviter.id)}]'s invite [{invite.id}] [{invite.uses}/{invite.max_uses}] [{invite.max_age//3600}]`"
        target_channel = client.get_channel(self.channel_dicts[str(joined.guild.id)])
        print(target_channel)
        await target_channel.send(log_str)

    async def log_invite_use(self, guild, member):
        new_invite_dict = await self.parse_invites(guild)
        used_invites = await self.find_used_invite(guild, new_invite_dict)
        if len(used_invites) == 1:
            await self.send_invite_log(member, used_invites[0])
        else:
            print("Failed LUL")
        self.invite_dicts[str(guild.id)] = new_invite_dict

    async def find_used_invite(self, guild, new_invite_dict):
        changed_invites = []
        print(new_invite_dict)
        for key in new_invite_dict.keys():
            if new_invite_dict[key].uses != self.invite_dicts[str(guild.id)][key].uses:
                changed_invites.append(new_invite_dict[key])
        return changed_invites

    async def update_invite_task(self):
        await self.wait_until_ready()
        while not self.is_closed():
            await self.update_invite_dicts()
            await asyncio.sleep(0.5)

client = MyClient()

client.run(CONFIG.INVITE_TOKEN, bot=True)