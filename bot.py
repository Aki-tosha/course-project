import private.token
import discord
from google_currency import convert
import random
import asyncio

global player
global ttt_bot
global channel
global play_grid
global play_board
global intents


class Herta(discord.Client):

    # Print in console on finished initialization
    @staticmethod
    async def on_ready():
        print(f'We have logged in as {client.user}')
        print("_" * 20)

    # Prevents bot to reply to itself
    # Also act as a trigger list for commands
    async def on_message(self, message):
        global channel
        channel = client.get_channel(message.channel.id)

        if message.author.id == self.user.id:
            return

        if message.content.startswith('>help'):
            await self.helper(message)

        if message.content.startswith('>curr'):
            await self.curr(message)

        if message.content.startswith('>tictactoe'):
            global play_grid
            play_grid = dict(a1=':blue_square:', a2=':blue_square:', a3=':blue_square:',
                             b1=':blue_square:', b2=':blue_square:', b3=':blue_square:',
                             c1=':blue_square:', c2=':blue_square:', c3=':blue_square:')
            await self.tictactoe_init(message)

    @staticmethod
    async def helper(message):  # returns list of available commands
        embed = discord.Embed(title="Available commands:")
        embed.add_field(name=">curr",
                        value="Convert one currency to other in format (amount, from currency, to currency")
        embed.add_field(name=">tictactoe",
                        value="Allows you to play a match of TicTacToe")
        await message.reply(content=None, embed=embed)

    @staticmethod
    async def curr(message):  # converts AMOUNT of CURRENCY into OTHER CURRENCY using Google service
        amount, from_curr, into_curr = message.content.replace('>curr ', '').split(' ')
        _, _, _, _, _, converted_amount, _, _ = convert(from_curr.lower(), into_curr.lower(), float(amount)).split(' ')
        await message.reply(
            f'''{amount} {from_curr.upper()} equal {converted_amount.replace('"', '').replace(',', '')} {into_curr.upper()}''')

    @staticmethod
    async def tictactoe_init(message):
        view = TTTbuttons1(timeout=5)
        msg = await message.reply('Match of TicTacToe?', view=view)

        view.msg = msg
        await view.wait()
        await view.disable_all_items()

    @staticmethod
    async def tictactoe_symbol_choice():
        player_choice = TTTplayerSymbol(timeout=15)
        msg2 = await channel.send('Choose your symbol:', view=player_choice)

        player_choice.msg2 = msg2
        await player_choice.wait()
        await player_choice.disable_all_items()

    @staticmethod
    def player_symbol_for_board():
        if player == 'x':
            return ':regional_indicator_x:'
        elif player == 'o':
            return ':regional_indicator_o:'

    @staticmethod
    def bot_symbol_for_board():
        if ttt_bot == 'x':
            return ':regional_indicator_x:'
        elif ttt_bot == 'o':
            return ':regional_indicator_o:'

    @staticmethod
    def play_board(play_grid):

        col_1 = ':one:'
        col_2 = ':two:'
        col_3 = ':three:'
        row_a = ':regional_indicator_a:'
        row_b = ':regional_indicator_b:'
        row_c = ':regional_indicator_c:'
        sprtr = ':black_large_square:'
        return f"{sprtr}{sprtr}{col_1}{col_2}{col_3}\n" \
               f"{sprtr}{sprtr}{sprtr}{sprtr}{sprtr}\n" \
               f"{row_a}{sprtr}{play_grid['a1']}{play_grid['a2']}{play_grid['a3']}\n" \
               f"{row_b}{sprtr}{play_grid['b1']}{play_grid['b2']}{play_grid['b3']}\n" \
               f"{row_c}{sprtr}{play_grid['c1']}{play_grid['c2']}{play_grid['c3']}"

    async def ttt_win_cons(self):
        win_cons_list = [[play_grid['a1'], play_grid['a2'], play_grid['a3']],
                         [play_grid['b1'], play_grid['b2'], play_grid['b3']],
                         [play_grid['c1'], play_grid['c2'], play_grid['c3']],
                         [play_grid['a1'], play_grid['b1'], play_grid['c1']],
                         [play_grid['a2'], play_grid['b2'], play_grid['c2']],
                         [play_grid['a3'], play_grid['b3'], play_grid['c3']],
                         [play_grid['a1'], play_grid['b2'], play_grid['c3']],
                         [play_grid['c1'], play_grid['b2'], play_grid['a3']]]
        for win_con in win_cons_list:
            if len(set(win_con)) == 1:
                for game_space in win_con:
                    if game_space == ':blue_square:':
                        pass
                    elif game_space == self.player_symbol_for_board():
                        await channel.send(f"You won")
                        raise Exception("It's like a break - but works in this case for me")
                    elif game_space == self.bot_symbol_for_board():
                        await channel.send(f"You lost")
                        raise Exception("It's like a break - but works in this case for me")

    async def ttt_turns(self, win=None):
        print('TURNS')

        if player == 'x':
            while win is None:
                for turn in range(5):
                    print(turn)

                    position_buttons = TTTPositionalPlayButtons(timeout=300)
                    position_buttons.play_board = game_board

                    free_spaces = []

                    await game_board.edit(content=self.play_board(play_grid), view=position_buttons)
                    await position_buttons.wait()
                    await self.ttt_win_cons()
                    await asyncio.sleep(5)
                    await position_buttons.disable_all_items()

                    for space in play_grid:
                        if play_grid[space] == ':blue_square:':
                            free_spaces.append(space)
                    if len(free_spaces) >= 1:
                        key = random.choice(free_spaces)
                        play_grid[key] = self.bot_symbol_for_board()
                    await game_board.edit(content=self.play_board(play_grid))
                    await self.ttt_win_cons()
                    await position_buttons.enable_all_items()

                    if turn == 4:
                        await channel.send('Draw!')
                        raise Exception("It's like a break - but works in this case for me")

        elif player == 'o':
            for turn in range(5):
                print(turn)

                position_buttons = TTTPositionalPlayButtons(timeout=300)
                position_buttons.play_board = game_board

                free_spaces = []

                for space in play_grid:
                    if play_grid[space] == ':blue_square:':
                        free_spaces.append(space)
                if len(free_spaces) >= 1:
                    key = random.choice(free_spaces)
                    play_grid[key] = self.bot_symbol_for_board()
                await game_board.edit(content=self.play_board(play_grid))
                await self.ttt_win_cons()
                await position_buttons.enable_all_items()

                if len(free_spaces) >= 1:
                    await game_board.edit(content=self.play_board(play_grid), view=position_buttons)
                    await position_buttons.wait()
                    await self.ttt_win_cons()
                    await asyncio.sleep(5)
                    await position_buttons.disable_all_items()

                if turn == 4:
                    await channel.send('Draw!')
                    raise Exception("It's like a break - but works in this case for me")

    async def ttt_start_turns(self):

        global game_board

        play_grid = dict(a1=':blue_square:', a2=':blue_square:', a3=':blue_square:',
                         b1=':blue_square:', b2=':blue_square:', b3=':blue_square:',
                         c1=':blue_square:', c2=':blue_square:', c3=':blue_square:')

        game_board = await channel.send(self.play_board(play_grid))

        await self.ttt_turns()


class TTTbuttons1(discord.ui.View):
    # Class for confirming start of game
    async def disable_all_items(self):
        for item in self.children:
            item.disabled = True
        await self.msg.edit(view=self)

    async def on_timeout(self) -> None:
        await self.msg.channel.send("You're too slow")
        await self.disable_all_items()

    @discord.ui.button(label='Yes',
                       style=discord.ButtonStyle.blurple)
    async def yes(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message('We going in!')
        self.stop()
        await Herta.tictactoe_symbol_choice()

    @discord.ui.button(label='Nope',
                       style=discord.ButtonStyle.blurple)
    async def no(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message('Well, have fun then')
        self.stop()


class TTTplayerSymbol(discord.ui.View):
    #  Class for choosing symbol for TicTacToe

    async def disable_all_items(self):
        for item in self.children:
            item.disabled = True
        await self.msg2.edit(view=self)

    async def on_timeout(self) -> None:
        await self.msg2.channel.send("You're too slow")
        await self.disable_all_items()

    @discord.ui.button(label='X',
                       style=discord.ButtonStyle.blurple)
    async def x_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        global player, ttt_bot
        player = 'x'
        ttt_bot = 'o'
        await interaction.response.send_message('You will be :regional_indicator_x: and going first')
        self.stop()
        await Herta(intents=intents).ttt_start_turns()

    @discord.ui.button(label='O',
                       style=discord.ButtonStyle.blurple)
    async def o_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        global player, ttt_bot
        player = 'o'
        ttt_bot = 'x'
        await interaction.response.send_message('You will be :regional_indicator_o: and going second')
        self.stop()
        await Herta(intents=intents).ttt_start_turns()


class TTTPositionalPlayButtons(discord.ui.View):
    # Class for position buttons which gives values for changing board

    async def disable_all_items(self):
        for item in self.children:
            item.disabled = True
        await self.play_board.edit(view=self)

    async def enable_all_items(self):
        for item in self.children:
            item.disabled = False
        await self.play_board.edit(view=self)

    @discord.ui.button(label='A1', row=0,
                       style=discord.ButtonStyle.blurple)
    async def a1_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        play_grid['a1'] = Herta.player_symbol_for_board()
        await interaction.response.edit_message(content=Herta.play_board(play_grid))
        self.stop()

    @discord.ui.button(label='A2', row=0,
                       style=discord.ButtonStyle.blurple)
    async def a2_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        play_grid['a2'] = Herta.player_symbol_for_board()
        await interaction.response.edit_message(content=Herta.play_board(play_grid))
        self.stop()

    @discord.ui.button(label='A3', row=0,
                       style=discord.ButtonStyle.blurple)
    async def a3_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        play_grid['a3'] = Herta.player_symbol_for_board()
        await interaction.response.edit_message(content=Herta.play_board(play_grid))
        self.stop()

    @discord.ui.button(label='B1', row=1,
                       style=discord.ButtonStyle.blurple)
    async def b1_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        play_grid['b1'] = Herta.player_symbol_for_board()
        await interaction.response.edit_message(content=Herta.play_board(play_grid))
        self.stop()

    @discord.ui.button(label='B2', row=1,
                       style=discord.ButtonStyle.blurple)
    async def b2_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        play_grid['b2'] = Herta.player_symbol_for_board()
        await interaction.response.edit_message(content=Herta.play_board(play_grid))
        self.stop()

    @discord.ui.button(label='B3', row=1,
                       style=discord.ButtonStyle.blurple)
    async def b3_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        play_grid['b3'] = Herta.player_symbol_for_board()
        await interaction.response.edit_message(content=Herta.play_board(play_grid))
        self.stop()

    @discord.ui.button(label='C1', row=2,
                       style=discord.ButtonStyle.blurple)
    async def c1_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        play_grid['c1'] = Herta.player_symbol_for_board()
        await interaction.response.edit_message(content=Herta.play_board(play_grid))
        self.stop()

    @discord.ui.button(label='C2', row=2,
                       style=discord.ButtonStyle.blurple)
    async def c2_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        play_grid['c2'] = Herta.player_symbol_for_board()
        await interaction.response.edit_message(content=Herta.play_board(play_grid))
        self.stop()

    @discord.ui.button(label='C3', row=2,
                       style=discord.ButtonStyle.blurple)
    async def c3_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        play_grid['c3'] = Herta.player_symbol_for_board()
        await interaction.response.edit_message(content=Herta.play_board(play_grid))
        self.stop()


# Discord feature on allowing bots to have access to specific intents
intents = discord.Intents.default()
intents.message_content = True  # THIS DO NOT CHANGE INTENT, BUT CHECKS IF CHOSEN INTENT TURNED ON
client = Herta(intents=intents)

client.run(private.token.token)
