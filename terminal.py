import inspect
import functools
import collections
import os
import readline

HISTORY_FILE = ""
HISTORY_LENGTH = 100

def init(alias):
	global HISTORY_FILE
	HISTORY_FILE = os.path.join(os.path.expanduser('~'), '.' + alias)
	if not os.path.exists(HISTORY_FILE):
		with open(HISTORY_FILE, 'w'): pass

def _make_completer(commands):
	def completer(text, state):
		result = [command for command in commands if command.startswith(text)] + [None]
		return result[state]
	return completer

def _save_history():
	readline.append_history_file(HISTORY_LENGTH, HISTORY_FILE)

def _read_history():
	readline.read_history_file(HISTORY_FILE)
	readline.set_history_length(HISTORY_LENGTH)


def _command(command_func):

	command_func.__name__ = command_func.__name__[8:]
	if command_func.__doc__:
		command_func.__doc__ += "\n\t\tPress 'q' to exit this help message"
	else:
		command_func.__doc__ = "\t\tThere is no documentation on this command.\n\t\tPress 'q' to exit this help message."

	types = command_func.__annotations__
	args_list = inspect.getfullargspec(command_func).args
	varargs = inspect.getfullargspec(command_func).varargs
	command_name = command_func.__name__

	@functools.wraps(command_func)
	def wrapper(*args, **kwargs):
		if varargs is None:
			if len(args) > len(args_list):
				return f"{command_name} takes only {len(args_list) - 1} parameter(s) but {len(args) - 1} where passed."

		if len(args) < len(args_list):
			missing_args = [f"'{arg}'" for arg in args_list[len(args):]]
			missing_args_str = ', '.join(missing_args[:-1]) + ' and ' + missing_args[-1] if len(missing_args) > 1 else missing_args[0]
			return f"{command_name} is missing {len(args_list) - len(args)} requierd arguments: {missing_args_str}"

		sanetized_args = [args[0]]
		for arg_name, arg in zip(args_list[1:], args[1:]):
			try:
				sanetized_args.append(types[arg_name](arg))
			except (ValueError, TypeError):
				return f"'{arg_name}' must be of type: '{types[arg_name]}'. For more information see 'help {command_name}'."

		for vararg in args[len(args_list):]:
			try:
				sanetized_args.append(types[varargs](vararg))
			except (ValueError, TypeError):
				return f"All '{varargs}' must be of type: '{types[varargs]}'. For more information see 'help {command_name}'."

		return command_func(*sanetized_args, **kwargs)

	wrapper.__name__ = command_func.__name__
	wrapper.__module__ = 'non-existing'

	_remove_self_from_signature(command_func, wrapper)
	return wrapper

def _remove_self_from_signature(command, wrapper):
	args_list = inspect.getfullargspec(command).args
	varargs = inspect.getfullargspec(command).varargs
	arguments = []
	exec(f"def formatting_wrapper({', '.join(args_list[1:])}{f', *{varargs}' if varargs is not None else ''}): pass")
	wrapper.__wrapped__ = locals()['formatting_wrapper']

def _command_type_checker(terminal):
	for key, value in terminal.__dict__.items():
		if key.startswith('command_'):
			setattr(terminal, key, _command(value))
	return terminal

class _FunctionDescriptor:
	def __init__(self, name):
		self.name = name

	def __get__(self, instance, cls):
		possible = []
		for other_cls in cls.__mro__:
			for function in other_cls.__dict__:
				if callable(other_cls.__dict__[function]) and function.startswith(self.name) and self.name != function:
					possible.append(function)
		possible.sort(key=lambda x:x[len(self.name):])

		def selector(*args, **kwargs):
			for function in possible[:-1]:
				if len(args) == int(function[len(self.name):]) - 1:
					return getattr(instance, function)(*args, **kwargs)
			if '+' in possible[-1][len(self.name):] or len(args) == int(possible[-1][len(self.name):]) - 1:
				return getattr(instance, possible[-1])(*args, **kwargs)
			else:
				return getattr(instance, possible[0])(*args, **kwargs)

		def formatting_wrapper(): pass
		selector.__doc__ = getattr(instance, possible[0]).__doc__ if getattr(instance, possible[0]).__doc__ else ''
		selector.__name__ = self.name[8:]
		selector.__wrapped__ = formatting_wrapper
		selector.__module__ = 'non-existing'

		return selector


	def __set__(self, instance, value):
		instance.__dict__[self.name] = value

	def __delete__(self, instance):
		del instance.__dict__[self.name]

class _MultiKeyDict(dict):
	def __setitem__(self, key, value):
		if value not in self.get(key, []):
			super().__setitem__(key, self.get(key, []) + [value])
		else:
			self.get(key).remove(value)
			super().__setitem__(key, self.get(key, []) + [value])

class _TerminalMeta(type):
	def __prepare__(self, *args):
		return _MultiKeyDict()

	def __new__(cls, clsname, bases, clsdict):
		filtered_clsdict = {}
		for key, item_list in clsdict.items():
			if len(item_list) == 1:
				filtered_clsdict[key] = item_list[0]
			else:
				filtered_clsdict[key] = _FunctionDescriptor(key)
				for func in item_list:
					args, varargs, *_ = inspect.getfullargspec(func)
					filtered_clsdict[key + str(len(args)) + ('+' if varargs is not None else '')] = func
		for key, item in filtered_clsdict.items():
			if key.startswith('command_') and not isinstance(item, _FunctionDescriptor):
				filtered_clsdict[key] = _command(item)
		return super().__new__(cls, clsname, bases, filtered_clsdict)


class Options:
	def __init__(self, container):
		self.container = container

	def __call__(self, value):
		if value not in self.container:
			raise ValueError
		return value

	def __str__(self):
		return "\b" * 10 + f"one of the following: '{self.container}"

class Terminal(metaclass=_TerminalMeta):

	def __init__(self, prompt='> '):
		self.prompt = prompt
		self.running = False
		try:
			self._format_help()
		except KeyError:
			pass

		readline.parse_and_bind('tab: complete')
		readline.set_completer(_make_completer(self._get_commands_name()))
		readline.set_auto_history(True)
		_read_history()

	def _get_commands_name(self):
		return [attr[8:] for cls in type(self).__mro__
		                 for attr in cls.__dict__
		                 if attr.startswith('command_') and (not attr.endswith('+') and not attr[-1].isnumeric())]

	def _format_help(self):
		commands = ""
		for cls in type(self).__mro__:
			for attr in cls.__dict__:
				if attr.startswith('command_') and (not attr.endswith('+') and not attr[-1].isnumeric()):
					commands += f"\t\t\t{attr[8:]: <16}-\t"
					if callable(cls.__dict__[attr]):
						commands += cls.__dict__[attr].__doc__.strip().split('\n')[0] + "\n"
					else:
						commands += getattr(self, attr).__doc__.strip().split('\n')[0] + "\n"
		Terminal.command_help1.__doc__ = Terminal.command_help1.__doc__.format(commands[2:])


	def command_help(self, command:str):
		for cls in type(self).__mro__:
			if 'command_' + command in cls.__dict__:
				if callable(cls.__dict__['command_' + command]):
					help(cls.__dict__['command_' + command])
					return
				else:
					help(getattr(self, 'command_' + command))
					return
		return f"No command named '{command}'"

	def command_help(self):
		"""
		Displays this help message.
		Type 'help name' to find out more about the command 'name'.
		If the beginning of a command is unambigous then only the begining is required.

		The following commands are available:

		{}
		"""

		help(self.command_help)

	def command_quit(self):
		"""
		Does what it says on the tin.

		Usage:
		quit
		"""
		self.running = False
		_save_history()
		return "Exiting"

	def command_clear(self):
		"""
		Clears the screen

		Usage:
		clear
		"""
		print(chr(27) + "[2J", end="")

	def _check_ambiguity(self, partial_command):
		partial_command = 'command_' + partial_command
		return [getattr(self, command_name) for cls in type(self).__mro__ for command_name in cls.__dict__ if command_name.startswith(partial_command)]

	def _execute_command(self, command, *args):
		res = command(*args)
		print(res if res is not None else '', end='\n' if res else '')

	def run(self):
		self.running = True
		while self.running:
			try:
				inp = input(self.prompt)
				command, *args = inp.split(' ')
				command = command.lower()
				if inp:
					for cls in type(self).__mro__:
						if 'command_' + command in cls.__dict__:
							command = getattr(self, 'command_' + command)
							self._execute_command(command, *args)
							break
						elif self._check_ambiguity(command):
							posibilities = self._check_ambiguity(command)
							formatted_pos = [f"'{func.__name__}'" for func in posibilities]
							if len(set(formatted_pos)) == 1:
								self._execute_command(posibilities[0], *args)
								break
							else:
								pos_str = ', '.join(formatted_pos[:-1]) + f" or {formatted_pos[-1]}" if len(formatted_pos) > 1 else formatted_pos[0]
								print(f"'{command}' is ambiguous. Did you mean {pos_str}")
								break
					else:
						print(f"No command named '{command}'")
			except (EOFError, KeyboardInterrupt) as e:
				print()
				print(self.command_quit())


