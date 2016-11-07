from subprocess import Popen, PIPE
import irc3


class Editor(object):
    """
    Wrapper to provide ed-style line editing.
    https://gist.github.com/rduplain/3441687
    Ron DuPlain <ron.duplain@gmail.com>
    """

    def __init__(self, command):
        """A wrapper around UNIX sed, for operating on strings with sed expressions.

        Args:
            command: Any valid sed s/ expression.

        Example:
            >>> editor = Editor('s/Hello/Greetings/')
            >>> print(editor.edit('Hello World!'))
            "Greetings World!"
            >>> print(editor.edit('Hello World!', 's/World!/World\./'))
            "Hello World."
            >>> print(editor.edit('Hello, World'))
            "Greetings, World"
        """

        self.command = command

    def _sed_wrapper(self, text, command=None):
        arguments = ['sed', command or self.command]
        sed = Popen(arguments, stdin=PIPE, stdout=PIPE, stderr=PIPE)
        sed.stdin.write(bytes(text.strip(), 'UTF-8'))
        sed.stdin.close()
        returncode = sed.wait()
        if returncode != 0:
            # Unix integer returncode, where 0 is success.
            raise EditorException(sed.stderr.read().decode('UTF-8').strip().replace('sed: -e ', ''))
        return sed.stdout.read().decode('UTF-8').strip()

    def edit(self, text, command=None):
        """Run this Editor's sed command against :text.

        Args:
            text: Text to run sed command against.
            command: An optional command to use for this specific operation.
        Returns:
            Resulting text after sed operation.
        Raises:
            EditorException: Details of sed errors.
        """
        output = self._sed_wrapper(text, command or self.command)
        if not output:
            return text
        # Prevent spam.
        max_len = 512
        if len(output) > max_len:
            return 'Output would be too large. ({0}/{1} characters)'.format(len(output), max_len)
        return output


class EditorException(Exception):
    """An error occurred while processing the editor command."""


@irc3.plugin
class Plugin(object):
    def __init__(self, bot):
        self.bot = bot
        self.history_buffer = {}

    @irc3.event(irc3.rfc.PRIVMSG)
    def chat_history(self, target, event, mask, data):
        if event != 'PRIVMSG' or not target.is_channel or data.startswith('s/'):
            return
        if target in self.history_buffer:
            self.history_buffer.pop(target)
        self.history_buffer.update({target: {mask.nick: data}})

    @irc3.event(r'^(@(?P<tags>\S+) )?:(?P<mask>\S+!\S+@\S+) PRIVMSG '
                r'(?P<target>\S+) :\s*'
                r'(?P<sed>s/.+)')
    def sed(self, mask, target, sed):
        if target in self.history_buffer:
            last_message = self.history_buffer.get(target)
            if not last_message:
                return

            (user, message), = last_message.items()
            editor = Editor(sed)
            try:
                message = editor.edit(message)
            except EditorException as error:
                self.bot.log.error(error)
                self.bot.privmsg(target, '{0}: {1}'.format(mask.nick, error))
            else:
                self.bot.privmsg(target, '<{0}> {1}'.format(user, message))
