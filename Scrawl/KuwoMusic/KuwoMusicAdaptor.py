from Scrawl.KuwoMusic import KuwoMusic


class KuwoMusicP(object):
    def __init__(self):
        self.platform = KuwoMusic.KuwoMusic()

    def search_by_key(self, keyword, page = 1):
        return self.platform.Search_List(keyword, page)

    def search_by_id(self, music_id):
        return self.platform.Search_details(music_id)