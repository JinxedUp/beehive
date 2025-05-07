# MIT License
# Copyright (c) 2025 JinxedUp
import random, asyncio, json, tls_client
from .utils import load_cookies, save_cookies
from .constants import USER_AGENTS

class RESTClient:
    def __init__(self, token):
        self.token = token
        self.session = aiohttp.ClientSession()

    async def get_user_info(self):
        """Get information about the bot user."""
        url = "https://discord.com/api/v9/users/@me"
        headers = {"Authorization": f"Bot {self.token}"}
        async with self.session.get(url, headers=headers) as resp:
            if resp.status == 200:
                data = await resp.json()
                print(f"Logged in as {data['username']}#{data['discriminator']}")

    async def get_user_info(self):
        """ Fetches the user info (selfbot's user ID) """
        url = "https://discord.com/api/v9/users/@me"
        response = await asyncio.to_thread(self.session.get, url)
        if response.status_code == 200:
            user_info = response.json()
            user_id = user_info["id"]  
            await self.command_handler.set_bot_user_id(user_info)  
            return user_info
        else:
            raise Exception(f"Failed to fetch user info: {response.status_code}")

    async def send_typing(self, channel_id):
        url = f"https://discord.com/api/v9/channels/{channel_id}/typing"
        await asyncio.to_thread(self.session.post, url)

    async def send_message(self, channel_id, content):
        await self.send_typing(channel_id)
        await asyncio.sleep(random.uniform(0.1, 0.3))
        url = f"https://discord.com/api/v9/channels/{channel_id}/messages"
        await asyncio.to_thread(self.session.post, url, json={ "content": content })
