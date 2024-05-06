# ./app/show.py

class Show:
    def __init__(self, weekend_number,host_name_and_stage, date):
        self.weekend_number = weekend_number
        self.host_name_and_stage = host_name_and_stage
        self.date = date

    def __str__(self):
        return f"*{self.weekend_number}*\nStage and host name: {self.host_name_and_stage}\nDate: {self.date}"
