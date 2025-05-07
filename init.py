# MIT License
# Copyright (c) 2025 JinxedUp

from .bot import Bot
from .command import Command, CommandError, MissingRequiredArgument, BadArgument, CommandNotFound, CommandInvokeError
from .context import Context, Message
from .exceptions import (
    DiscordError,
    RateLimitError,
    PermissionError,
    HTTPError,
    NotFoundError,
    ForbiddenError
)

__all__ = [
    'Bot',
    'Command',
    'Context',
    'Message',
    
    'CommandError',
    'MissingRequiredArgument',
    'BadArgument',
    'CommandNotFound',
    'CommandInvokeError',
    
    'DiscordError',
    'RateLimitError',
    'PermissionError',
    'HTTPError',
    'NotFoundError',
    'ForbiddenError'
]

__version__ = '0.1.0'
