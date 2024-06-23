from typing import Optional
from app.models.show_model import Show


class Artist:
    def __init__(self, name: str, host_name_and_stage: str, weekend: str, date: str, songs_num: int = 0,
                 spotify_link: str = ""):
        self.name = name
        self.songs_num = songs_num
        self.show = Show(weekend, host_name_and_stage, date)
        self.show2: Optional[Show] = None
        self.spotify_link = spotify_link

    def add_new_show(self, weekend: str, host_name_and_stage: str, date: str) -> None:
        self.show2 = Show(weekend, host_name_and_stage, date)

    def __str__(self, selected_weekend: str = "") -> str:
        art_with_spotify = f'<a href="{self.spotify_link}">{self.name}</a>' if self.spotify_link else self.name
        output = f"{art_with_spotify}- Songs number: {self.songs_num}\n"
        show_string = self.get_show_string(selected_weekend)
        output += show_string
        return output

    def get_show_string(self, selected_weekend: str) -> str:
        if not selected_weekend or selected_weekend.lower() == "both":
            show_string = f"{self.show}"
            if self.show2:
                show_string += f"{self.show2}"
        elif self.show.weekend_number.lower() == selected_weekend.lower():
            show_string = f"{self.show}"
        elif self.show2 and self.show2.weekend_number.lower() == selected_weekend.lower():
            show_string = f"{self.show2}"
        else:
            show_string = "No show for the selected weekend."
        return show_string
