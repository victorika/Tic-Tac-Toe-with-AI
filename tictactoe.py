import random
import sys
from abc import ABC, abstractmethod
from copy import deepcopy


class Board:
    def __init__(self):
        self.game_table = [[' ', ' ', ' '], [' ', ' ', ' '], [' ', ' ', ' ']]

    def print_table(self):
        print('  -------')
        j = 4
        for i in self.game_table:
            j -= 1
            print(str(j) + '| ' + i[0] + ' ' + i[1] + ' ' + i[2] + ' |')
        print('  -------\n   1 2 3  ')

    def result(self):
        # by diogonal
        if self.game_table[0][2] == self.game_table[1][1] == self.game_table[2][0] \
                and self.game_table[0][2] != ' ':
            return self.game_table[1][1] + ' wins'
        elif self.game_table[0][0] == self.game_table[1][1] == self.game_table[2][2] \
                and self.game_table[1][1] != ' ':
            return self.game_table[1][1] + ' wins'
        # by row and column
        for i in range(3):
            if self.game_table[i][0] == self.game_table[i][1] == self.game_table[i][2] \
                    and self.game_table[i][0] != ' ':
                return self.game_table[i][0] + ' wins'
            elif self.game_table[0][i] == self.game_table[1][i] == self.game_table[2][i] \
                    and self.game_table[0][i] != ' ':
                return self.game_table[0][i] + ' wins'
        for j in range(3):
            for i in range(3):
                if ' ' in self.game_table[i][j]:
                    return 'Game not finished'
        return 'Draw'

    def close_to_win(self, symbol):
        # by row and column
        for i in range(3):
            if sum((self.game_table[i][0] == symbol,
                    self.game_table[i][1] == symbol,
                    self.game_table[i][2] == symbol)) == 2 and ' ' in \
                    (self.game_table[i][0],
                     self.game_table[i][1],
                     self.game_table[i][2]):
                column = (self.game_table[i][0], self.game_table[i][1], self.game_table[i][2]).index(' ')
                row = i
                return row, column
            elif sum((self.game_table[0][i] == symbol,
                     self.game_table[1][i] == symbol,
                     self.game_table[2][i] == symbol)) == 2 and ' ' in \
                    (self.game_table[0][i],
                     self.game_table[1][i],
                     self.game_table[2][i]):
                row = (self.game_table[0][i], self.game_table[1][i], self.game_table[2][i]).index(' ')
                column = i
                return row, column
        # by diogonal
        diagonal = [self.game_table[0][0], self.game_table[1][1], self.game_table[2][2]]
        if sum((diagonal[0] == symbol,
                diagonal[1] == symbol,
                diagonal[2] == symbol)) == 2 and ' ' in diagonal:
            column = diagonal.index(' ')
            row = diagonal.index(' ')
            return row, column
        diagonal = [self.game_table[0][2], self.game_table[1][1], self.game_table[2][0]]
        if sum((diagonal[0] == symbol,
                diagonal[1] == symbol,
                diagonal[2] == symbol)) == 2 and ' ' in diagonal:
            row = diagonal.index(' ')
            if row == 0:
                column = 2
            elif row == 1:
                column = 1
            else:
                column = 0
            return row, column
        return None, None

    def empty_indexes(self):
        indices = [[], [], []]
        rows = []
        columns = []
        for row in range(3):
            indices[row] = [i for i, x in enumerate(self.game_table[row]) if x == " "]
        for row in range(3):
            for values in indices[row]:
                rows.append(row)
                columns.append(values)
        return list(zip(rows, columns))


class Player(ABC):
    def __init__(self, symbol) -> None:
        self.symbol = symbol
        if self.symbol == 'X':
            self.other_symbol = 'O'
        else:
            self.other_symbol = 'X'

    @abstractmethod
    def get_move(self, board: Board) -> None:
        ...


class User(Player):
    def get_move(self, board):
        while True:
            coordinates = list(input("Enter next move coordinates: "))
            #diffirent number of imputs
            if len(coordinates) != 3 or coordinates[1] != ' ':
                print('Input two numbers from 1 to 3 devided by space')
                continue
            # not int
            try:
                row = int(coordinates[2])
                column = int(coordinates[0])
            except ValueError:
                print("You should enter numbers")
                continue
            # coordinates from 1 to 3
            if row < 1 or row > 3 or column < 1 or column > 3:
                print("Coordinates should be from 1 to 3")
                continue
            elif board.game_table[3 - row][column - 1] != ' ':
                print('This cell is occupied. Choose another one.')
                continue
            else:
                board.game_table[3 - row][column - 1] = self.symbol
                return board.print_table()


class Easy(Player):
    def get_move(self, board):
        while True:
            row = random.randint(0, 2)
            column = random.randint(0, 2)
            if board.game_table[row][column] == ' ':
                print(f'Making move level "{self.__class__.__name__.lower()}"')
                board.game_table[row][column] = self.symbol
                return board.print_table()


class Medium(Easy):
    def get_move(self, board):
        row, column = board.close_to_win(self.symbol)
        row_other, column_other = board.close_to_win(self.other_symbol)
        if row is not None and column is not None:
            board.game_table[row][column] = self.symbol
            print('Making move level "medium"')
            return board.print_table()
        elif row_other is not None and column_other is not None:
            board.game_table[row_other][column_other] = self.symbol
            print('Making move level "medium"')
            return board.print_table()
        else:
            super().get_move(board)


class Hard(Easy):
    def minimax(self, board, indexes, circle: bool, depth=0, first_index=(-1, -1)):
        # find a result
        result = board.result()
        if result == f'{self.symbol} wins':
            return 1, first_index
        elif result == f'{self.other_symbol} wins':
            return -1, first_index
        elif result == 'Draw':
            return 0, first_index
        else:
            player_symbol = 'O' if circle else 'X'
            if self.symbol == player_symbol:
                # maximum
                maximum = (- 2, (-1, -1))
                for idx, (x, y) in enumerate(indexes):  # zipped indexes [(x,y), (x,y)]
                    # copy board
                    new_board = deepcopy(board)
                    # catch first index
                    if depth == 0:
                        first_index = (x, y)
                    # make move on new board
                    new_board.game_table[x][y] = player_symbol
                    grade = self.minimax(new_board, indexes[:idx]+indexes[idx+1:], not circle, depth+1, first_index)
                    # (0, (0, 1))
                    maximum = max(maximum, grade)
                return maximum
            else:
                minimum = (2, (-1, -1))
                # minimum
                for idx, (x, y) in enumerate(indexes):  # zipped indexes [(x,y), (x,y)]
                    # copy board
                    new_board = deepcopy(board)
                    # catch first index
                    if depth == 0:
                        first_index = (x, y)
                    # make move on new board
                    new_board.game_table[x][y] = player_symbol
                    grade = self.minimax(new_board, indexes[:idx]+indexes[idx+1:], not circle, depth+1, first_index)
                    minimum = min(minimum, grade)
                return minimum

    def get_move(self, board: Board) -> None:
        if self.symbol == 'X':
            self.other_symbol = 'O'
        else:
            self.other_symbol = 'X'

        empty_indexes = board.empty_indexes()
        if len(empty_indexes) > 8:
            super().get_move(board)
        else:
            grade = self.minimax(board, empty_indexes, self.symbol == 'O')
            # print(f'last result = {grade}')
            board.game_table[grade[1][0]][grade[1][1]] = self.symbol
            print('Making move level "hard"')
            return board.print_table()


class PlayerFactory:
    players = {'user': User, 'easy': Easy, 'medium': Medium, 'hard': Hard}

    @staticmethod
    def create_players(ma, mb):
        return PlayerFactory.players[ma]('X'), PlayerFactory.players[mb]('O')


def game():
    print('Welcome to the Tic-Tac-Toe game!\n')
    print('Start the game = (level of a player1) (level of a player2)')
    print('Show levels of a player = levels')
    print('Rules of the game = rules')
    print('Exit the game = exit\n')
    while True:
        command = input('Input command: ').split()
        if len(command) == 1 and command[0] == 'exit':
            sys.exit()
        elif len(command) == 1 and command[0] == 'rules':
            print('\nThis is a 2-player game. The first player plays the X mark, and the second is O')
            print('The player who succeeds in placing three of their marks in a horizontal, vertical, or diagonal row is the winner.')
            board.print_table()
            print('To make a user move choose from board coordinates from 1 to 3. First number horisontal, second is vertical')
            print('Choose levels for your players to start the game.')
        elif len(command) == 1 and command[0] == 'levels':
            print('\nThere are 4 levels of players:')
            print('user - manually put your symbol on the board')
            print('easy - little bot who put their mark randomly')
            print('medium - bot who tries to get a good move')
            print('hard - AI bot using MinMax algorithm')
        elif len(command) == 2:
            if command[0] in PlayerFactory.players and command[1] in PlayerFactory.players:
                player1, player2 = PlayerFactory.create_players(command[0], command[1])
                board = Board()
                board.print_table()
                while True:
                    player1.get_move(board)
                    if board.result() != 'Game not finished':
                        break
                    player2.get_move(board)
                    if board.result() != 'Game not finished':
                        break
                print(board.result())
        else:
            print('Bad parameters')
            print('Start the game = (level of a player1) (level of a player2)')
            print('Show levels of a player = levels')
            print('Rules of the game = rules')
            print('Exit the game = exit\n')


game()