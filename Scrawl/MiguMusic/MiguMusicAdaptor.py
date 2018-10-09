from Scrawl.MiguMusic import MiguMusic


class MiguP(object):
    def __init__(self):
        self.platform = MiguMusic.Migu()

    def search_by_key(self, keyword, page):
        return self.platform.search(keyword, page)

    def search_by_id(self, music_id):
        return self.platform.search_details(music_id)