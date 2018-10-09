from Scrawl.NeteasyMusic import NeteasyMusic


class NeteasyMusicP(object):
    def __init__(self):
        self.platform = NeteasyMusic.Netmusic()

    def search_by_key(self, keyword, page = 1):
        return self.platform.pre_response_neteasymusic(keyword, page)

    def search_by_id(self, music_id):
        return self.platform.music_id_requests(music_id)