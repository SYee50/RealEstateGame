"""
Test module for RealEstateGame
"""

import unittest
from RealEstateGame import RealEstateGame

class TestRealEstateGame(unittest.TestCase):
    """ Represents tests for basic functionality of RealEstateGame module. """

    def setUp(self) -> None:
        """ Create game spaces and players. """
        self.game = RealEstateGame()

        self.rent_list = [10, 10, 10, 20, 20, 20, 30, 30, 30, 40, 40, 40,
                          50, 50, 50, 60, 60, 60, 70, 70, 70, 80, 80, 80]
        self.game.create_spaces(200, self.rent_list)

        self.player_name = ["Sandra", "Eric", "Patty", "Leo"]
        for name in self.player_name:
            self.game.create_player(name, 1000)

    def test_initial_player_account_balance(self):
        for name in self.player_name:
            result = self.game.get_player_account_balance(name)
            self.assertEqual(1000, result)

    def test_initial_current_position(self):
        for name in self.player_name:
            result = self.game.get_player_current_position(name)
            self.assertEqual(0, result)

    def test_buy_space_on_GO_not_allowed(self):
        for name in self.player_name:
            # buy_space() returns False for GO
            self.assertFalse(self.game.buy_space(name))

            # Player's don't own any spaces
            self.assertEqual(0, len(self.game._players_in_game[name].get_spaces_owned()))

            # Player balance unchanged
            self.assertEqual(1000, self.game.get_player_account_balance(name))

        # GO space owner name is None
        self.assertIsNone(self.game._game_spaces[0].get_owner_name())

    def test_move_one_player(self):
        self.game.move_player("Sandra", 6)
        self.assertEqual(6, self.game.get_player_current_position("Sandra"))
        self.assertEqual(1000, self.game.get_player_account_balance("Sandra"))

    def test_move_one_player_land_on_GO(self):
        # 6: 5, 5: 10, 4: 14, 3: 17, 2: 19, 1: 20, 4: 24, 1:0 -> GO
        num_space_move = [6, 5, 4, 3, 2, 1, 4, 1]
        expected_index = [6, 11, 15, 18, 20, 21, 0, 1]

        for index, num in enumerate(num_space_move):
            self.game.move_player("Sandra", num)
            self.assertEqual(expected_index[index], self.game.get_player_current_position("Sandra"))

    def test_one_player_loop_board_twice(self):
        # First loop
        num_space_move = [6, 5, 4, 3, 2, 1, 4, 1]
        for num in num_space_move:
            self.game.move_player("Sandra", num)
        self.assertEqual(1, self.game.get_player_current_position("Sandra"))

        # Second loop
        num_space_move = [6, 5, 4, 3, 2, 1, 4, 3]
        for num in num_space_move:
            self.game.move_player("Sandra", num)
        self.assertEqual(4, self.game.get_player_current_position("Sandra"))

        # Move beyond 6
        self.game.move_player("Sandra", 6)
        self.assertEqual(10, self.game.get_player_current_position("Sandra"))

    def test_inactive_player_cannot_move(self):
        self.game.move_player("Sandra", 2)
        self.game.buy_space("Sandra")

        self.game._players_in_game["Eric"].set_account_balance(- 990)
        self.assertEqual(10, self.game.get_player_account_balance("Eric"))

        self.game.move_player("Eric", 2)
        self.assertEqual(0, self.game.get_player_account_balance("Eric"))
        self.assertEqual(2, self.game.get_player_current_position("Eric"))
        self.assertFalse(self.game.buy_space("Eric"))
        self.assertIsNone(self.game.move_player("Eric", 1))
        self.game.move_player("Eric", 5)
        self.assertEqual(2, self.game.get_player_current_position("Eric"))

        # 1000 - 50 (purchase price) + 10 (rent paid)
        self.assertEqual(960, self.game.get_player_account_balance("Sandra"))

    def test_player_buy_space(self):
        self.game.move_player("Sandra", 6)
        self.assertEqual(6, self.game.get_player_current_position("Sandra"))

        self.game.buy_space("Sandra")
        self.assertEqual(900, self.game.get_player_account_balance("Sandra"))
        self.assertEqual("Sandra", self.game._game_spaces[6].get_owner_name())

    def test_space_cannot_be_bought_by_two_players(self):
        self.game.move_player("Sandra", 1)
        self.game.move_player("Eric", 1)

        self.assertEqual(1, self.game.get_player_current_position("Sandra"))
        self.assertEqual(1, self.game.get_player_current_position("Eric"))


        self.game.buy_space("Sandra")
        self.assertEqual("Sandra", self.game._game_spaces[1].get_owner_name())

        self.game.buy_space("Eric")
        self.assertEqual(950, self.game.get_player_account_balance("Sandra"))
        self.assertEqual(1000, self.game.get_player_account_balance("Eric"))
        self.assertEqual("Sandra", self.game._game_spaces[1].get_owner_name())

    def test_player_cannot_buy_space_account_balance_equal_to_price(self):
        self.game._players_in_game["Eric"].set_account_balance(- 900)
        self.assertEqual(100, self.game.get_player_account_balance("Eric"))

        self.game.move_player("Eric", 4)
        self.assertEqual(4, self.game.get_player_current_position("Eric"))
        self.assertFalse(self.game.buy_space("Eric"))

        # Check owner name not altered
        self.game.buy_space("Eric")
        self.assertIsNone(self.game._game_spaces[4].get_owner_name())

    def test_player_cannot_buy_space_account_balance_less_than_price(self):
        self.game._players_in_game["Eric"].set_account_balance(- 990)
        self.assertEqual(10, self.game.get_player_account_balance("Eric"))

        self.game.move_player("Eric", 4)
        self.assertEqual(4, self.game.get_player_current_position("Eric"))
        self.assertFalse(self.game.buy_space("Eric"))

        # Check owner name not altered
        self.game.buy_space("Eric")
        self.assertIsNone(self.game._game_spaces[4].get_owner_name())

    def test_inactive_player_cannot_buy_space(self):
        self.game.move_player("Eric", 4)
        self.game._players_in_game["Eric"].set_account_balance(- 1000)
        self.assertEqual(0, self.game.get_player_account_balance("Eric"))

        self.assertEqual(4, self.game.get_player_current_position("Eric"))
        self.assertFalse(self.game.buy_space("Eric"))

        # Check owner name not altered
        self.game.buy_space("Eric")
        self.assertIsNone(self.game._game_spaces[4].get_owner_name())

    def test_rent_paid_to_owner(self):
        self.game.move_player("Eric", 4)
        self.game.buy_space("Eric")

        self.game.move_player("Sandra", 4)
        self.assertEqual(980, self.game.get_player_account_balance("Sandra"))
        self.assertEqual(920, self.game.get_player_account_balance("Eric"))

    def test_rent_paid_by_multiple_players(self):
        self.game.move_player("Eric", 4)
        self.game.buy_space("Eric")

        self.game.move_player("Sandra", 4)
        self.assertEqual(980, self.game.get_player_account_balance("Sandra"))
        self.assertEqual(920, self.game.get_player_account_balance("Eric"))

        self.game.move_player("Leo", 4)
        self.assertEqual(980, self.game.get_player_account_balance("Sandra"))
        self.assertEqual(940, self.game.get_player_account_balance("Eric"))

    def test_rent_not_paid_by_owner_landing_on_owned_space(self):
        self.game.move_player("Eric", 4)
        self.game.buy_space("Eric")  # account balance: 1000 - 100 = 900

        self.game.move_player("Eric", 21)
        # account balance: 900 + 200 = 1100
        self.assertEqual(0, self.game.get_player_current_position("Eric"))

        self.game.move_player("Eric", 4)  # no rent paid (own this space)
        self.assertEqual(4, self.game.get_player_current_position("Eric"))
        self.assertEqual(1100, self.game.get_player_account_balance("Eric"))

    def test_player_account_balance_less_than_rent(self):
        self.game._players_in_game["Eric"].set_account_balance(- 990)
        self.assertEqual(10, self.game.get_player_account_balance("Eric"))

        self.game.move_player("Sandra", 4)
        self.game.buy_space("Sandra")
        self.assertEqual(900, self.game.get_player_account_balance("Sandra"))
        rent_amount = self.game._game_spaces[4].get_rent_amount()
        self.assertEqual(20, rent_amount)

        self.game.move_player("Eric", 4)
        self.assertEqual(4, self.game.get_player_current_position("Eric"))
        self.assertEqual(0, self.game.get_player_account_balance("Eric"))
        self.assertEqual(910, self.game.get_player_account_balance("Sandra"))

        # rent amount unaltered after player pays different amount (account balance)
        rent_amount = self.game._game_spaces[4].get_rent_amount()
        self.assertEqual(20, rent_amount)

    def test_no_rent_when_previous_owner_becomes_inactive_player(self):
        self.game._players_in_game["Sandra"].set_account_balance(- 695)
        self.game.move_player("Sandra", 4)  # 100
        self.game.buy_space("Sandra")
        owner_name = self.game._game_spaces[4].get_owner_name()
        self.assertEqual("Sandra", owner_name)

        self.game.move_player("Sandra", 6)  # 200
        self.game.buy_space("Sandra")
        owner_name = self.game._game_spaces[10].get_owner_name()
        self.assertEqual("Sandra", owner_name)

        self.game.move_player("Eric", 5)
        self.game.move_player("Eric", 6)
        self.game.buy_space("Eric")
        self.assertEqual(800, self.game.get_player_account_balance("Eric"))

        self.game.move_player("Sandra", 1)
        self.assertEqual(0, self.game.get_player_account_balance("Sandra"))
        self.assertEqual(805, self.game.get_player_account_balance("Eric"))

        # Player on previously owned space
        self.game.move_player("Leo", 4)
        self.assertEqual(1000, self.game.get_player_account_balance("Leo"))  # No rent paid

        # Inactive player cannot own spaces
        self.assertIsNone(self.game._game_spaces[4].get_owner_name())  # Inactive player cannot own space
        self.assertIsNone(self.game._game_spaces[10].get_owner_name())

        # player can purchase previously owned property
        self.game.buy_space("Leo")
        owner_name = self.game._game_spaces[4].get_owner_name()
        self.assertEqual("Leo", owner_name)
        self.assertEqual(900, self.game.get_player_account_balance("Leo"))

    def test_game_over_one_player_active(self):
        self.game._players_in_game["Sandra"].set_account_balance(- 1000)
        self.game._players_in_game["Eric"].set_account_balance(- 1000)
        self.game._players_in_game["Leo"].set_account_balance(- 1000)
        self.assertEqual("Patty", self.game.check_game_over())

    def test_game_not_over_more_than_one_player_active(self):
        self.game._players_in_game["Sandra"].set_account_balance(- 1000)
        self.game._players_in_game["Eric"].set_account_balance(- 1000)
        self.assertEqual("", self.game.check_game_over())


class TestReadMeSpec(unittest.TestCase):
    """ Represents tests for readme specifications. """

    def setUp(self) -> None:
        self.game = RealEstateGame()

        rent_list = [50, 50, 50, 100, 100, 100, 150, 150, 150, 200, 200, 200,
                     250, 250, 250, 300, 300, 300, 350, 350, 350, 400, 400, 400]
        self.game.create_spaces(100, rent_list)

        self.game.create_player("Sandra", 1000)
        self.game.create_player("Maria", 1000)
        self.game.create_player("Sue", 1000)
        self.game.create_player("Sam", 1000)

    def test_create_spaces_len_is_25(self):
        # 25 spaces created
        self.assertEqual(25, len(self.game._game_spaces))

        # Purchase price is 5 times rent
        for space in self.game._game_spaces[1:]:
            rent_amount = space.get_rent_amount()
            self.assertEqual(rent_amount * 5, space.get_purchase_price())

    def test_create_spaces_GO_space_created(self):
        go_purchase_price = self.game._game_spaces[0].get_purchase_price()
        self.assertEqual(0, go_purchase_price)

        amount_paid_for_go = self.game._game_spaces[0].get_rent_amount()
        self.assertEqual(100, amount_paid_for_go)

        owner_name = self.game._game_spaces[0].get_owner_name()
        self.assertIsNone(owner_name)

    def test_GO_cannot_be_purchased(self):
        for name in self.game._players_in_game:
            self.game.buy_space(name)
            self.assertIsNone(self.game._game_spaces[0].get_owner_name())

    def test_player_initial_account_balance(self):
        for name in self.game._players_in_game:
            self.assertEqual(1000, self.game.get_player_account_balance(name))

    def test_player_initial_position(self):
        for name in self.game._players_in_game:
            self.assertEqual(0, self.game.get_player_current_position(name))

    def test_buy_space_deducts_purchase_price_from_account_balance(self):
        player_move = [1, 2, 3, 4]
        for name, move in zip(self.game._players_in_game, player_move):
            self.game.move_player(name, move)
            self.game.buy_space(name)

        expected_account_bal = [750, 750, 750, 500]
        for name, bal in zip(self.game._players_in_game, expected_account_bal):
            self.assertEqual(bal, self.game.get_player_account_balance(name))

    def test_buy_space_player_set_as_owner(self):
        player_move = [1, 2, 3, 4]
        for name, move in zip(self.game._players_in_game, player_move):
            self.game.move_player(name, move)
            self.game.buy_space(name)
            self.assertEqual(name, self.game._game_spaces[move].get_owner_name())

    def test_buy_space_return_True_for_successful_purchase(self):
        player_move = [1, 2, 3, 4]
        for name, move in zip(self.game._players_in_game, player_move):
            self.game.move_player(name, move)
            self.assertTrue(self.game.buy_space(name))

    def test_buy_space_return_False_for_unsuccessful_purchase(self):
        # Set player account balance to 100
        for player in self.game._players_in_game.values():
            player.set_account_balance(- 900)
            self.assertEqual(100, player.get_account_balance())

        # Attempt to purchase space with a balance below purchase price
        player_move = [1, 2, 3, 4]
        for name, move in zip(self.game._players_in_game, player_move):
            self.game.move_player(name, move)
            self.assertFalse(self.game.buy_space(name))

    def test_buy_space_already_owned_by_player(self):
        # Initial purchase of spaces
        player_move = [1, 2, 3, 4]
        for name, move in zip(self.game._players_in_game, player_move):
            self.game.move_player(name, move)
            self.game.buy_space(name)

        # Reset position of players to GO
        for player in self.game._players_in_game.values():
            player.set_position_index(0)
            self.assertEqual(0, player.get_position_index())

        # Attempt to purchase space owned by self
        player_move = [1, 2, 3, 4]
        for name, move in zip(self.game._players_in_game, player_move):
            self.game.move_player(name, move)
            self.assertFalse(self.game.buy_space(name))

    def test_buy_space_owned_by_another_player(self):
        # Initial purchase of spaces
        player_move = [1, 2, 3, 4]
        for name, move in zip(self.game._players_in_game, player_move):
            self.game.move_player(name, move)
            self.game.buy_space(name)

        # Reset position of players to GO
        for player in self.game._players_in_game.values():
            player.set_position_index(0)
            self.assertEqual(0, player.get_position_index())

        # Attempt to purchase space owned by another player
        new_player_move = [4, 3, 2, 1]
        for name, move in zip(self.game._players_in_game, new_player_move):
            self.game.move_player(name, move)
            self.assertFalse(self.game.buy_space(name))

    def test_move_player_no_move_made_when_balance_0(self):
        # Set player account balance to 0
        for player in self.game._players_in_game.values():
            player.set_account_balance(- 1000)
            self.assertEqual(0, player.get_account_balance())

        # Attempt to move player
        for name in self.game._players_in_game:
            self.assertIsNone(self.game.move_player(name, 1))
            self.assertEqual(0, self.game.get_player_current_position(name))

    def test_move_player_advances_player_to_correct_position_index(self):
        player_move = [1, 2, 3, 4]
        for name, move in zip(self.game._players_in_game, player_move):
            self.game.move_player(name, move)
            self.assertEqual(move, self.game.get_player_current_position(name))

        # Move one player to another position
        self.game.move_player("Sam", 6)
        self.assertEqual(10, self.game.get_player_current_position("Sam"))

    def test_move_player_loop_to_GO_position(self):
        # Set player position to last space on board
        self.game._players_in_game["Sandra"].set_position_index(24)
        self.assertEqual(24, self.game.get_player_current_position("Sandra"))

        # Advance the player to GO position
        self.game.move_player("Sandra", 1)
        self.assertEqual(0, self.game.get_player_current_position("Sandra"))

    def test_move_player_loop_to_pass_GO_position(self):
        # Set player position to last space on board
        for name, player in self.game._players_in_game.items():
            player.set_position_index(24)
            self.assertEqual(24, self.game.get_player_current_position(name))

        # Advance player pass GO
        player_move = [2, 3, 4, 5]
        for name, move in zip(self.game._players_in_game, player_move):
            self.game.move_player(name, move)

        # Validate new position index is correct
        expected_index = [1, 2, 3, 4]
        for name, index in zip(self.game._players_in_game, expected_index):
            self.assertEqual(index, self.game.get_player_current_position(name))

    def test_move_player_GO_money_added_to_balance_when_land_on_GO(self):
        # Set player position to last space on board
        for name, player in self.game._players_in_game.items():
            player.set_position_index(24)
            self.assertEqual(24, self.game.get_player_current_position(name))

        # Advance player to land on GO
        # initial bal = 1000
        # GO amount = 100
        for name in self.game._players_in_game:
            self.game.move_player(name, 1)
            self.assertEqual(1100, self.game.get_player_account_balance(name))

    def test_move_player_GO_money_added_to_balance_when_passing_GO(self):
        # Set player position to last space on board
        for name, player in self.game._players_in_game.items():
            player.set_position_index(24)
            self.assertEqual(24, self.game.get_player_current_position(name))

        # Advance player to pass GO
        # initial bal = 1000
        # GO amount = 100
        player_move = [2, 3, 4, 5]
        for name, move in zip(self.game._players_in_game, player_move):
            self.game.move_player(name, move)
            self.assertEqual(1100, self.game.get_player_account_balance(name))

    def test_move_player_rent_paid_to_owner(self):
        self.game.move_player("Sandra", 1)
        self.game.buy_space("Sandra")
        self.assertEqual(750, self.game.get_player_account_balance("Sandra"))

        player_name = ["Maria", "Sue", "Sam"]
        for name in player_name:
            self.game.move_player(name, 1)
            self.assertEqual(950, self.game.get_player_account_balance(name))

        # Confirm rent paid to owner
        self.assertEqual(900, self.game.get_player_account_balance("Sandra"))

    def test_move_player_rent_not_paid_if_space_owned_by_player(self):
        self.game.move_player("Sandra", 1)
        self.game.buy_space("Sandra")
        self.assertEqual(750, self.game.get_player_account_balance("Sandra"))

        # Reset position index to 0
        self.game._players_in_game["Sandra"].set_position_index(0)
        self.assertEqual(0, self.game._players_in_game["Sandra"].get_position_index())

        # No rent paid
        self.game.move_player("Sandra", 1)
        self.assertEqual(750, self.game.get_player_account_balance("Sandra"))

    def test_move_player_no_rent_paid_if_space_not_owned(self):
        for name in self.game._players_in_game:
            self.game.move_player(name, 2)
            self.assertEqual(1000, self.game.get_player_account_balance(name))

    def test_move_player_rent_paid_changed_to_account_bal_when_bal_lower_than_rent(self):
        self.game.move_player("Sam", 2)
        self.game.buy_space("Sam")

        # Set balance lower than rent amount
        self.game._players_in_game["Sandra"].set_account_balance(-990)
        self.assertEqual(10, self.game.get_player_account_balance("Sandra"))

        # Move player to owned space
        self.game.move_player("Sandra", 2)

        # Check account balance is zero for rent payer
        self.assertEqual(0, self.game.get_player_account_balance("Sandra"))

        # Check account balance of owner increased by 10
        # less than rent amount of 50
        # initial bal is 750
        self.assertEqual(760, self.game.get_player_account_balance("Sam"))

    def test_move_player_spaces_owned_by_inactive_player_removed(self):
        # Player buys spaces 1 - 3
        for move in [1, 1, 1]:
            self.game.move_player("Sandra", move)
            self.game.buy_space("Sandra")

        # Get player balance
        self.assertEqual(250, self.game.get_player_account_balance("Sandra"))
        # Get player position
        self.assertEqual(3, self.game.get_player_current_position("Sandra"))

        # Other player's buy spaces 4 - 6
        player_name = ["Sam", "Maria", "Sue"]
        index = 4
        for name in player_name:
            self.game.move_player(name, index)
            self.game.buy_space(name)
            self.assertEqual(100, self.game._game_spaces[index].get_rent_amount())
            index += 1

        # Move one player across three owned spaces
        # Reduce player balance to zero
        for move in [1, 1, 1]:
            self.game.move_player("Sandra", move)
        self.assertEqual(0, self.game.get_player_account_balance("Sandra"))

        # Check previously owned spaces no longer have owner
        for num in range(1, 4):
            self.assertIsNone(self.game._game_spaces[num].get_owner_name())

        # Check list of spaces owned by inactive player is empty
        self.assertEqual(0, len(self.game._players_in_game["Sandra"]._spaces_owned))

    def test_buy_space_cannot_buy_space_that_is_equal_to_balance(self):
        # Reduce balance
        for move in [1, 1]:
            self.game.move_player("Sandra", move)
            self.game.buy_space("Sandra")

        # Get current balance
        self.assertEqual(500, self.game.get_player_account_balance("Sandra"))
        # Get purchase price of space at index 4
        self.assertEqual(500, self.game._game_spaces[4].get_purchase_price())

        # Get current position
        self.assertEqual(2, self.game.get_player_current_position("Sandra"))

        # Move player
        self.game.move_player("Sandra", 2)

        # Attempt to buy space
        self.assertFalse(self.game.buy_space("Sandra"))

    def test_check_game_over_one_active_player(self):
        # Set 3 players account balance to zero
        player_name = ["Sandra", "Sue", "Sam"]
        for name in player_name:
            self.game._players_in_game[name].set_account_balance(-1000)
            self.assertEqual(0, self.game.get_player_account_balance(name))

        self.assertEqual("Maria", self.game.check_game_over())

    def test_check_game_over_no_inactive_players(self):
        self.assertEqual("", self.game.check_game_over())

    def test_check_game_over_one_inactive_player(self):
        # Set 1 player account balance to zero
        self.game._players_in_game["Sandra"].set_account_balance(-1000)
        self.assertEqual(0, self.game.get_player_account_balance("Sandra"))

        self.assertEqual("", self.game.check_game_over())

    def test_check_game_over_two_inactive_players(self):
        # Set 2 players account balance to zero
        player_name = ["Sandra", "Sue"]
        for name in player_name:
            self.game._players_in_game[name].set_account_balance(-1000)
            self.assertEqual(0, self.game.get_player_account_balance(name))

        self.assertEqual("", self.game.check_game_over())
