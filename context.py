# MIT License
# Copyright (c) 2025 JinxedUp

import asyncio
import random
from typing import Optional, List, Dict, Any
from .exceptions import DiscordError, RateLimitError, PermissionError, HTTPError, NotFoundError, ForbiddenError

class Message:
    def __init__(self, data: Dict[str, Any]):
        self.id = data.get('id')
        self.content = data.get('content', '')
        self.author = data.get('author', {})
        self.channel_id = data.get('channel_id')
        self.guild_id = data.get('guild_id')
        self.timestamp = data.get('timestamp')
        self.edited_timestamp = data.get('edited_timestamp')
        self.attachments = data.get('attachments', [])
        self.embeds = data.get('embeds', [])
        self.reactions = data.get('reactions', [])
        self.raw_data = data

class Context:
    def __init__(self, bot, channel_id: str, message: Optional[Dict[str, Any]] = None):
        self.bot = bot
        self.channel_id = channel_id
        self.message = Message(message) if message else None
        self._guild = None
        self._channel = None
        self._author = None
        self._headers = {
            "Authorization": f"Bot {self.bot.token}" if self.bot.is_bot else self.bot.token,
            "Content-Type": "application/json"
        }

    async def send(self, content: str) -> Message:
        """Send a message to the channel"""
        try:
            response = await self.bot.session.post(
                f"https://discord.com/api/v9/channels/{self.channel_id}/messages",
                headers=self._headers,
                json={"content": content}
            )

            if response.status_code == 429:  
                retry_after = float(response.headers.get('Retry-After', 1))
                raise RateLimitError(retry_after)
            elif response.status_code == 403:
                raise PermissionError("send_messages")
            elif response.status_code == 404:
                raise NotFoundError("Channel")
            elif response.status_code >= 400:
                raise HTTPError(response.status_code, response.text)

            return Message(response.json())
        except Exception as e:
            if not isinstance(e, DiscordError):
                raise HTTPError(0, str(e))
            raise

    async def edit(self, message_id: str, content: str) -> Message:
        """Edit a message"""
        try:
            response = await self.bot.session.patch(
                f"https://discord.com/api/v9/channels/{self.channel_id}/messages/{message_id}",
                headers=self._headers,
                json={"content": content}
            )

            if response.status_code == 429:
                retry_after = float(response.headers.get('Retry-After', 1))
                raise RateLimitError(retry_after)
            elif response.status_code == 403:
                raise PermissionError("manage_messages")
            elif response.status_code == 404:
                raise NotFoundError("Message")
            elif response.status_code >= 400:
                raise HTTPError(response.status_code, response.text)

            return Message(response.json())
        except Exception as e:
            if not isinstance(e, DiscordError):
                raise HTTPError(0, str(e))
            raise

    async def delete(self, message_id: str) -> None:
        """Delete a message"""
        try:
            response = await self.bot.session.delete(
                f"https://discord.com/api/v9/channels/{self.channel_id}/messages/{message_id}",
                headers=self._headers
            )

            if response.status_code == 429:
                retry_after = float(response.headers.get('Retry-After', 1))
                raise RateLimitError(retry_after)
            elif response.status_code == 403:
                raise PermissionError("manage_messages")
            elif response.status_code == 404:
                raise NotFoundError("Message")
            elif response.status_code >= 400:
                raise HTTPError(response.status_code, response.text)
        except Exception as e:
            if not isinstance(e, DiscordError):
                raise HTTPError(0, str(e))
            raise

    async def bulk_delete(self, message_ids: List[str]) -> None:
        """Bulk delete messages"""
        try:
            response = await self.bot.session.post(
                f"https://discord.com/api/v9/channels/{self.channel_id}/messages/bulk-delete",
                headers=self._headers,
                json={"messages": message_ids}
            )

            if response.status_code == 429:
                retry_after = float(response.headers.get('Retry-After', 1))
                raise RateLimitError(retry_after)
            elif response.status_code == 403:
                raise PermissionError("manage_messages")
            elif response.status_code == 404:
                raise NotFoundError("Channel")
            elif response.status_code >= 400:
                raise HTTPError(response.status_code, response.text)
        except Exception as e:
            if not isinstance(e, DiscordError):
                raise HTTPError(0, str(e))
            raise

    async def add_reaction(self, message_id: str, emoji: str) -> None:
        """Add a reaction to a message"""
        try:

            encoded_emoji = emoji.encode('utf-8').hex()
            response = await self.bot.session.put(
                f"https://discord.com/api/v9/channels/{self.channel_id}/messages/{message_id}/reactions/{encoded_emoji}/@me",
                headers=self._headers
            )

            if response.status_code == 429:
                retry_after = float(response.headers.get('Retry-After', 1))
                raise RateLimitError(retry_after)
            elif response.status_code == 403:
                raise PermissionError("add_reactions")
            elif response.status_code == 404:
                raise NotFoundError("Message")
            elif response.status_code >= 400:
                raise HTTPError(response.status_code, response.text)
        except Exception as e:
            if not isinstance(e, DiscordError):
                raise HTTPError(0, str(e))
            raise

    async def remove_reaction(self, message_id: str, emoji: str) -> None:
        """Remove a reaction from a message"""
        try:
            encoded_emoji = emoji.encode('utf-8').hex()
            response = await self.bot.session.delete(
                f"https://discord.com/api/v9/channels/{self.channel_id}/messages/{message_id}/reactions/{encoded_emoji}/@me",
                headers=self._headers
            )

            if response.status_code == 429:
                retry_after = float(response.headers.get('Retry-After', 1))
                raise RateLimitError(retry_after)
            elif response.status_code == 403:
                raise PermissionError("add_reactions")
            elif response.status_code == 404:
                raise NotFoundError("Message")
            elif response.status_code >= 400:
                raise HTTPError(response.status_code, response.text)
        except Exception as e:
            if not isinstance(e, DiscordError):
                raise HTTPError(0, str(e))
            raise

    async def get_reactions(self, message_id: str, emoji: str) -> List[Dict[str, Any]]:
        """Get users who reacted with an emoji"""
        try:
            encoded_emoji = emoji.encode('utf-8').hex()
            response = await self.bot.session.get(
                f"https://discord.com/api/v9/channels/{self.channel_id}/messages/{message_id}/reactions/{encoded_emoji}",
                headers=self._headers
            )

            if response.status_code == 429:
                retry_after = float(response.headers.get('Retry-After', 1))
                raise RateLimitError(retry_after)
            elif response.status_code == 403:
                raise PermissionError("read_message_history")
            elif response.status_code == 404:
                raise NotFoundError("Message")
            elif response.status_code >= 400:
                raise HTTPError(response.status_code, response.text)

            return response.json()
        except Exception as e:
            if not isinstance(e, DiscordError):
                raise HTTPError(0, str(e))
            raise

    async def get_channel_info(self) -> Dict[str, Any]:
        """Get information about the current channel"""
        try:
            response = await self.bot.session.get(
                f"https://discord.com/api/v9/channels/{self.channel_id}",
                headers=self._headers
            )

            if response.status_code == 429:
                retry_after = float(response.headers.get('Retry-After', 1))
                raise RateLimitError(retry_after)
            elif response.status_code == 403:
                raise PermissionError("view_channel")
            elif response.status_code == 404:
                raise NotFoundError("Channel")
            elif response.status_code >= 400:
                raise HTTPError(response.status_code, response.text)

            return response.json()
        except Exception as e:
            if not isinstance(e, DiscordError):
                raise HTTPError(0, str(e))
            raise

    async def get_guild_info(self) -> Dict[str, Any]:
        """Get information about the current guild"""
        if not self.message or not self.message.guild_id:
            raise NotFoundError("Guild")

        try:
            response = await self.bot.session.get(
                f"https://discord.com/api/v9/guilds/{self.message.guild_id}",
                headers=self._headers
            )

            if response.status_code == 429:
                retry_after = float(response.headers.get('Retry-After', 1))
                raise RateLimitError(retry_after)
            elif response.status_code == 403:
                raise PermissionError("view_guild")
            elif response.status_code == 404:
                raise NotFoundError("Guild")
            elif response.status_code >= 400:
                raise HTTPError(response.status_code, response.text)

            return response.json()
        except Exception as e:
            if not isinstance(e, DiscordError):
                raise HTTPError(0, str(e))
            raise

    async def get_user_info(self, user_id: str) -> Dict[str, Any]:
        """Get information about a user"""
        try:
            response = await self.bot.session.get(
                f"https://discord.com/api/v9/users/{user_id}",
                headers=self._headers
            )

            if response.status_code == 429:
                retry_after = float(response.headers.get('Retry-After', 1))
                raise RateLimitError(retry_after)
            elif response.status_code == 404:
                raise NotFoundError("User")
            elif response.status_code >= 400:
                raise HTTPError(response.status_code, response.text)

            return response.json()
        except Exception as e:
            if not isinstance(e, DiscordError):
                raise HTTPError(0, str(e))
            raise

    async def get_message_history(self, limit: int = 50, before: Optional[str] = None) -> List[Message]:
        """Get message history for the channel"""
        try:
            params = {"limit": limit}
            if before:
                params["before"] = before

            response = await self.bot.session.get(
                f"https://discord.com/api/v9/channels/{self.channel_id}/messages",
                headers=self._headers,
                params=params
            )

            if response.status_code == 429:
                retry_after = float(response.headers.get('Retry-After', 1))
                raise RateLimitError(retry_after)
            elif response.status_code == 403:
                raise PermissionError("read_message_history")
            elif response.status_code == 404:
                raise NotFoundError("Channel")
            elif response.status_code >= 400:
                raise HTTPError(response.status_code, response.text)

            return [Message(msg) for msg in response.json()]
        except Exception as e:
            if not isinstance(e, DiscordError):
                raise HTTPError(0, str(e))
            raise

    async def spam(self, content: str, count: int = 0, delay: float = 2.0) -> None:
        """Spam a message in the channel. If count=0, spam infinitely. Delay is in seconds (default 2s)."""
        sent = 0
        try:
            while count == 0 or sent < count:
                await self.send(content)
                sent += 1
                await asyncio.sleep(delay)
        except Exception as e:
            if not isinstance(e, DiscordError):
                raise HTTPError(0, str(e))
            raise
