# MIT License
# Copyright (c) 2025 JinxedUp
import re
from typing import Dict, List, Optional, Tuple, Union
from .command import Command, CommandError, MissingRequiredArgument, BadArgument, CommandNotFound, CommandInvokeError

class CommandHandler:
    def __init__(self, bot):
        self.bot = bot
        self._command_cache: Dict[str, Command] = {}
        self._arg_pattern = re.compile(r'("[^"]*"|\S+)')

    def _parse_args(self, content: str) -> Tuple[str, List[str]]:
        

        content = content[len(self.bot.command_prefix):].strip()
        if not content:
            return "", []

        parts = self._arg_pattern.findall(content)
        if not parts:
            return "", []

        command = parts[0].lower()
        args = []

        current_arg = []
        in_quotes = False

        for part in parts[1:]:
            if part.startswith('"'):
                in_quotes = True
                current_arg.append(part[1:])
            elif part.endswith('"') and in_quotes:
                in_quotes = False
                current_arg.append(part[:-1])
                args.append(' '.join(current_arg))
                current_arg = []
            elif in_quotes:
                current_arg.append(part)
            else:
                args.append(part)

        if current_arg:
            args.append(' '.join(current_arg))

        return command, args

    def _get_command(self, name: str) -> Optional[Command]:
        

        if name in self._command_cache:
            return self._command_cache[name]

        cmd = self.bot.commands.get(name)
        if cmd:

            self._command_cache[name] = cmd

            for alias in cmd.aliases:
                self._command_cache[alias] = cmd
        return cmd

    async def handle_command(self, content: str, channel_id: str) -> None:
       
        try:

            command_name, args = self._parse_args(content)
            if not command_name:
                return

            command = self._get_command(command_name)
            if not command:
                raise CommandNotFound(command_name)

            ctx = self.bot.get_context(channel_id)

            kwargs = {}
            for i, (name, param) in enumerate(command._signature.items()):
                if i < len(args):
                    arg_value = args[i]
                    if not arg_value:  
                        continue

                    if hasattr(param['type'], '__origin__'):
                        if param['type'].__origin__ is Union:

                            actual_type = param['type'].__args__[0]
                            try:
                                kwargs[name] = actual_type(arg_value)
                            except (ValueError, TypeError):
                                raise BadArgument(name, arg_value, actual_type)
                        else:
                            kwargs[name] = arg_value
                    else:
                        try:
                            kwargs[name] = param['type'](arg_value)
                        except (ValueError, TypeError):
                            raise BadArgument(name, arg_value, param['type'])
                elif not param['required']:

                    kwargs[name] = param['default']

            await command.invoke(ctx, **kwargs)

        except CommandError as e:

            if isinstance(e, MissingRequiredArgument):
                await ctx.send(f"Missing required argument: {e.param_name}")
            elif isinstance(e, BadArgument):
                await ctx.send(f"Invalid argument for {e.param_name}: {e.value} (expected {e.expected_type.__name__})")
            elif isinstance(e, CommandNotFound):
                await ctx.send(f"Command not found: {e.name}")
            elif isinstance(e, CommandInvokeError):
                await ctx.send(f"Error in command: {str(e.original)}")
            else:
                await ctx.send(str(e))
        except Exception as e:

            await ctx.send(f"An unexpected error occurred: {str(e)}")
