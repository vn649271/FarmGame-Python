"""
CSSE1001 Assignment 3
Semester 1, 2023
"""
__author__ = "Orhan Ors"
__email__ = "o.ors@uq.net.au"
__date__ = "25/05/2023"

import tkinter as tk
from tkinter import filedialog 
from typing import Callable, Union, Optional
from a3_support import *
from model import *
from constants import *


class InfoBar(AbstractGrid):
    """ A view class
    Displays information to the user about the number of days elapsed in
    the game, as well as the player’s energy and money
    """
    def __init__(self, master: tk.Tk | tk.Frame) -> None:

        super().__init__(master, (2, 3), (FARM_WIDTH+INVENTORY_WIDTH,
                                          INFO_BAR_HEIGHT))

        self.set_dimensions((2, 3))
        self.pack(side=tk.BOTTOM)

    def redraw(self, day: int, money: int, energy: int) -> None:
        self.clear()
        
        # Layout of infobar status text
        infobar_status = ['Day:', 'Money:', 'Energy:']
        for text in range(len(infobar_status)):
            position = self.get_midpoint((0, text))
            self.create_text(position[0], position[1],
                             text=infobar_status[text],
                             font=HEADING_FONT)
        self.pack(side=tk.BOTTOM)
        
        # Layout of infobar status variables
        status_amounts = [day, '${}'.format(money), energy]
        for amounts in range(len(status_amounts)):
            position = self.get_midpoint((1, amounts))
            self.create_text(position[0], position[1],
                             text=status_amounts[amounts])
        self.pack(side=tk.BOTTOM, fill= tk.BOTH, expand=True)


class FarmView(AbstractGrid):
    """ A view class
        Displays a grid containing the farm map, player, and plants
    """
    def __init__(self, master: tk.Tk | tk.Frame, dimensions: tuple[int, int],
                 size: tuple[int, int], **kwargs) -> None:

        super().__init__(master, dimensions, size, **kwargs)

        self._size = size
        self.set_dimensions(dimensions)
        self.cache = {}
        self.pack(side=tk.LEFT)

    def redraw(self, ground: list[str], plants: dict[tuple[int, int], 'Plant'],
               player_position: tuple[int, int], player_direction: str) -> None:

        # Prevent duplicating visuals
        self.clear()

        # Generate the map
        image_size = self.get_cell_size()
        for row in range(len(ground)):
            for col in range(len(ground[row])):
                # Select tile 
                floor = ground[row][col]
                image_name = IMAGES[floor]
                image_path = 'images/{}'.format(image_name)
                tile = get_image(image_path, image_size, self.cache)
                self.cache[image_name] = tile  
                # Place tile
                tile_position = self.get_midpoint((row, col))
                self.create_image(tile_position[0], tile_position[1],
                                  image=tile)
                # Place plants on map
                for plant in plants.keys():
                    if row == plant[0] and col == plant[1]:
                        plant_type = plants[plant]
                        plant_name = get_plant_image_name(plant_type)
                        image_location = f"images/{plant_name}"
                        plant_image = get_image(image_location,
                                                image_size, self.cache)
                        self.cache[image_location] = plant_image 

                        plant_position = self.get_midpoint(plant)
                        self.create_image(plant_position[0], plant_position[1],
                                          image=plant_image)
                # Place player on map
                if row == player_position[0] and col == player_position[1]:
                    image_location = 'images/{}'.format(IMAGES[player_direction])
                    player_image = get_image(image_location, image_size,
                                           self.cache)

                    position = self.get_midpoint(player_position)
                    self.create_image(position[0], position[1],
                                      image=player_image)


class ItemView(tk.Frame):
    """ A view class
        Displays the relevant information and buttons for each of the 6 items
        available in the game
    """
    def __init__(self, master: tk.Frame, item_name: str, amount: int,
                 select_command: Optional[Callable[[str], None]] = None,
                 sell_command: Optional[Callable[[str], None]] = None,
                 buy_command: Optional[Callable[[str], None]] = None) -> None:

        super().__init__(master)

        self._item_name = item_name
        
        try:
            self._buy_price = BUY_PRICES[item_name]
        except KeyError:
            self._buy_price = 'N/A'
            
        if item_name in SELL_PRICES:
            self._sell_price = SELL_PRICES[item_name]
        else:
            self._sell_price = 'N/A'
        item = item_name
        # Set background colour based on available stock
        if amount > 0:
            self.config(bg=INVENTORY_COLOUR, padx=10)
        else:
            self.config(bg=INVENTORY_EMPTY_COLOUR, padx=10)
        # ItemView layout
        if item_name in SEEDS: # start with seeds
            # display relevant item text
            self._item_name_label = tk.Label(self, padx=10, pady=20, text='{}: {}\n Sell price: ${}\n Buy price: ${}'.format(item_name, amount, SELL_PRICES[item_name], BUY_PRICES[item_name]), borderwidth=0, highlightthickness=0)
            self._item_name_label.pack(side=tk.LEFT)
            # create buy button
            self._buy_btn = tk.Button(self, text="Buy", padx=10)
            self._buy_btn.pack(side=tk.LEFT)
            # create sell button
            self._sell_btn = tk.Button(self, text="Sell", padx=10)
            self._sell_btn.pack(side=tk.LEFT)
            # bind mouse click for buying and selling
            self._item_name_label.bind('<Button-1>', lambda event, item=self._item_name: select_command(item))
            self._sell_btn.bind('<Button-1>', lambda event, item=self._item_name: sell_command(item))
            self._buy_btn.bind('<Button-1>', lambda event, item=self._item_name: buy_command(item))
            self._item_name_label.pack()
        else: # then all non-seeds
            self._item_name_label = tk.Label(self, padx=34, pady=18, text='{}: {}\n Sell price: ${}\n Buy price: $N/A'.format(item_name, amount, SELL_PRICES[item_name]), borderwidth=0, highlightthickness=0)
            self._item_name_label.pack(side=tk.LEFT)
            # create sell button
            self._sell_btn = tk.Button(self, text="Sell", padx=5)
            self._sell_btn.pack(side=tk.RIGHT)
            # bind mouse click for selling
            self._item_name_label.bind('<Button-1>', lambda event, item=item: select_command(item))
            self._sell_btn.bind('<Button-1>', lambda event, item=item: sell_command(item))


    def update(self, amount: int, selected: bool = False) -> None:
        amount_update = amount

        if self._item_name in SEEDS and self._item_name in ITEMS:
            if amount_update > 0:
                if selected:
                    self.config(bg=INVENTORY_SELECTED_COLOUR)
                    self._item_name_label.config(
                        bg=INVENTORY_SELECTED_COLOUR,
                        text='{}: {}\n Sell price: ${}\n Buy price: ${}'.format(
                            self._item_name, amount_update, self._sell_price, self._buy_price if self._buy_price != 'N/A' else 'N/A'
                        ),
                    )
                else:
                    self.config(bg=INVENTORY_COLOUR)
                    self._item_name_label.config(
                        bg=INVENTORY_COLOUR,
                        text='{}: {}\n Sell price: ${}\n Buy price: ${}'.format(
                            self._item_name, amount_update, self._sell_price, self._buy_price
                        ),
                    )
            else:
                self.config(bg=INVENTORY_EMPTY_COLOUR)
                self._item_name_label.config(
                    bg=INVENTORY_EMPTY_COLOUR,
                    text='{}: {}\n Sell price: ${}\n Buy price: ${}'.format(
                        self._item_name, amount_update, self._sell_price, self._buy_price
                    ),
                )
        elif self._item_name not in SEEDS and self._item_name in ITEMS:
            if amount_update > 0:
                if selected:
                    self.config(bg=INVENTORY_SELECTED_COLOUR)
                    self._item_name_label.config(
                        bg=INVENTORY_SELECTED_COLOUR,
                        text='{}: {}\n Sell price: ${}\n Buy price: $N/A'.format(
                            self._item_name, amount_update, self._sell_price
                        ),
                    )
                else:
                    self.config(bg=INVENTORY_COLOUR)
                    self._item_name_label.config(
                        bg=INVENTORY_COLOUR,
                        text='{}: {}\n Sell price: ${}\n Buy price: $N/A'.format(
                            self._item_name, amount_update, self._sell_price
                        ),
                    )
            else:
                self.config(bg=INVENTORY_EMPTY_COLOUR)
                self._item_name_label.config(
                    bg=INVENTORY_EMPTY_COLOUR,
                    text='{}: {}\n Sell price: ${}\n Buy price: $N/A'.format(
                        self._item_name, amount_update, self._sell_price
                    ),
                )



class FarmGame:
    """ The controller class for the overall game.
        responsible for creating and maintaining instances of the model
        and view classes, event handling, and facilitating communication
        between the model and view classes
    """
    def __init__(self, master: tk.Tk, map_file: str) -> None:
        # Set the title of the window
        master.title("Farm Game")
        self._cache = {}
        # Create the title banner
        banner = get_image('images/header.png', (FARM_WIDTH+INVENTORY_WIDTH,
                                                 BANNER_HEIGHT), self._cache)
        label = tk.Label(master, image=banner, borderwidth=1, highlightthickness=1)
        label.pack()
        # Create the FarmModel instance
        self._model = FarmModel(map_file)
        # Command to execute next day
        def next_day():
            self._model.new_day()
            self._infobar.redraw(self._model.get_days_elapsed(),
                                 self._model.get_player().get_money(),
                                 self._model.get_player().get_energy())
            self.redraw()
        
        # "Next day" button
        tk.Button(master, text="Next day", command=next_day).pack(side=tk.BOTTOM)
        # Create InfoBar instance
        self._infobar = InfoBar(master)
        # Create FarmView instance
        self._farmview = FarmView(master, self._model.get_dimensions(),
                                  (FARM_WIDTH, FARM_WIDTH))
        self.items_dict = {}
        
        # Create ItemView instance
        item_frame = tk.Frame(master, height=FARM_WIDTH, width=INVENTORY_WIDTH,
                              borderwidth=0, highlightthickness=0)
        inventory = self._model.get_player().get_inventory()
        
        for item_name in ITEMS:
            item_qty = 0
            if item_name in inventory:
                item_qty = inventory[item_name]
            if item_name in SEEDS:
                item_view = ItemView(item_frame, item_name, item_qty,
                                     self.select_item, self.sell_item, self.buy_item)
            else:
                item_view = ItemView(item_frame, item_name, item_qty,
                                     self.select_item, self.sell_item)
            
            item_view.pack(side=tk.TOP)
            self.items_dict[item_name] = item_view
        
        item_frame.pack()
        self.redraw()
        
        master.bind('<KeyPress>', self.handle_keypress)
        master.mainloop()


    def redraw(self) -> None:
        # Redraw each view class
        # Redraw FarmView
        ground = self._model.get_map()
        plants = self._model.get_plants()
        position = self._model.get_player().get_position()
        direction = self._model.get_player().get_direction()
        self._farmview.redraw(ground, plants, position, direction)

        # Redraw InfoBar
        day = self._model.get_days_elapsed()
        money = self._model.get_player().get_money()
        energy = self._model.get_player().get_energy()
        self._infobar.redraw(day, int(money), energy)

        # Redraw ItemView
        frames = self.items_dict
        player_inventory = self._model.get_player().get_inventory()
        player_selected_item = self._model.get_player().get_selected_item()
        for item in ITEMS:
            item_frame = frames[item]
            # Player has item in inventory
            try:
                item_amount = player_inventory[item]
                if item == player_selected_item:
                    item_frame.update(item_amount, True)
                else:
                    item_frame.update(item_amount, False)
            # Player does not have item in inventory
            except KeyError:
                item_amount = 0
                item_frame.update(item_amount, False)

        # Update selected item in ItemView
        selected_frame = frames.get(player_selected_item)
        if selected_frame:
            selected_frame.update(player_inventory.get(player_selected_item, 0), True)


    def handle_keypress(self, event: tk.Event) -> None:
        keypress = event.keysym.lower()
        keycharsym = event.keysym
        keypress = keypress.lower()
        player = self._model.get_player()
        player_position = self._model.get_player().get_position()
        player_selected_item = self._model.get_player().get_selected_item()
        player_inventory = self._model.get_player().get_inventory()

        valid_player_directions = 'wasd'
        if keypress in valid_player_directions and keycharsym in valid_player_directions:
            self._model.move_player(keypress)
            self.redraw()
        # Till soil
        elif (keypress == "t") and (keycharsym == "t"):  
            self._model.till_soil(player_position)
            self.redraw()
        # Until soil
        elif (keypress == "u") and (keycharsym == "u"):  
            self._model.untill_soil(player_position)
            self.redraw()
        # Plant seed
        elif keypress == "p":  
            map = self._model.get_map()
            row, col = player_position
            if (map[row][col] == SOIL) and (player_selected_item in player_inventory):
                if player_selected_item == 'Potato Seed':
                    self._model.add_plant(player_position, PotatoPlant())
                elif player_selected_item == 'Kale Seed':
                    self._model.add_plant(player_position, KalePlant())
                elif player_selected_item == 'Berry Seed':
                    self._model.add_plant(player_position, BerryPlant())
                else:
                    return

                frames = self.items_dict
                item_frame = frames[player_selected_item]
                item_frame.update(player_inventory.get(player_selected_item, 0), True)
                self._model.get_player().remove_item((player_selected_item, 1))
                self.redraw()

            else:
                return
        # Pick produce
        elif keypress == "h":  
            harvest_result = self._model.harvest_plant(player_position)
            if harvest_result is None:
                return

            frames = self.items_dict
            item_frame = frames[harvest_result[0]]
            self._model.get_player().add_item(harvest_result)
            item_frame.update(self._model.get_player().get_inventory()[harvest_result[0]], False)
            self.redraw()
            pass
        # Remove plant
        elif keypress == "r":  
            self._model.remove_plant(player_position)
            self.redraw()
        elif keypress == '':
            pass
        else:
            pass

    def select_item(self, item_name: str) -> None:
        for item in ITEMS:
            if item_name == item:
                self._model.get_player().select_item(item_name)
        self.redraw()


    def buy_item(self, item_name: str) -> None:
        player_money = self._model.get_player().get_money()
        price_of_item_to_buy = BUY_PRICES[item_name]

        if player_money >= price_of_item_to_buy:
            self._model.get_player().buy(item_name, price_of_item_to_buy)

            if item_name in self._model.get_player().get_inventory():
                frames = self.items_dict
                item_frame = frames[item_name]
                item_frame.update(self._model.get_player().get_inventory()[item_name], False)
            self.redraw()
        else:
            return


    def sell_item(self, item_name: str) -> None:
        price_of_item_to_sell = SELL_PRICES[item_name]
        self._model.get_player().sell(item_name, price_of_item_to_sell)
        self._infobar.redraw(self._model.get_days_elapsed(),
                             self._model.get_player().get_money(),
                             self._model.get_player().get_energy())  # Update money in InfoBar
        if item_name in self._model.get_player().get_inventory():
            frames = self.items_dict
            item_frame = frames[item_name]
            item_frame.update(self._model.get_player().get_inventory()[item_name], False)
        self.redraw()



def play_game(root: tk.Tk, map_file: str) -> None:
    
    game = FarmGame(root, map_file)
    root.mainloop()

def main() -> None:
    
    root = tk.Tk()
    map_file = filedialog.askopenfilename()
    play_game(root, map_file)

if __name__ == '__main__':
    main()
