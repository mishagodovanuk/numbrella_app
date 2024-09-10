import toga
from toga.style import Pack
from toga.style.pack import COLUMN, ROW
import time
import threading

class TestGame(toga.App):
    def startup(self):
        # Initialize state
        self.selected_button = None
        self.buttons = []  # Store buttons to manage their state
        self.score = 0
        self.timer_running = False
        self.time_elapsed = 0
        self.timer_label = toga.Label("Time: 0s", style=Pack(padding=5))
        self.score_label = toga.Label(f"Score: {self.score}", style=Pack(padding=5))
        self.timer_thread = threading.Thread(target=self.start_timer)

        # Main layout
        main_box = toga.Box(style=Pack(direction=COLUMN, padding=10))
        
        # Add the score and timer at the top
        status_box = toga.Box(style=Pack(direction=ROW, alignment="center"))
        status_box.add(self.timer_label)
        status_box.add(self.score_label)
        main_box.add(status_box)

        # Create game grid
        self.create_grid(main_box)

        # Show the window
        self.main_window = toga.MainWindow(title=self.formal_name)
        self.main_window.content = main_box
        self.main_window.show()

        # Start timer when game starts
        self.start_game()

    def create_grid(self, main_box):
        """Creates the grid of buttons."""
        numbers = [i for i in range(1, 100) if '0' not in str(i)]
        row_box = toga.Box(style=Pack(direction=ROW))
        buttons_in_row = 0

        for number in numbers:
            # Split digits if the number is greater than 9
            for digit in str(number):
                button = toga.Button(
                    digit, 
                    on_press=self.select_button, 
                    style=Pack(flex=1, background_color='lightgrey', padding=5)
                )
                button.value = digit
                button.checked = False
                row_box.add(button)
                self.buttons.append(button)  # Store button in the list
                buttons_in_row += 1

                # After 9 buttons, start a new row
                if buttons_in_row == 9:
                    main_box.add(row_box)
                    row_box = toga.Box(style=Pack(direction=ROW))
                    buttons_in_row = 0

        # Add any remaining buttons to the main box
        if buttons_in_row > 0:
            main_box.add(row_box)

    def select_button(self, widget):
        """Handle button selection logic."""
        if self.selected_button is None:
            # First button click
            self.selected_button = widget
            widget.style.background_color = 'darkorange'  # Mark selected button
            widget.enabled = False  # Make it unclickable
        else:
            # Second button click, check if valid
            if self.is_valid_selection(self.selected_button, widget):
                widget.style.background_color = 'darkred'
                widget.style.color = 'black'  # Mark checked button text as dark
                widget.enabled = False
                widget.checked = True
                self.selected_button.style.background_color = 'darkred'
                self.selected_button.style.color = 'black'
                self.selected_button.checked = True
                self.update_score()  # Update score when buttons are matched
                self.check_victory()  # Check if victory is achieved
            else:
                # Reset if not a valid selection
                self.reset_button(self.selected_button)
            self.selected_button = None  # Reset for the next selection

    def reset_button(self, button):
        """Reset the button to default state."""
        button.style.background_color = 'lightgrey'
        button.enabled = True  # Make it clickable again

    def is_valid_selection(self, button1, button2):
        """Check if the selection is valid based on adjacency and other rules."""
        if button1.value != button2.value:
            return False  # Values are different

        index1 = self.buttons.index(button1)
        index2 = self.buttons.index(button2)

        # Check if the buttons are adjacent either horizontally or vertically
        if abs(index1 - index2) == 1:  # Horizontal neighbor
            if index1 // 9 == index2 // 9:  # Ensure they are in the same row
                return True
        elif abs(index1 - index2) % 9 == 0:  # Vertical neighbor
            # Check if all buttons between them in the column are checked
            step = 9 if index2 > index1 else -9
            for i in range(index1 + step, index2, step):
                if not self.buttons[i].checked:
                    return False
            return True

        # Check if all buttons between are marked as checked (for horizontal)
        if index1 < index2:
            buttons_in_between = self.buttons[index1 + 1:index2]
        else:
            buttons_in_between = self.buttons[index2 + 1:index1]

        if all(button.checked for button in buttons_in_between):
            return True

        return False

    def update_score(self):
        """Update score when buttons are matched."""
        self.score += 10
        self.score_label.text = f"Score: {self.score}"

    def check_victory(self):
        """Check if the player has won by leaving only digits 1 to 9."""
        remaining_values = {button.value for button in self.buttons if not button.checked}
        if remaining_values == {'1', '2', '3', '4', '5', '6', '7', '8', '9'}:
            self.victory()

    def victory(self):
        """Show victory message and propose a new game."""
        self.timer_running = False  # Stop the timer
        self.main_window.info_dialog("Congratulations!", f"You won in {self.time_elapsed}s with a score of {self.score}!")
        self.restart_game()

    def restart_game(self):
        """Restart the game."""
        if self.main_window.question_dialog("New Game", "Do you want to start a new game?"):
            self.main_window.content = toga.Box(style=Pack(direction=COLUMN, padding=10))
            self.score = 0
            self.time_elapsed = 0
            self.start_game()

    def start_game(self):
        """Start the game and reset score and timer."""
        self.timer_label.text = "Time: 0s"
        self.score_label.text = f"Score: {self.score}"
        self.timer_running = True
        if not self.timer_thread.is_alive():
            self.timer_thread = threading.Thread(target=self.start_timer)
            self.timer_thread.start()

    def start_timer(self):
        """Start the game timer."""
        while self.timer_running:
            time.sleep(1)
            self.time_elapsed += 1
            self.timer_label.text = f"Time: {self.time_elapsed}s"


def main():
    return TestGame()

