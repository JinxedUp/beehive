import asyncio
import httpx
import random
import time
from typing import Dict, Optional, List, Any
from .command_handler import CommandHandler
from .context import Context
from .gateway import GatewayClient
from .command import Command, CommandError, BadArgument, MissingRequiredArgument, CommandNotFound, CommandInvokeError

class Bot:
    def __init__(self, command_prefix="!", intents=None, is_bot=False):
        print("Initializing bot...")
        self.command_prefix = command_prefix
        self.intents = intents or {}
        self.commands: Dict[str, Command] = {}
        self.events = {}
        self.session = httpx.AsyncClient()
        self.command_handler = CommandHandler(self)
        self.token = None
        self.user_id = None
        self.is_bot = is_bot
        self._last_message_time = 0
        self._message_queue = asyncio.Queue()
        self._message_task = None
        self._context_cache: Dict[str, Context] = {}
        print(f"Bot initialized with prefix: {command_prefix}")

@self.command(name="help")
async def help_command(ctx, *, command: Optional[str] = None):
    """Shows help for all commands or a specific command."""
    if not command:
        if not self.commands:
            await ctx.send("No commands available.")
            return

        help_msg = "**Available Commands:**\n"
        for name, cmd in sorted(self.commands.items()):
            help_msg += f"• `{self.command_prefix}{name}`"
            if hasattr(cmd, 'aliases') and cmd.aliases:
                help_msg += f" (aliases: {', '.join(cmd.aliases)})"
            help_msg += f": {cmd.description or 'No description.'}\n"
        await ctx.send(help_msg)
        return

    command_lower = command.lower()
    cmd = None
    for name, c in self.commands.items():
        if name.lower() == command_lower or (hasattr(c, 'aliases') and command_lower in [alias.lower() for alias in c.aliases]):
            cmd = c
            break

    if not cmd:
        await ctx.send(f"Command `{command}` not found.")
        return

    help_msg = f"**{self.command_prefix}{cmd.name}**\n"
    if hasattr(cmd, 'aliases') and cmd.aliases:
        help_msg += f"Aliases: {', '.join(cmd.aliases)}\n"
    help_msg += f"Description: {cmd.description or 'No description.'}\n"

    if hasattr(cmd, '_signature') and cmd._signature:
        help_msg += "\nParameters:\n"
        for pname, param in cmd._signature.items():
            required = "Required" if param.get('required', False) else "Optional"
            ptype = param.get('type', str).__name__
            help_msg += f"- {pname} ({ptype}, {required})"
            if param.get('description'):
                help_msg += f": {param['description']}"
            help_msg += "\n"

    await ctx.send(help_msg)

    def command(self, name=None):
        """Command decorator"""
        def decorator(func):
            cmd_name = name or func.__name__
            self.commands[cmd_name] = Command(cmd_name, func)
            print(f"Registered command: {cmd_name}")
            return self.commands[cmd_name]
        return decorator

    def remove_command(self, name: str):
        """Remove a command by name"""
        if name in self.commands:
            del self.commands[name]
            print(f"Removed command: {name}")

    def event(self, name):
        """Event decorator"""
        def decorator(func):
            self.events[name] = func
            print(f"Registered event handler: {name}")
            return func
        return decorator

    def get_context(self, channel_id: str, message: Optional[Dict[str, Any]] = None) -> Context:
        """Get or create a context for a channel"""
        if channel_id in self._context_cache:
            ctx = self._context_cache[channel_id]
            if message:
                ctx.message = Message(message)
            return ctx

        ctx = Context(self, channel_id, message)
        self._context_cache[channel_id] = ctx
        return ctx

    async def handle(self, event_data):
        """Handle incoming gateway events"""
        if not isinstance(event_data, dict):
            print(f"Received non-dict event: {event_data}")
            return

        event_type = event_data.get("_event_type")
        print(f"Bot handling event type: {event_type}")

        if event_type in self.events:
            print(f"Calling event handler for: {event_type}")
            await self.events[event_type](event_data)

        if event_type == "MESSAGE_CREATE":
            print("Processing MESSAGE_CREATE event")
            await self.on_message(event_data)

    async def handle_message(self, content: str, channel_id: str):
        """Handles incoming messages and checks if they're commands"""
        try:
            print(f"Handling message: {content}")
            if not content or not content.startswith(self.command_prefix):
                return

            await self.command_handler.handle_command(content, channel_id)
        except Exception as e:
            print(f"Error handling message: {e}")

    async def on_message(self, message):
        """Triggered when the bot receives a message"""
        try:
            if not isinstance(message, dict):
                print("Received invalid message format")
                return

            author_id = str(message.get("author", {}).get("id"))
            if author_id != str(self.user_id):
                return

            print("Message is from selfbot, processing...")
            content = message.get("content", "")
            channel_id = message.get("channel_id")
            if not channel_id:
                print("No channel_id in message")
                return

            print(f"Message content: {content}")
            print(f"Channel ID: {channel_id}")
            await self.handle_message(content, channel_id)
        except Exception as e:
            print(f"Error in on_message: {e}")

    async def connect(self):
        """Connect to Discord's gateway"""
        try:
            print("Starting gateway connection...")
            if not self.token:
                raise ValueError("No token provided")
            gateway = GatewayClient(self.token, self)
            await gateway.connect()
        except Exception as e:
            print(f"Error connecting to gateway: {e}")
            raise

    def run(self, token):
        """Runs the bot"""
        try:
            print("Starting bot...")
            if not token:
                raise ValueError("No token provided")
            self.token = token
            asyncio.run(self.connect())
        except KeyboardInterrupt:
            print("\nBot shutting down...")
        except Exception as e:
            print(f"Error running bot: {e}")
        finally:
            if hasattr(self, 'session'):
                try:
                    asyncio.run(self.session.aclose())
                except Exception as e:
                    print(f"Error closing session: {e}")

    @self.command()
    async def spam(ctx, text: str, count: int = 0, delay: float = 2.0):
        """
        Spam a message in the channel.
        Usage:
          !spam <text>            
          !spam <text> <count>    
          !spam <text> <count> <delay>  
        """
        await ctx.spam(text, count=count, delay=delay)
