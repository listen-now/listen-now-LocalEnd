#!/usr/bin/env python3
# @File:main.py
# @Date:2018/5/9
# Author:Cat.1
# 2018/05/20 代码部分重构
# 2018/07/15 重构系统
# 2018/07/29 增加酷狗音乐初步支持
# 2018/08/03 增加百度、酷我音乐初步支持
# 2018/08/25 增加Spotify初步支持


import json, time, requests
from Log import Logger
from Module import RetDataModule, ReturnStatus
from flask import Flask, request, Response, jsonify

from Scrawl.QQMusic import QQMusicAdaptor as QQMusic
from Scrawl.KugouMusic import KugoMusicAdaptor as KugoMusic
from Scrawl.KuwoMusic import KuwoMusicAdaptor as KuwoMusic
from Scrawl.MiguMusic import MiguMusicAdaptor as MiguMusic
from Scrawl.BaiduMusic import BaiduMusicAdaptor as BaiduMusic
from Scrawl.NeteasyMusic import NeteasyMusicAdaptor as NeteasyMusic


"""
引入json网页框架用于开放api接口
引入json库用于解析前端上传的json文件
引入AES外部文件用于加密网易云音乐的POST数据
引入Scrawl用于各个平台的爬虫
引入config文件用于配置数据库等配置信息
引入Sync文件用不各个平台歌单信息同步
引入Module文件用于规定各个平台返回数据的格式和针对不同状况的错误处理码
引入flask_cors用于运行跨域访问
"""

"""
>>>全局设定开始>>>

"""

re_dict = {}
# 返回参数初始化

logger = Logger.Logger('Log/Listen-now.log', level='info')
# 初始化日志函数，返回等级为info及以上

# sp = spotify.Spotify(2) # 必要的全局变量 参数是保持的待用驱动数 一个驱动可以处理一个用户
# 暂时因为spotify平台问题而没有启用

app = Flask(__name__)
# 形成flask实例


def _Return_Error_Post(code, status, detail="", **kw):
    """
    用于向前端反馈错误信息的函数
    包括code参数 错误码
    status     状态信息
    detail     详细信息
    组装数据包成json格式返回
    """
    RetureContent = {"code": code, "status": status, "detail": detail, "other": kw}
    logger.logger.info("向前端返回请求结果" + RetureContent)

    return RetureContent


@app.route('/search', methods=['POST', 'GET'])
def search_json():
    """
    用于接受各类前端的歌曲名字的api请求
    分为POST/GET请求
    如果是POST则又分为
    三大platform平台不同而调起不同的爬虫脚本
    有关更多错误码信息请查阅SDK文档
    """
    global re_dict
    if request.method == 'POST':
        re_dict = {}
        data = request.get_data()  # 获得json数据包.
        try:
            dict_data = json.loads(data)  # 解析json数据包.
        except:
            re_dict = _Return_Error_Post(code=ReturnStatus.ERROR_PSOT_DATA, status="Failed", detail="ERROR_PSOT_DATA")
        try:
            music_title = dict_data["title"]
            music_platform = dict_data["platform"]
            try:
                music_page = dict_data["page"]
            except:
                music_page = 1
            # 获得请求的歌曲名字和选择的音乐平台
        except:
            re_dict = _Return_Error_Post(code=ReturnStatus.ERROR_PARAMS, status="Failed", detail="ERROR_PARAMS")
        else:
            if music_page > 10:
                re_dict = _Return_Error_Post(code=ReturnStatus.OVER_MAXPAGE, status="Failed", detail="OVER_MAXPAGE")
            else:
                if music_title != '' or music_title != None:
                    platform = platform_factory(music_platform)
                    if platform == None:
                        logger.logger.warning("用户请求了一个不被支持的平台")
                        re_dict = _Return_Error_Post(code=ReturnStatus.NO_SUPPORT, status="Failed", detail="NO_SUPPORT")
                    else:
                        re_dict = platform.search_by_key(music_title, music_page)
                else:
                    logger.logger.warning("用户的请求有参数错误" + dict_data)
                    re_dict = _Return_Error_Post(code=ReturnStatus.ERROR_PARAMS, status="Failed", detail="ERROR_PARAMS")
        finally:
            if re_dict == "":
                re_dict = _Return_Error_Post(code=ReturnStatus.NOT_SAFE, status="Failed", detail="NOT_SAFE")
            elif re_dict == ReturnStatus.NO_EXISTS:
                re_dict = _Return_Error_Post(code=ReturnStatus.NO_EXISTS, status="Failed", detail="NO_EXISTS")
                logger.logger.warning("用户的请求不存在。" + dict_data)
            response = Response(json.dumps(re_dict), mimetype='application/json')
            response.headers.add('Server', 'python flask')
            return response

    else:
        logger.logger.warning("请求search接口使用了错误的方法")
        re_dict = _Return_Error_Post(code=ReturnStatus.ERROR_METHOD, status="Failed", detail="ERROR_METHOD")
        response = Response(json.dumps(re_dict), mimetype='application/json')
        response.headers.add('Server', 'python flask')
        return response


@app.route('/TopSongList', methods=['POST', "GET"])
def Return_Random_User_Song_List():
    """
    用于向前端返回20个热门歌单信息
    允许GET、POST任何请求均可
    """
    return


@app.route('/song_list_requests', methods=['POST', 'GET'])
def Return_User_Song_List_Detail():
    """
    用于向前端返回某一个歌单的详细信息(
        包括歌单的名称，
        歌单id，
        每首歌曲id，
        歌曲名称，
        歌曲演唱者
        )
    """
    return

@app.route('/id', methods=['POST', 'GET'])
def play_id():
    """
    用于前端请求歌曲id时服务器针对性的反馈方法
    基本内容如上.
    """
    global re_dict
    if request.method == 'POST':
        data = request.get_data()
        dict_data = json.loads(data)

        try:
            music_platform = dict_data['platform']
            music_id       = dict_data["id"]
        except:
            re_dict = _Return_Error_Post(code=ReturnStatus.ERROR_PARAMS, status="Failed", detail="ERROR_PARAMS")
        else:
            if music_platform != '' or music_platform != None:
                platform = platform_factory(music_platform)
                if platform == None:
                    logger.logger.warning("平台不受支持，请求的平台是: " + music_platform)
                    re_dict = _Return_Error_Post(code=ReturnStatus.NO_SUPPORT, status="Failed", detail="NO_SUPPORT")
                else:
                    re_dict = platform.search_by_id(music_id)
        finally:
            response = Response(json.dumps(re_dict), mimetype='application/json')
            response.headers.add('Server', 'python flask')
            return response

    else:
        re_dict = _Return_Error_Post(code=ReturnStatus.ERROR_METHOD, status="Failed", detail="ERROR_METHOD")
        response = Response(json.dumps(re_dict), mimetype='application/json')
        response.headers.add('Server', 'python flask')
        return response


def platform_factory(platform_name):
    """
        音乐平台工厂
    """
    if platform_name == "Neteasemusic":
        return NeteasyMusic.NeteasyMusicP()
    elif platform_name == "QQmusic":
        return QQMusic.QQMusicP()
    elif platform_name == "Kugoumusic":
        return KugoMusic.KugouMusicP()
    elif platform_name == "Kuwomusic":
        return KuwoMusic.KuwoMusicP()
    elif platform_name == "Migumusic":
        return MiguMusic.MiguP()
    elif platform_name == "Baidumusic":
        return BaiduMusic.BaiduMusicP()
    else:
        return None


if __name__ == '__main__':
    host = 'localhost'
    port = '80'
    app.run(host=host, port=int(port), debug=True)

