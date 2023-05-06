class Artist:
    def __init__(self, name, host_name_and_stage, weekend, date):
        self.name = name
        self.host_name_and_stage = host_name_and_stage
        self.weekend = weekend
        self.date = date

    def __str__(self):
        return f"Artist: {self.name}\nStage and host name: {self.host_name_and_stage}\nWeekend: {self.weekend}\nDate: {self.date}"
