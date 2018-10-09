from Scrawl.KugouMusic import kugou


class KugouMusicP(object):
    def __init__(self):
        self.platform = kugou.Kugou()

    def search_by_key(self, keyword, page = 1):
        return self.platform.Search_List(keyword, page)

    def search_by_id(self, music_id):
        return self.platform.hash_search(music_id)
