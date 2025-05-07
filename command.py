# MIT License
# Copyright (c) 2025 JinxedUp

import inspect
import asyncio
from typing import Any, Callable, Dict, List, Optional, Union
from .exceptions import (
    DiscordError,
    RateLimitError,
    PermissionError,
    HTTPError,
    NotFoundError,
    ForbiddenError
)

class CommandError(Exception):
    """Base exception for command-related errors"""
    pass

class MissingRequiredArgument(CommandError):
    """Raised when a required argument is missing"""
    def __init__(self, param_name: str):
        self.param_name = param_name
        super().__init__(f"Missing required argument: {param_name}")

class BadArgument(CommandError):
    """Raised when an argument cannot be converted to the required type"""
    def __init__(self, param_name: str, value: str, expected_type: type):
        self.param_name = param_name
        self.value = value
        self.expected_type = expected_type
        super().__init__(f"Could not convert '{value}' to {expected_type.__name__} for parameter {param_name}")

class CommandNotFound(CommandError):
    """Raised when a command is not found"""
    def __init__(self, name: str):
        self.name = name
        super().__init__(f"Command '{name}' not found")

class CommandInvokeError(CommandError):
    """Raised when an error occurs during command invocation"""
    def __init__(self, original: Exception):
        self.original = original
        super().__init__(f"Error in command: {str(original)}")

class Command:
    def __init__(self, name: str, callback: Callable, **kwargs):
        self.name = name
        self.callback = callback
        self.aliases = kwargs.get('aliases', [])
        self.help = kwargs.get('help', None)
        self._signature = self._parse_signature(callback)
        self._error_handler = None

    def _parse_signature(self, func):
        """Parse the function signature to get parameter information"""
        sig = inspect.signature(func)
        signature = {}
        
        for name, param in sig.parameters.items():
            if name == 'ctx':
                continue
                
            param_info = {
                'type': param.annotation if param.annotation != inspect.Parameter.empty else str,
                'required': param.default == inspect.Parameter.empty,
                'default': param.default if param.default != inspect.Parameter.empty else None
            }
            
            signature[name] = param_info
            
        return signature

    def error(self, func: Callable) -> 'Command':
        """Decorator to set the error handler for this command"""
        self._error_handler = func
        return self

    async def invoke(self, ctx, *args, **kwargs) -> Any:
        """Invoke the command with the given context and arguments"""
        try:
            # Check for required arguments
            for name, param in self._signature.items():
                if param['required'] and name not in kwargs:
                    raise MissingRequiredArgument(name)
                    
            # Convert arguments to their proper types
            converted_kwargs = {}
            for name, value in kwargs.items():
                param = self._signature.get(name)
                if param:
                    try:
                        converted_kwargs[name] = param['type'](value)
                    except (ValueError, TypeError) as e:
                        raise BadArgument(name, str(value), param['type'])
                        
            # Call the command
            return await self.callback(ctx, **converted_kwargs)
            
        except CommandError:
            raise
        except Exception as e:
            raise CommandInvokeError(e)

    @property
    def help_str(self) -> str:
        """Get a help string for this command"""
        help_str = f"{self.name}"
        
        # Add required arguments
        required = [name for name, param in self._signature.items() if param['required']]
        if required:
            help_str += f" <{' '.join(required)}>"
            
        # Add optional arguments
        optional = [name for name, param in self._signature.items() if not param['required']]
        if optional:
            help_str += f" [{' '.join(optional)}]"
            
        # Add help text if available
        if self.help:
            help_str += f"\n{self.help}"
            
        return help_str 
