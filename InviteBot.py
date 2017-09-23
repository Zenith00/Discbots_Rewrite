import traceback
import discord
import asyncio
import re
import CONFIG
from PIL import Image
import requests
from io import BytesIO
import os
import utils.utils_text, utils.utils_image
import datetime

class MyClient(discord.Client):
    invite_dicts = {}
    channel_dicts = {"274347674122190848": 360606080256180234, "341371271432372224":360805855781715968, "280833874299191296":360898682721271818}

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
            try:
                self.invite_dicts[str(guild.id)] = await self.parse_invites(guild)
            except discord.errors.Forbidden:
                print("FAILED PERMS IN " + guild.name)

    async def on_member_join(self, member):
        await self.log_invite_use(guild=member.guild, member=member)

    async def on_member_remove(self, member):
        log_embed = discord.Embed(title=f"{member} [{member.id}] has left".replace(" ",' '*2) + ' ' * (145 - 2*len(str(member))) + "​​​​​​")
        if member.avatar_url:
            log_embed.set_thumbnail(url=member.avatar_url)
            color = utils.utils_image.average_color_url(member.avatar_url)
            log_embed.colour = discord.Colour(int(color, 16))
        log_embed.set_footer(text=datetime.datetime.utcnow().isoformat(" ")[:16])
        log_embed.add_field(name="Time in server", value=utils.utils_text.format_timedelta(datetime.datetime.utcnow() - member.joined_at))
        target_channel = client.get_channel(self.channel_dicts[str(member.guild.id)])
        await target_channel.send(embed=log_embed)

    async def on_guild_channel_update(self, before, after):
        pass
        # print(await before.invites())
        # print(await after.invites())

    async def on_message(self, message):
        pass
        # if message.content == "!!store":
        #     self.invites = await message.guild.invites()
        if message.content == "!!parse":
            await self.parse_invites(message.guild)
        if message.content == "!!output":
            for invite in await message.guild.invites():
                await message.channel.send(f"[{invite.id}] Owner: {str(invite.inviter)} Uses: {invite.uses} Expires: {invite.max_age//3600}")

    async def parse_invites(self, guild):
        new_invites = await guild.invites()
        new_invite_dict = {k:v for k,v in zip([invite.id for invite in new_invites], new_invites)}
        # print(new_invite_dict)
        return new_invite_dict

    async def send_invite_log(self, joined, invite):
        time = joined.joined_at.isoformat(" ")[:16]
        # time = time[6:19] + " " + time[0:5]
        log_embed = discord.Embed(title=f"{joined} [{joined.id}] has joined".replace(" ",' '*2) + ' ' * (140 - 2*len(str(joined))) + "​​​​​​")
        log_embed.add_field(name="Inviter", value="(" + str(invite.inviter) + f") [{invite.inviter.id}]", inline=False)
        log_embed.add_field(name="Invite ID", value=invite.id)
        log_embed.add_field(name="Invite Uses", value="{invite_uses}/{invite_max}".format(invite_uses=invite.uses, invite_max=invite.max_uses if invite.max_uses != 0 else "∞"))
        log_embed.add_field(name="Invite Expiration", value="in {}".format(utils.utils_text.format_timedelta(datetime.timedelta(seconds=invite.max_age))) if invite.max_age != 0 else "Never")
        if joined.avatar_url:
            log_embed.set_thumbnail(url=joined.avatar_url)
            color = utils.utils_image.average_color_url(joined.avatar_url)
            log_embed.colour = discord.Colour(int(color, 16))
        log_embed.set_footer(text=datetime.datetime.utcnow().isoformat(" ")[:16])

        log_str = f"`[{time}]` :inbox_tray: `{joined} [{str(joined.id)}] joined from {invite.inviter} [{str(invite.inviter.id)}]'s invite [{invite.id}] [{invite.uses}/{invite.max_uses}] [{invite.max_age//3600}]`"
        target_channel = client.get_channel(self.channel_dicts[str(joined.guild.id)])
        await target_channel.send(embed=log_embed)

    async def log_invite_use(self, guild, member):
        new_invite_dict = await self.parse_invites(guild)
        used_invites = await self.find_used_invite(guild, new_invite_dict)
        if len(used_invites) == 1:
            await self.send_invite_log(member, used_invites[0])
        else:
            print(used_invites)
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
            await asyncio.sleep(0.2)

client = MyClient()

client.run(CONFIG.INVITE_TOKEN, bot=True)