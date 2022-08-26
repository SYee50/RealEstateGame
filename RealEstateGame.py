""" Backend of Real Estate Board Game similar to Monopoly. """

class RealEstateGame:
    """ Represents a real estate board game.

    Attributes:
        _players_in_game (dict): dictionary of all players; name: Player object
        _game_spaces (list): list of Space objects; tracks space index
    """

    def __init__(self):
        self._players_in_game = {}
        self._game_spaces = []

    def create_spaces(self, money_amount, rent_amounts_list):
        """ Create spaces for board game.

        Args:
            money_amount (int): amount paid to players when land or pass GO
            rent_amounts_list (list): list of 24 rent amounts
        """
        # Create a space named "GO"
        self._game_spaces.append(Space("GO", money_amount, 0))

        # Create 24 more game spaces
        for index, rent_amount in enumerate(rent_amounts_list, 1):
            self._game_spaces.append(Space(str(index), rent_amount, rent_amount * 5))

    def create_player(self, name, initial_balance):
        """ Create player for game.

        Args:
            name (str): unique player name
            initial_balance (int): account balance at start of game
        """
        self._players_in_game[name] = Player(name, initial_balance)

    def get_player_account_balance(self, name):
        """ Retrieve the player's account balance.

        Args:
            name (str): unique player name
        Returns:
            int: player's current account balance
        """
        return self._players_in_game[name].get_account_balance()

    def get_player_current_position(self, name):
        """ Retrieve the player's current position on the board.

        Args:
            name (str): unique player name
        Returns:
            int: player's current position on the board game
        """
        return self._players_in_game[name].get_position_index()

    def buy_space(self, name):
        """ Purchase space on board with player's account balance.

        Args:
            name (str): unique player name
        Returns:
            True: if player buys space
            False: if player does not buy space
        """
        account_bal = self._players_in_game[name].get_account_balance()
        player_pos_index = self._players_in_game[name].get_position_index()
        owner_name = self._game_spaces[player_pos_index].get_owner_name()
        purchase_price = self._game_spaces[player_pos_index].get_purchase_price()
        space_object = self._game_spaces[player_pos_index]

        if account_bal > purchase_price and owner_name is None and player_pos_index != 0:
            # Deduct purchase price from player's account balance
            self._players_in_game[name].set_account_balance(- purchase_price)
            # Set player as owner of space
            self._game_spaces[player_pos_index].set_owner_name(name)
            # Add to spaces_owned list in class Player
            self._players_in_game[name].set_spaces_owned(space_object)

            return True

        # Conditions for buying space not met
        return False

    def player_move_to_next_position(self, name, num_spaces_to_move):
        """ Helper method for move_player. Calculate the player's next position
        on the board. Move player to next position.

        Args:
            name (str): unique player name
            num_spaces_to_move (int): number of spaces to move player on board
        Returns:
            next_position_index (int): index of player's next position on board
        """
        current_position_index = self._players_in_game[name].get_position_index()
        next_position_index = current_position_index + num_spaces_to_move

        if next_position_index <= 24:
            self._players_in_game[name].set_position_index(next_position_index)
        else:
            # Collect money for landing/passing "GO"
            amount_paid = self._game_spaces[0].get_rent_amount()
            self._players_in_game[name].set_account_balance(amount_paid)

            # Loop player's position back to start of board
            next_position_index -= 25
            self._players_in_game[name].set_position_index(next_position_index)

        return next_position_index

    def pay_rent(self, name, next_position_index):
        """ Helper method for move player. Calculate rent player needs to pay.
        Pay any rent owed.

        Args:
            name (str): unique player name
            next_position_index (int): index of player's next position on board
        """
        owner_name = self._game_spaces[next_position_index].get_owner_name()
        account_balance = self._players_in_game[name].get_account_balance()
        rent_amount = self._game_spaces[next_position_index].get_rent_amount()

        # Pay rent on spaces owned by another player and not GO
        if owner_name is not None and owner_name != name and next_position_index != 0:

            # Change rent amount to account balance when balance lower than rent
            if account_balance < rent_amount:
                rent_amount = account_balance

            # Deduct rent from player's account balance
            self._players_in_game[name].set_account_balance(- rent_amount)
            # Add rent to owner's account balance
            self._players_in_game[owner_name].set_account_balance(rent_amount)

    def remove_inactive_player_space_ownership(self, name):
        """ Helper method for move_player. Set owner name to None for all
        spaces owned by the inactive player.

        Args:
            name (str): unique player name
        """
        # Remove ownership of spaces from inactive player
        if self._players_in_game[name].get_account_balance() == 0:

            # Set owner name to None
            for spaces_owned in self._players_in_game[name].get_spaces_owned():
                spaces_owned.set_owner_name(None)

            # Remove spaces from spaces_owned list in class Player
            self._players_in_game[name].remove_all_spaces_owned()

    def move_player(self, name, num_spaces_to_move):
        """ Move player a specified amount of spaces on board. Pay any rent owed.
        Remove inactive player ownership of spaces.

        Args:
            name (str): unique player name
            num_spaces_to_move (int): number of spaces to move player on board
        """
        # No movement when account balance is zero
        if self._players_in_game[name].get_account_balance() == 0:
            return

        # Move player and get next position index
        next_pos_index = self.player_move_to_next_position(name, num_spaces_to_move)

        # Player pays rent owed
        self.pay_rent(name, next_pos_index)

        # Remove inactive player ownership of spaces
        self.remove_inactive_player_space_ownership(name)

    def check_game_over(self):
        """ Determine if game is over and return name of winner.

        Returns:
            str: name of winner, if game over
            str: empty string, if game not over
        """
        # Create list of active players
        active_players = []
        for name, player_object in self._players_in_game.items():
            if player_object.get_account_balance() > 0:
                active_players.append(name)

        # Game over when there is 1 active player
        if len(active_players) == 1:
            # Return winning player name
            return active_players[0]
        else:
            # Return empty string if game is not over
            return ""


class Player:
    """ Represents a player in the game.

    Attributes:
        _name (str): unique player name
        _account_balance (int): player account balance
        _position_index (int): index of player's position on board
        _spaces_owned (list): list of Space objects owned by player
    """

    def __init__(self, name, account_balance):
        self._name = name
        self._account_balance = account_balance
        self._position_index = 0
        self._spaces_owned = []

    def get_account_balance(self):
        """ Return player account balance.

        Returns:
            int: balance amount in player's account
        """
        return self._account_balance

    def get_position_index(self):
        """ Return player position on board.

        Returns:
            int: integer representation of board position
        """
        return self._position_index

    def get_spaces_owned(self):
        """ Return list of spaces owned by player.

        Returns:
            list: list of spaces owned by player
        """
        return self._spaces_owned

    def set_account_balance(self, amount_changed):
        """ Adjust account balance.

        Args:
            amount_changed (int): amount account balance will be changed
        """
        self._account_balance += amount_changed

    def set_position_index(self, new_position_index):
        """ Set player position index.

        Args:
            new_position_index (int): index of space on board player moving to
        """
        self._position_index = new_position_index

    def set_spaces_owned(self, space):
        """ Add new space purchased by player.

        Args:
            space (Space): Space object of purchased space
        """
        self._spaces_owned.append(space)

    def remove_all_spaces_owned(self):
        """ Remove all previously purchased spaces from list. """
        self._spaces_owned = []


class Space:
    """ Represents space on game board.

    Attributes:
        _name (str): name of space
        _rent_amount (int): rental price for landing on space when owned
        _purchase_price (int): cost to purchase space
        _owner_name (str): name of player who purchased space
    """

    def __init__(self, name, rent_amount, purchase_price):
        self._name = name
        self._rent_amount = rent_amount
        self._purchase_price = purchase_price
        self._owner_name = None

    def get_rent_amount(self):
        """ Return space rent amount.

        Returns:
            int: specified rent for space
        """
        return self._rent_amount

    def get_purchase_price(self):
        """ Return space purchase price.

        Returns:
            int: specified purchase price for space
        """
        return self._purchase_price

    def get_owner_name(self):
        """ Return ownership status of space.

        Returns:
            None: if space unowned
            name (str): name of player who owns space, if owned
        """
        return self._owner_name

    def set_owner_name(self, name):
        """ Set owner_name to name of player who purchased space.

        Args:
            name (str): player name
        """
        self._owner_name = name
