class Playlist:
    def __init__(self, platform, link):
        self.platform = platform
        self.link = link

    def __str__(self):
        return f"*{self.platform}*\nLink: {self.link}"
