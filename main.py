# pip install google-auth-oauthlib google-auth-httplib2 google-api-python-client pytz pyinstaller
import logging
import json
import os
import inspect
import google.auth.transport.requests
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from datetime import datetime, timedelta, timezone

from basic import *
import command
from command import Command
from api import youtubeapi
SCOPES = ['https://www.googleapis.com/auth/youtube.force-ssl']
redirect_uri = 'http://localhost:8080/'

# yt api documentation
# LiveStreams:https://developers.google.com/youtube/v3/live/docs/liveStreams?hl=zh-tw
# LiveBroadcasts:https://developers.google.com/youtube/v3/live/docs/liveBroadcasts?hl=zh-tw
# Videos:https://developers.google.com/youtube/v3/docs/videos?hl=zh-tw

# 類別 ID(Category ID): https://mixedanalytics.com/blog/list-of-youtube-video-category-ids/
# 或用 api.http:line 1 取得類別 id

# Game Title
# https://stackoverflow.com/questions/39907947/youtube-api-how-to-set-game-title

# 如果修改範圍，刪除 token.json 文件
def get_authenticated_service():
    if not os.path.exists('client_secret.json'):
        print('client_secret.json not found')
        exit()
    creds = None
    # 檢查 token.json 文件是否存在
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    # 如果沒有（或無效），進行 OAuth 2.0 流程
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(google.auth.transport.requests.Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'client_secret.json', SCOPES)
            flow.redirect_uri = redirect_uri
            creds = flow.run_local_server(port=8080)
        # 保存憑證
        with open('token.json', 'w') as token:
            token.write(creds.to_json())
    return build('youtube', 'v3', credentials=creds)

# 獲取module裏面繼承主類Command的所有成員名稱
def get_classes(module):
    parent_class = Command
    return [name for name, obj in inspect.getmembers(module) if inspect.isclass(obj) and issubclass(obj, parent_class) and obj is not parent_class]

if __name__ == "__main__":
    # Api usage 2 time
    logging.basicConfig(filename='app.log',encoding='utf-8', level=logging.DEBUG, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.INFO)
    # logger.debug('調試日誌')
    # logger.info('信息日誌')
    # logger.warning('警告日誌')
    # logger.error('錯誤日誌')
    # logger.critical('嚴重錯誤日誌')
    data = {}
    with open('url.json', 'r') as f:
        data['url'] = json.load(f)

    youtube = get_authenticated_service()
    ytapi = youtubeapi(youtube, logger)
    channel_id = ytapi.get_channel_id()
    liveing = ytapi.get_live_stream(channel_id)
    if liveing:
        video_id = liveing['videoId']
        live_description = ytapi.get_live_description(video_id)
        live_time = convert_timezone(ytapi.get_live_stream_start_time(video_id))
        data['live_time'] = live_time
        print("URL:" + id_to_link(video_id))
        print("描述:" + live_description)
        print("開始時間:" + str(live_time))
        print("已直播:" + str(get_live_stream_time(live_time)))
    else:
        print("當前沒有進行中的直播")

    commandlist = []
    classes = get_classes(command)
    for classname in classes:
        cls = getattr(command, classname)
        commandlist.append(cls())
    menu = []
    for index, commands in enumerate(commandlist, start=1):
        menu.append(str(index)+':'+commands.name)
    for i in menu:
        print(i)
    while True:
        commandnum = int(input("輸入操作數字:"))
        if 0 < commandnum < len(commandlist):
            commands = commandlist[commandnum-1]
            if commands.inited:
                commands.main()
            else:
                commands.init(ytapi, logger, liveing, channel_id,data)
                commands.main()
        elif commandnum == len(commandlist)+1:
            for i in menu:
                print(i)
        else:
            print('沒有定義的操作')
