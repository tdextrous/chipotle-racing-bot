import time

import cv2
import mss
import numpy as np
from pynput.keyboard import Key, Controller


def get_columns(img):
    """
    Get the columns images of the racing game. Should return length 3 tuple
    """
    col0 = img[0:-1, 10:180]
    col1 = img[0:-1, 210:375]
    col2 = img[0:-1, 395:-1]
    return (col0, col1, col2)


def is_column_good(col):
    """
    Check if a column contains the colors of the bonus
    sprites.
    """
    # lower, upper, BGR color boundaries
    # black - #1d1c19
    # guac green - #9e951b
    # chip brown - #986347
    boundaries = [
        ([0x18, 0x1b, 0x1c], [0x1a, 0x1d, 0x1e]),  # black
        ([0x1a, 0x94, 0x9d], [0x1c, 0x96, 0x9f]),  # green
        ([0x46, 0x62, 0x97], [0x48, 0x64, 0x99])   # brown
    ]
    is_column_good = False
    for (lower, upper) in boundaries:
        lower = np.array(lower, dtype="uint8")
        upper = np.array(upper, dtype="uint8")
        mask = cv2.inRange(col, lower, upper)
        if 255 in mask:
            is_column_good = True
            return is_column_good
    return is_column_good


def is_column_bad(col):
    """
    Check if a column contains the colors of the hazardous
    chemical sprites.
    """
    # lower, upper, BGR color boundaries
    # cyan - #97e0e8
    boundaries = [
        ([0xe7, 0xdf, 0x96], [0xe9, 0xe1, 0x98]),  # blue
        ([0xa9, 0xf0, 0xeb], [0xab, 0xf2, 0xed]),  # tan
        ([0x41, 0xd6, 0x4d], [0x43, 0xd8, 0x4f])   # green
    ]

    is_column_bad = False
    for (lower, upper) in boundaries:
        lower = np.array(lower, dtype="uint8")
        upper = np.array(upper, dtype="uint8")
        mask = cv2.inRange(col, lower, upper)
        if 255 in mask:
            is_column_bad = True
            return is_column_bad
    return is_column_bad


class Bot():
    def __init__(self):
        self.curr_column = None
        self.last_move = time.time()
        self.keyboard = Controller()
        self.MOVE_COOLDOWN = 0.5

    def start(self):
        """
        Start the racing bot.
        """
        # Game frame for 1920x1080 res monitor.
        # Different monitor resolutions will need to adjust this.
        mon = {"top": 135, "left": 675, "width": 580, "height": 775}

        title = "chipotle game"
        sct = mss.mss()

        # Initial Game settings.
        self.curr_column = 1  # columns are 0, 1, 2.

        # Game loop
        while True:
            img_bgra = np.asarray(sct.grab(mon))
            img = cv2.cvtColor(img_bgra, cv2.COLOR_BGRA2BGR)
            self.play_game_per_frame(img)

            cv2.imshow(title, img)
            # Press 'q' to quit.
            if cv2.waitKey(25) & 0xFF == ord("q"):
                cv2.destroyAllWindows()
                break

    def play_game_per_frame(self, img):
        """
        Take game img frame as input, then perform all game actions.
        """
        all_cols = get_columns(img)
        curr_column = self.curr_column
        is_curr_column_bad = is_column_bad(all_cols[curr_column])
        # Have a cool down period to avoid glitchy fast moves.
        if (time.time() - self.last_move > self.MOVE_COOLDOWN):
            # Check if current col contains bad sprite.
            if is_curr_column_bad:
                # Switch columns.
                if curr_column == 0:
                    # Go to right immediately.
                    self.press_right_arrow()
                elif curr_column == 2:
                    # Go left immediately.
                    self.press_left_arrow()
                elif curr_column == 1:
                    # Check other columns
                    is_col0_bad = is_column_bad(all_cols[0])
                    if is_col0_bad:
                        # go right
                        self.press_right_arrow()
                    else:
                        # go left
                        self.press_left_arrow()
            else:
                # If current col is not bad, try to switch to a good col.
                if curr_column == 0:
                    # Check mid col for bonus
                    is_col1_good = is_column_good(all_cols[1])
                    if is_col1_good:
                        self.press_right_arrow()

                elif curr_column == 2:
                    # Check mid col for bonus
                    is_col1_good = is_column_good(all_cols[1])
                    if is_col1_good:
                        self.press_left_arrow()

                elif curr_column == 1:
                    # Check both cols for good stuff, do left one first.
                    # Check left.
                    is_col0_good = is_column_good(all_cols[0])
                    if is_col0_good:
                        self.press_left_arrow()
                    # Check right.
                    is_col2_good = is_column_good(all_cols[2])
                    if is_col2_good:
                        self.press_right_arrow()

    def press_left_arrow(self):
        """
        Simulate left arrow key press

        Update column state and last move time.
        """
        self.keyboard.press(Key.left)
        self.curr_column = self.curr_column - 1
        self.last_move = time.time()
        print('col:', self.curr_column)  # output current col state.


    def press_right_arrow(self):
        """
        Simulate right arrow key press.

        Update column state and last move time.
        """
        self.keyboard.press(Key.right)
        self.curr_column = self.curr_column + 1
        self.last_move = time.time()
        print('col:', self.curr_column)  # output current col state.


if __name__ == '__main__':
    bot = Bot()
    bot.start()
