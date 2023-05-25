import tkinter as tk
from tkinter import filedialog # For masters task
from typing import Callable, Union, Optional
from a3_support import *
from model import *
from constants import *

# Implement your classes here
class InfoBar(AbstractGrid):
    def __init__(self, master: tk.Tk | tk.Frame) -> None:
        """Initializes the InfoBar.

        Parameters:
            master: The master frame for this Canvas.
        """
        counter = 1
        
        super().__init__(master, (2, 3), (FARM_WIDTH+INVENTORY_WIDTH,
                                          INFO_BAR_HEIGHT))
        self._day = None
        self._money = None
        self._energy = None
        self.config(bg="yellow")
        

    def redraw(self, day: int, money: int, energy: int) -> None:
        """Clears the InfoBar and redraws it.

        Parameters:
            day: The current day.
            money: The current amount of money.
            energy: The current amount of energy.
        """
        self.clear()
        
        self._day = day
        self._money = money
        self._energy = energy

        self.annotate_position((0, 0), "Day:")
        self.annotate_position((1, 0), f"{self._day}")
        self.annotate_position((0, 1), "Money: ")
        self.annotate_position((1, 1), f"{self._money}")
        self.annotate_position((0, 2), "Energy: ")
        self.annotate_position((1, 2), f"{self._energy}")


class FarmView(AbstractGrid):
    """A GUI component that displays the farm."""

    def __init__(self, master: tk.Tk | tk.Frame, dimensions: tuple[int, int], 
                 size: tuple[int, int], **kwargs) -> None:
        """Initializes the FarmView.

        Parameters:
            master: The master frame for this Canvas.
            dimensions: The dimensions of the grid as (#rows, #columns)
            size: The size of the grid as (width in pixels, height in pixels)
        """
        super().__init__(master, (10, 10), (FARM_WIDTH, FARM_WIDTH))
        self.config(bg="blue")
        self._image_cache = {}

    def redraw(self, ground: list[str], plants: dict[tuple[int, int], 'Plant'], 
               player_position: tuple[int, int], player_direction: str) -> None:
        """Redraws the FarmView.

        Parameters:
            ground: The list of strings representing the tiles in the map.
            plants: The dictionary mapping (row, col) positions to Plants.
            player_position: The current position of the player as (row, col).
            player_direction: The current direction of the player.
        """
        self.clear()

        cell_width, cell_height = self.get_cell_size()

        for row in range(self._dimensions[0]):
            for col in range(self._dimensions[1]):
                tile = ground[row][col]
                image_name = 'images/' + f'{tile}.png'
                image = get_image(image_name, (cell_width, cell_height), self._image_cache)
                self.create_image(self.get_midpoint((row, col)), image=image)

        for position, plant in plants.items():
            image_name = 'images/' + get_plant_image_name(plant)
            image = get_image(image_name, (cell_width, cell_height), self._image_cache)
            self.create_image(self.get_midpoint(position), image=image)

        player_image_name = 'images/' + f'player_{player_direction}.png'
        player_image = get_image(player_image_name, (cell_width, cell_height), self._image_cache)
        self.create_image(self.get_midpoint(player_position), image=player_image)

class ItemView(tk.Frame):
    """A GUI component that displays the item sections."""

    def __init__(self, master: tk.Frame, select_command: Optional[Callable[[str], None]] = None,
                 sell_command: Optional[Callable[[str], None]] = None,
                 buy_command: Optional[Callable[[str], None]] = None) -> None:
        """Initializes the ItemView.

        Parameters:
            master: The master frame for this Frame.
            select_command: The callback function to call when an item is selected.
            sell_command: The callback function to call when an item is sold.
            buy_command: The callback function to call when an item is bought.
        """
        super().__init__(master)
        self._sections = {}

        # Create the sections for each item
        for item in ITEMS:
            section = tk.Frame(self)
            section.pack(side=tk.TOP, fill=tk.X)
            self._sections[item] = section

        # Configure the section labels and buttons
        for item in ITEMS:
            section = self._sections[item]
            buy_price = BUY_PRICES.get(item)
            sell_price = SELL_PRICES.get(item)

            label_text = f"{item}:"
            label = tk.Label(section, text=label_text)
            label.pack(side=tk.TOP, anchor=tk.W)

            if sell_price is not None:
                sell_price_text = f"Sell Price: ${sell_price}"
                sell_price_label = tk.Label(section, text=sell_price_text)
                sell_price_label.pack(side=tk.TOP, anchor=tk.W)

            if buy_price is not None:
                buy_price_text = f"Buy Price: ${buy_price}"
                buy_price_label = tk.Label(section, text=buy_price_text)
                buy_price_label.pack(side=tk.TOP, anchor=tk.W)

            button_frame = tk.Frame(section)
            button_frame.pack(side=tk.RIGHT)

            if buy_price is not None:
                buy_button = tk.Button(button_frame, text=f"Buy ({buy_price})",
                                       command=lambda item=item: buy_command(item))
                buy_button.pack(side=tk.LEFT)

            if sell_price is not None:
                sell_button = tk.Button(button_frame, text=f"Sell ({sell_price})",
                                        command=lambda item=item: sell_command(item))
                sell_button.pack(side=tk.LEFT)

            if select_command:
                section.bind('<Button-1>', lambda event, item=item: select_command(item))

    def redraw(self, inventory: dict[str, int]) -> None:
        """Updates the display of the item sections.

        Parameters:
            inventory: The dictionary mapping items to their quantities in the player's inventory.
        """
        for item, section in self._sections.items():
            quantity = inventory.get(item, 0)
            label_text = f"{item}: {quantity}"
            section.config(text=label_text)


class FarmGame:
    def __init__(self, master: tk.Tk, map_file: str):
        """Initializes the FarmGame Controller class"""
        self.master = master
        self.master.title('Farm Game')

        # Add banner
        self.banner = get_image('images/header.png', (FARM_WIDTH+INVENTORY_WIDTH, BANNER_HEIGHT)) 
        self.banner_label = tk.Label(master, image=self.banner)
        self.banner_label.grid(row=0, column=0, columnspan=3)

        # Create FarmModel instance
        self.model = FarmModel(map_file)

        # Create View instances
        self.info_bar = InfoBar(master)
        self.info_bar.redraw(1,2,3)
        self.info_bar.grid(row=2, column=0, columnspan=3)
        self.farm_view = FarmView(master, (FARM_WIDTH, 700), (100,100))
        self.farm_view.grid(row=1, column=0)

        
        self.item_view = ItemView(master, self.select_item, self.sell_item, self.buy_item)
        self.item_view.grid(row=1, column=10, columnspan=6)

        # Create 'Next day' button
        self.next_day_button = tk.Button(master, text='Next day', command=self.advance_day)
        self.next_day_button.grid(row=2, column=2)

        # Bind keypress event
        master.bind('<KeyPress>', self.handle_keypress)

        # Draw the initial state of the game
        self.redraw()

    def redraw(self):
        """Redraws the game based on current model state"""
        # Update views
        self.info_bar.redraw(self.model.day, self.model.money, self.model.energy)  # Replace placeholders with actual values
        self.farm_view.redraw(self.model.ground, self.model.plants, self.model.player_position, self.model.player_direction)
        self.item_view.redraw(self.item_name, self.amount)
        # Replace placeholders with actual values
        # Implement similar update methods for other views as needed

    def handle_keypress(self, event: tk.Event):
        """Handle keypress events"""
        key = event.keysym
        if key == 'Left':
            # Implement logic for handling left key press
            pass
        elif key == 'Right':
            # Implement logic for handling right key press
            pass
        # Implement similar conditionals for other key press events
        self.redraw()

    def select_item(self, item_name: str):
        """Handle item selection"""
        # Update the model with the selected item
        self.model.select_item(item_name)
        self.redraw()

    def buy_item(self, item_name: str):
        """Handle buying items"""
        # Update the model with the purchased item
        self.model.buy_item(item_name, BUY_PRICES[item_name])  
        self.redraw()

    def sell_item(self, item_name: str):
        """Handle selling items"""
        # Update the model with the sold item
        self.model.sell_item(item_name, SELL_PRICES[item_name])  
        self.redraw()

    def advance_day(self):
        """Advance the game to the next day"""
        # Implement the logic for advancing to the next day in the model
        self.model.new_day
        self.redraw()


def play_game(root: tk.Tk, map_file: str) -> None:
    
    game = FarmGame(root, map_file)
    root.mainloop()

def main() -> None:
    
    root = tk.Tk()
    map_file = 'maps/map1.txt'
    play_game(root, map_file)

if __name__ == '__main__':
    main()
