# ./app/artist.py
from typing import Optional
from app.show import Show

class Artist:
    def __init__(self, name: str, host_name_and_stage: str, weekend: str, date: str, songs_num: int = 0):
        self.name = name
        self.songs_num = songs_num
        self.show = Show(weekend, host_name_and_stage, date)
        self.show2: Optional[Show] = None

    def add_new_show(self, weekend: str, host_name_and_stage: str, date: str) -> None:
        """
        Add a new show to the object's attribute 'show2'.

        This method creates a new 'Show' object with the provided 'weekend', 'host_name_and_stage',
        and 'date' arguments and assigns it to the 'show2' attribute of the object.

        Args:
            weekend (str): The weekend information for the show.
            host_name_and_stage (str): The name of the host and the stage for the show.
            date (str): The date of the show.
        """
        self.show2 = Show(weekend, host_name_and_stage, date)

    def __str__(self, selected_weekend: str = "") -> str:
        output = f"*{self.name}*- Songs number: {self.songs_num}\n"
        show_string = self.get_show_string(selected_weekend)
        output += show_string
        return output

    def get_show_string(self, selected_weekend: str) -> str:
        """
        Get the string representation of the show(s) based on the selected weekend.

        Args:
            selected_weekend (str): The weekend number to filter the shows.

        Returns:
            str: The string representation of the show(s) for the selected weekend.
        """
        if not selected_weekend:
            show_string = f"Show:\n{self.show}"
            if self.show2:
                show_string += f"\nShow2:\n{self.show2}"
        elif self.show.weekend_number.lower() == selected_weekend.lower():
            show_string = f"Show:\n{self.show}"
        elif self.show2 and self.show2.weekend_number.lower() == selected_weekend.lower():
            show_string = f"Show2:\n{self.show2}"
        else:
            show_string = "No show for the selected weekend."
        return show_string