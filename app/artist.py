# ./app/artist.py
from app.show import Show


class Artist:
    def __init__(self, name, host_name_and_stage, weekend, date, songs_num=0):
        self.name = name
        self.songs_num = songs_num
        self.show = Show(weekend, host_name_and_stage, date)
        self.show2 = None

    def add_new_show(self, weekend, host_name_and_stage, date):
        """
        Add a new show to the object's attribute 'show2'.

        This method creates a new 'Show' object with the provided 'weekend', 'host_name_and_stage',
        and 'date' arguments and assigns it to the 'show2' attribute of the object.

        Arguments:
            self: The object reference.
            weekend (str): The weekend information for the show.
            host_name_and_stage (str): The name of the host and the stage for the show.
            date (str): The date of the show.

        Returns:
            None: The method does not return anything; it simply updates the 'show2' attribute.
        """
        self.show2 = Show(weekend, host_name_and_stage, date)

    def __str__(self, selected_weekend=""):
        if selected_weekend == "":
            output = f"*{self.name}*- Songs number: {self.songs_num}\nShow:\n{self.show}"
            if self.show2:
                output += f"\nShow2:\n{self.show2}"
        elif self.show.weekend_number.lower() == selected_weekend.lower():
            output = f"*{self.name}*- Songs number: {self.songs_num}\nShow:\n{self.show}"
        elif self.show2 and self.show2.weekend_number.lower() == selected_weekend.lower():
            output = f"*{self.name}*- Songs number: {self.songs_num}\nShow2:\n{self.show2}"
        else:
            output = f"*{self.name}*- Songs number: {self.songs_num}\nNo show for the selected weekend."
        return output
