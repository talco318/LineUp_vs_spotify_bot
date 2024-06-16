import logging


class UserSession:
    def __init__(self):
        self.my_relevant = []
        self.selected_weekend = "none"
        self.artists_str = ""
        self.artists_by_weekend = []
        self.playlist_links_list = []

    def clear_all(self):
        self.my_relevant.clear()
        self.selected_weekend = "none"
        self.artists_str = ""
        self.artists_by_weekend.clear()
        self.playlist_links_list.clear()
        logging.info("All data has been cleared")