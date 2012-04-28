"""Application base class.
"""

import itertools
import logging
import logging.handlers
import shlex

import cmd2

LOG = logging.getLogger(__name__)


class InteractiveApp(cmd2.Cmd):

    use_rawinput = True
    doc_header = "Shell commands (type help <topic>):"
    app_cmd_header = "Application commands (type help <topic>):"

    def __init__(self, parent_app, command_manager, stdin, stdout):
        self.parent_app = parent_app
        self.command_manager = command_manager
        cmd2.Cmd.__init__(self, 'tab', stdin=stdin, stdout=stdout)

    def default(self, line):
        # Tie in the the default command processor to
        # dispatch commands known to the command manager.
        # We send the message through our parent app,
        # since it already has the logic for executing
        # the subcommand.
        line_parts = shlex.split(line)
        self.parent_app.run_subcommand(line_parts)

    def completedefault(self, text, line, begidx, endidx):
        """Tab-completion for commands known to the command manager.

        Does not handle options on the commands.
        """
        if not text:
            completions = sorted(n for n, v in self.command_manager)
        else:
            completions = sorted(n for n, v in self.command_manager
                                 if n.startswith(text)
                                 )
        return completions

    def help_help(self):
        # Use the command manager to get instructions for "help"
        self.default('help help')

    def do_help(self, arg):
        if arg:
            # Check if the arg is a builtin command or something
            # coming from the command manager
            arg_parts = shlex.split(arg)
            method_name = '_'.join(
                itertools.chain(['do'],
                                itertools.takewhile(lambda x: not x.startswith('-'),
                                                    arg_parts)
                                )
                )
            # Have the command manager version of the help
            # command produce the help text since cmd and
            # cmd2 do not provide help for "help"
            if hasattr(self, method_name):
                return cmd2.Cmd.do_help(self, arg)
            # Dispatch to the underlying help command,
            # which knows how to provide help for extension
            # commands.
            self.default('help ' + arg)
        else:
            cmd2.Cmd.do_help(self, arg)
            cmd_names = [n for n, v in self.command_manager]
            self.print_topics(self.app_cmd_header, cmd_names, 15, 80)
        return

    def get_names(self):
        return [n
                for n in cmd2.Cmd.get_names(self)
                if not n.startswith('do__')
                ]