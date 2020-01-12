#  This file is part of cappuccino.
#
#  cappuccino is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  cappuccino is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with cappuccino.  If not, see <https://www.gnu.org/licenses/>.

import re

from enum import Enum
import irc3

IRC_CODES_REGEX = re.compile(r'\x1f|\x02|\x1D|\x03(?:\d{1,2}(?:,\d{1,2})?)?', re.UNICODE)


class Color(Enum):
    RESET = '\x0f'
    WHITE = '00'
    BLACK = '01'
    BLUE = '02'
    GREEN = '03'
    RED = '04'
    BROWN = '05'
    PURPLE = '06'
    ORANGE = '07'
    YELLOW = '08'
    LIGHT_GREEN = '09'
    TEAL = '10'
    LIGHT_CYAN = '11'
    LIGHT_BLUE = '12'
    PINK = '13'
    GRAY = '14'
    LIGHT_GRAY = '15'


@irc3.plugin
class Formatting(object):

    def __init__(self, bot):
        self.bot = bot
        self.bot.color = Color

    @irc3.extend
    def format(self, text: str, color: Color = None, bold: bool = False, reset: bool = True) -> str:
        if bold:
            text = f'\x02{text}'
        if color:
            text = f'\x03{color.value}{text}'
        if reset:
            text += self.bot.color.RESET.value
        return text

    @irc3.extend
    def strip_formatting(self, string: str) -> str:
        return IRC_CODES_REGEX.sub('', string)
