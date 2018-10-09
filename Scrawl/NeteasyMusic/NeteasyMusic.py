#!/usr/bin/env python3
# @File:Scrawl_Neteasymusic.py
# @Date:2018/5/9
# Author:Cat.1
import datetime

import requests, re, json
import urllib.parse
import redis
from Module import ReturnStatus
from Module import RetDataModule
from Module import ReturnFunction
from Scrawl.NeteasyMusic.NeteasyHelper import AES


class Netmusic(object):


    def __init__(self):
        self.requ_date    = {"song":{"totalnum":"", "list":[{}]}}

        self.search_url   = "http://music.163.com/api/search/get/web?csrf_token="
        # 通过歌曲名称获得歌曲的ID信息(GET请求)
        self.play_url     = "http://music.163.com/weapi/song/enhance/player/url?csrf_token="
        # 通过加密数据POST请求得到播放地址
        # https://api.imjad.cn/cloudmusic/?type=song&id=%s&br=320000
        self.url_         = "http://music.163.com/song/media/outer/url?id=%s.mp3"
        # 网易根据api直接请求到下载音乐地址(%s均为歌曲id)
        self.comment_url  = "https://music.163.com/weapi/v1/resource/comments/R_SO_4_%s?csrf_token="
        # 通过加密数据POST请求得到评论内容        
        self.lyric_url    = "http://music.163.com/api/song/lyric?id=%s&lv=1&kv=1&tv=-1"      
        # 通过id获得歌曲的歌词信息(json包) 只需要(GET请求)
        self.session      = requests.session()
        self.headers      = {
        'User-Agent':'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.13; rv:57.0) Gecko/20100101 Firefox/57.0',
        'Referer':'http://music.163.com/',
        'Content-Type':'application/x-www-form-urlencoded'
        }
        self.play_default = "{\"ids\":\"[%s]\",\"br\":%s\
        ,\"csrf_token\":\"\"}"
        self.br    = "128000"

    def requests_play_url(self, music_id):
        self.post_data = AES.encrypted_request(self.play_default %(music_id, self.br))
        resp           = self.session.post(url=self.play_url, data=self.post_data, headers=self.headers)
        resp         = resp.json()
        play_url       = resp["data"][0]['url']
        if play_url == None:
            play_url = self.url_ %(music_id)
        self.requ_date["song"]["list"][0].update({"play_url": play_url})



    def requests_comment(self, music_id, proxies=''):
        self.post_data = AES.encrypted_request(self.play_default %(music_id, self.br))
        resp         = self.session.post(url=self.comment_url %(music_id), data=self.post_data, headers=self.headers)
        try:
            resp       = resp.json()
            self.requ_date["song"]["comments"] = []

            for item in resp["hotComments"]:
                like              = item["likedCount"]
                username          = item['user']["nickname"]
                comment_content   = item["content"]
                comment_timestamp = int(str(item["time"])[:-3])
                dateArray         = datetime.datetime.utcfromtimestamp(comment_timestamp)
                comment_time      = dateArray.strftime("%Y--%m--%d %H:%M:%S")
                self.requ_date["song"]["comments"].append({"comment_time":comment_time, "comment_content":comment_content, "likecount":like, "username":username})
        except:
            return self.requ_date["song"]["comments"]

        return self.requ_date["song"]["comments"]


    def music_id_requests(self, music_id):
        id_flag        = 1
        musicDataiList = self.music_detail(music_id, id_flag)

        lyric          = self.requests_lyric(music_id)
        re_dict_class  = ReturnFunction.RetDataModuleFunc()
        re_dict        = re_dict_class.RetDataModSong(
                            self.url_ % (music_id),
                            music_id,
                            musicDataiList['music_name'],
                            musicDataiList['artists'],
                            musicDataiList['image_url'],
                            lyric['lyric'],
                            comment=self.requests_comment(music_id),
                            tlyric=lyric['tlyric'],
                            code=ReturnStatus.SUCCESS,
                            status='Success')

        return re_dict

    def music_detail(self, music_id, id_flag=0, proxies=''):
        music_data = {}
        url        = "http://music.163.com/api/song/detail?ids=[%s]"
        if proxies == '':
          resp         = self.session.get(url=url %music_id, headers=self.headers)
        else:
          resp         = self.session.get(url=url %music_id, headers=self.headers, proxies=proxies)
        try:
            content    = resp.json()
            name       = content['songs'][0]["name"]
            artists    = content['songs'][0]["artists"][0]["name"]
            image_url  = content['songs'][0]["album"]["picUrl"]
        except:
            music_data['code'] = ReturnStatus.ERROR_SEVER
        else:

            music_data.update({"image_url":image_url, "music_name":name, "artists":artists})
            try:
                if id_flag == 1:
                    self.requ_date["song"]["list"][0].update(music_data)
                try:
                    self.requ_date["song"]["list"][0]["image_url"]
                except KeyError:
                    self.requ_date["song"]["list"][0].update(music_data)
                else:
                    self.requ_date["song"]["list"].append(music_data)
            except:
                self.requ_date["song"]["list"] = {}
                self.requ_date["song"]["list"].append(music_data)
        return self.requ_date["song"]["list"][0]



    def pre_response_neteasymusic(self, text, page = 1):
        global count, i, lock

        text       = urllib.parse.quote(text)                        
        data       = "hlpretag=&hlposttag=&s=%s&type=1&offset=%s&total=true&limit=10" %(text, str((page-1)*10))
        resp       = self.session.post(url = self.search_url, data = data, headers = self.headers)
        result     = resp.json()
        try:
            songList      = ReturnFunction.songList(Data=result['result']['songs'], songdir="[\"name\"]", artistsdir="[\'artists\'][0][\'name\']", iddir="[\"id\"]", page=page)
            songList.buidingSongList()
            re_dict_class = ReturnFunction.RetDataModuleFunc()
            now_page      = page
            before_page, next_page = page-1, page+1
            totalnum      = songList.count
            re_dict       = re_dict_class.RetDataModSearch(now_page, next_page, before_page, songList, totalnum, code=ReturnStatus.SUCCESS, status='Success')
        except KeyError:
            code   = ReturnStatus.NO_EXISTS
            status = 'ReturnStatus.NO_EXISTS'
            return ReturnStatus.NO_EXISTS

        except:
            code   = ReturnStatus.ERROR_UNKNOWN
            status = 'ReturnStatus.ERROR_UNKNOWN'
            return ReturnStatus.ERROR_UNKNOWN
        else:
            re_dict['code']   = ReturnStatus.SUCCESS
            re_dict['status'] = 'ReturnStatus.SUCCESS'
            return re_dict



    def requests_lyric(self, music_id):
        self.lyric_data  = self.session.get(url = self.lyric_url %(music_id), headers = self.headers)
        self.lyric  = self.lyric_data.json()["lrc"].get("lyric", "本首歌还没有歌词")
        self.tlyric = self.lyric_data.json()["tlyric"].get("lyric", "None")

        return {"lyric":self.lyric, "tlyric":self.tlyric}


if __name__ == '__main__':
    test = Netmusic()
    print(test.music_id_requests(3570196))
    # print(test.pre_response_neteasymusic('hangover'))
    # test.pre_response_neteasymusic('大鱼')





