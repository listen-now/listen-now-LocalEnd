from Scrawl.BaiduMusic import BaiduMusic


class BaiduMusicP(object):
    def __init__(self):
        self.platform = BaiduMusic.BaiduMusic()

    def search_by_key(self, keyword, page = 1):
        return self.platform.search_by_keyword(keyword, page)

    def search_by_id(self, music_id):
        return self.platform.search_by_id(music_id)
