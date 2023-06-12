from show import Show
class Artist:
    def __init__(self, name,songs_num, host_name_and_stage, weekend, date):
        self.name = name
        self.songs_num = songs_num
        self.show = Show(weekend, host_name_and_stage, date)
        self.show2 = None

    def __init__(self, name, host_name_and_stage, weekend, date):
        self.name = name
        self.songs_num = 1
        self.show = Show(weekend, host_name_and_stage, date)
        self.show2 = None

    def add_show(self,weekend, host_name_and_stage, date):
        self.show2 = Show(weekend,host_name_and_stage,date)

    def __str__(self):
        output = f"*{self.name}*- Songs number: {self.songs_num}\nShow:\n{self.show}"
        if self.show2 is not None:
            output += f"\nShow2:\n{self.show2}"
        return output
