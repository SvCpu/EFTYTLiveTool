# pip install google-auth-oauthlib google-auth-httplib2 google-api-python-client pytz pyinstaller
import logging
import json
import os
import re
import time
import google.auth.transport.requests
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from datetime import datetime, timedelta, timezone
import requests
import pytz
SCOPES = ['https://www.googleapis.com/auth/youtube.force-ssl']

# yt api
# LiveStreams:https://developers.google.com/youtube/v3/live/docs/liveStreams?hl=zh-tw
# LiveBroadcasts:https://developers.google.com/youtube/v3/live/docs/liveBroadcasts?hl=zh-tw

EFT_game_title = "逃離塔科夫"
# 遊戲名稱設置那裡還沒有方法可以添加
# 類別 ID(Category ID): https://mixedanalytics.com/blog/list-of-youtube-video-category-ids/

# eventType 直播事件類型:completed：已完成的直播事件。live：正在進行的直播事件。upcoming：即將開始的直播事件。
# order 指定搜索結果的排序:
    # date：按發布日期排序，最新的影片排在最前面。
    # rating：按評分排序，評分最高的影片排在最前面。
    # relevance：按相關性排序，與搜索查詢最相關的影片排在最前面。
    # title：按標題的字母順序排序。
    # videoCount：按頻道中的影片數量排序，影片數量最多的頻道排在最前面。
    # viewCount：按觀看次數排序，觀看次數最多的影片排在最前面

# status:
# privacyStatus:public-所有人都可以看到直播。,private-只有您和您選擇的人可以看到直播。,unlisted-直播未公開列出，但任何知道連結的人都可以訪問。
# selfDeclaredMadeForKids: 表示直播是為兒童製作的
# embeddable:T/F允許將直播嵌入到其他網站
# license:youtube-標準YouTube許可證,creativeCommon-知識共享授權
# publishAt:指示何時應發布直播串流的時間戳記。

# contentDetails
# latencyPreference(延遲類型):"normal"：正常延遲,"low"：低延遲,"ultraLow"：超低延遲

# 如果修改範圍，刪除 token.json 文件
def get_authenticated_service():
    if not os.path.exists('client_secret.json'):
        print('client_secret.json not found')
        os.quit(1)
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
            flow.redirect_uri = 'http://localhost:8080/'
            creds = flow.run_local_server(port=8080)
        # 保存憑證
        with open('token.json', 'w') as token:
            token.write(creds.to_json())
    return build('youtube', 'v3', credentials=creds)

# 獲取頻道 ID
def get_channel_id():
    request = youtube.channels().list(
        part='id',
        mine=True
    )
    response = request.execute()
    if 'items' in response and len(response['items']) > 0:
        return response['items'][0]['id']
    else:
        return None

# 獲取正在直播的鏈接
def get_live_stream(channel_id):
    request = youtube.search().list(
        part='snippet',
        channelId=channel_id,
        eventType='live',
        type='video'
    )
    response = request.execute()

    if 'items' in response and len(response['items']) > 0:
        snippet = response['items'][0]['snippet']
        out = {'title': snippet['title'],
            'videoId': response['items'][0]["id"]['videoId'],
            'description': snippet['description'],
            'liveBroadcastContent': snippet['liveBroadcastContent'],
            'publishTime': snippet["publishTime"],
            }
        return out
    else:
        return None
# 获取频道直播影片列表前10部的直播影片(非排名)
def get_top_live_videos():
    request = youtube.search().list(
        part='snippet',
        channelId=channel_id,
        eventType='completed',
        type='video',
        maxResults=10,
        order='date'
    )
    response = request.execute()
    items = response.get("items", [])
    outlist = []
    for video in items:
        snippet = video['snippet']
        out = {'title': snippet['title'],
            'videoId': video["id"]['videoId'],
            'description': snippet['description'],
            'liveBroadcastContent': snippet['liveBroadcastContent'],
            'publishTime': snippet["publishTime"],
            }
        outlist.append(out)
    return outlist

def id_to_link(id):
    return f"https://www.youtube.com/watch?v={id}"

# 獲取直播描述
def get_live_description(video_id):
    request = youtube.videos().list(
        part='snippet',
        id=video_id
    )
    response = request.execute()

    if 'items' in response and len(response['items']) > 0:
        description = response['items'][0]['snippet']['description']
        return description
    else:
        return None

# 獲取指定影片的詳細信息
def get_video_details(video_id):
    request = youtube.videos().list(
        part="snippet",
        id=video_id
    )
    response = request.execute()
    return response.get('items', [])

# 獲取直播開始的時間
def get_live_stream_start_time(video_id):
    request = youtube.videos().list(
        part='liveStreamingDetails',
        id=video_id
    )
    response = request.execute()

    if 'items' in response and len(response['items']) > 0:
        live_details = response['items'][0]['liveStreamingDetails']
        start_time = live_details['actualStartTime']
        return start_time
    else:
        return None


def get_live_stream_time(start_time):
    now = datetime.now(timezone.utc)
    duration = now - start_time
    return duration


def convert_timezone(utc_time_str):
    # 解析 UTC 時間字串
    utc_time = datetime.strptime(utc_time_str, "%Y-%m-%dT%H:%M:%SZ")

    # 設定時區
    macau_tz = pytz.timezone("Asia/Macau")

    # 將 UTC 時間轉換為澳門時間
    macau_time = utc_time.replace(tzinfo=pytz.utc).astimezone(macau_tz)

    return macau_time


# 修改直播描述
def update_live_description(video_id, new_description):
    request = youtube.videos().update(
        part='snippet',
        body={
            'id': video_id,
            'snippet': {
                'description': new_description
            }
        }
    )
    response = request.execute()
    return response



# 創建直播
# title = "New Live Broadcast"
# description = "This is a test broadcast."
# start_time = "2024-09-22T15:00:00Z"
# end_time = "2024-09-22T16:00:00Z"
# create_broadcast(title, description, start_time, end_time)
def create_broadcast(title, description, start_time, end_time=''):
    requestbody = {
            'snippet': {
                'title': title,
                'description': description,
                'scheduledStartTime': start_time,
                'categoryId' : 20
            },
            'status': {
                'privacyStatus': 'public',
                "selfDeclaredMadeForKids": False
            }
        }
    if end_time:
        requestbody["snippet"]['scheduledEndTime'] = end_time
    request = youtube.liveBroadcasts().insert(
        part='snippet,status',
        body=requestbody
    )
    try:
        broadcast_response = request.execute()
    except Exception as e:
        logger.error('Broadcast '+title+' create request error,error info is '+str(e))
        print('發送請求時出錯, 請查詢日誌')
    else:
        logger.info('Broadcast '+title+' create request Sent,start time is '+start_time)
    if broadcast_response['id']:
        logger.info("The live broadcast with activity ID "+broadcast_response['id']+" has been created")
        print('ID為'+broadcast_response['id']+'的直播已建立')
        print('直播聊天室ID:'+broadcast_response['snippet']['liveChatId'])
        input('為避免浪費API查詢額度, 請確定直播已傳送到YouTube後按下任意鍵繼續')
        print('查詢活動狀態的直播流並綁定到直播活動')
        streamId = ''
        for _ in range(3):
            # 獲取直播流信息
            streams_request = youtube.liveStreams().list (
                part='snippet,contentDetails,status',
                mine=True
            )
            logger.info('Query live stream status information')
            out_response = streams_request.execute()
            # 過濾出 streamStatus 為 active 的項目
            active_streams = [item for item in out_response["items"] if item["status"]["streamStatus"] == "active"]
            if active_streams:
                if len(active_streams) == 1:
                    streamId = active_streams[0]["id"]
                    break
                else:
                    print('多於一個直播流啟動處於活動狀態')
            else:
                print('沒有活動狀態的直播流')
            time.sleep(3)
        if streamId:
            # 將直播流綁定到直播活動
            bind_request = youtube.liveBroadcasts().bind(
                part='id,contentDetails',
                id=broadcast_response['id'],
                streamId=streamId
            )
            try:
                bind_response = bind_request.execute()
            except Exception as e:
                logger.error('Live Streaming '+streamId+' Bind to Live Event '+broadcast_response['id']+' Request Sent,error info is '+str(e))
            else:
                logger.info('Live Streaming '+streamId+' Bind to Live Event '+broadcast_response['id']+' Request Sent')
                print('直播流'+streamId+'已與直播活動'+broadcast_response['id']+'繫結')
                startlive_request=youtube.liveBroadcasts().transition(
                    broadcastStatus="live",
                    id=broadcast_response['id']
                )
                logger.info('Live broadcast '+broadcast_response['id']+' Start Request Sent')
                startlive_request.execute()
                print('直播'+broadcast_response['id']+'已設置爲活動狀態')
        else:
            print('沒有活動狀態的直播流')
            bind_response = None
    return (broadcast_response, bind_response)

# 更新直播活動
    broadcast_id = ""
    new_title = "Updated Live Broadcast Title"
    new_description = "This is an updated description."
    updated_broadcast = update_broadcast(
        broadcast_id, new_title, new_description)
    print("Broadcast updated:", updated_broadcast)
def update_broadcast(broadcast_id, title, description,CategoryId='',GameTitle=''):
    requestbody = {
            'id': broadcast_id,
            'snippet': {
                'title': title,
                'description': description
            },
            # "status": {
            #     "selfDeclaredMadeForKids": False
            # }
        }
    if CategoryId:
        requestbody['snippet']['categoryId'] = CategoryId
    if GameTitle:
        requestbody['snippet']['gameTitle'] = GameTitle
    request = youtube.liveBroadcasts().update(
        part='snippet',
        body=requestbody
    )
    response = request.execute()
    logger.info('request Broadcast '+ broadcast_id + ' chage of '+title+ ' '+description)
    return response

# 刪除直播活動
# delete_response = delete_broadcast(broadcast_id)
# print("Broadcast deleted:", delete_response)
def delete_broadcast(broadcast_id):
    request = youtube.liveBroadcasts().delete(
        id=broadcast_id
    )
    try:
        request.execute()
    except Exception as e:
        logger.error('Broadcast '+ broadcast_id + ' del request error with:'+str(e))
    else:
        logger.info('Broadcast '+ broadcast_id + ' del request Sent')

# 獲取直播聊天信息
# live_chat_id = "YOUR_LIVE_CHAT_ID"
# chat_messages = get_live_chat_messages(live_chat_id)
# for message in chat_messages['items']:
#     print(f"{message['authorDetails']['displayName']}: {message['snippet']['displayMessage']}")


def get_live_chat_messages(live_chat_id):
    request = youtube.liveChatMessages().list(
        liveChatId=live_chat_id,
        part='snippet,authorDetails'
    )
    response = request.execute()
    return response

# 獲取live_chat_id
def get_live_chat_id(video_id):
    request = youtube.videos().list(
        part='liveStreamingDetails',
        id=video_id
    )
    response = request.execute()

    if 'items' in response and len(response['items']) > 0:
        live_details = response['items'][0]['liveStreamingDetails']
        live_chat_id = live_details.get('activeLiveChatId')
        return live_chat_id
    else:
        return None

# 獲取直播的詳細信息
# live_details.get('actualStartTime')
# actualStartTime：這是直播實際開始的時間。
# actualEndTime：這是直播實際結束的時間（如果直播已經結束）。
# scheduledStartTime：這是直播計劃開始的時間。
# scheduledEndTime：這是直播計劃結束的時間。
# concurrentViewers：這是當前同時觀看直播的觀眾數量。
# activeLiveChatId：這是直播聊天的唯一標識符，用於獲取直播聊天信息。
# boundStreamId：這是與直播綁定的流 ID。
# monitorStream：這包含監控流的相關信息，例如監控流的 URL。
# recordingStatus：這表示直播的錄製狀態，例如是否正在錄製。
# broadcastStatus：這表示直播的狀態，例如 live、completed 或 testing。
def get_live_stream_details(video_id):
    request = youtube.videos().list(
        part='liveStreamingDetails',
        id=video_id
    )
    response = request.execute()

    if 'items' in response and len(response['items']) > 0:
        live_details = response['items'][0]['liveStreamingDetails']
        print(response)
        return live_details
    else:
        return None

def is_video_live(video_id):
    request = youtube.videos().list(
        part='snippet,liveStreamingDetails',
        id=video_id
    )
    response = request.execute()
    if 'items' in response and len(response['items']) > 0:
        live_broadcast_content = response['items'][0]['snippet']['liveBroadcastContent']
        return live_broadcast_content
    else:
        return False

# def get_latest_video_id(playlist_id):
#     request = youtube.playlistItems().list(
#         part='snippet',
#         playlistId=playlist_id,
#         maxResults=1
#     )
#     response = request.execute()
#     if 'items' in response and len(response['items']) > 0:
#         return response['items'][0]['snippet']['resourceId']['videoId']
#     else:
#         return None

# 獲取指定播放列表中最後新增的視頻
def get_latest_video_title(playlist_id):
    request = youtube.playlistItems().list(
        part='snippet',
        playlistId=playlist_id,
        maxResults=3
    )
    response = request.execute()
    if 'items' in response and len(response['items']) > 0:
        print(response)
        latest_video = max(response['items'], key=lambda x: x['snippet']['publishedAt'])
        out = {
            "title": latest_video['snippet']['title'],
            "videoid": latest_video['snippet']['resourceId']['videoId'],
            "description": latest_video['snippet']['description'],
            "publishedAt": latest_video['snippet']['publishedAt']
        }
        return out
    else:
        return None

def sort_videos(video_list):
    # 解析日期字串並排序
    parsed_videos = [(video, parse_date_string(video[10:])) for video in video_list]
    sorted_videos = sorted(parsed_videos, key=lambda x: (x[1]['year'], x[1]['month'], x[1]['day'], x[1]['serial']), reverse=True)
    return [video[0] for video in sorted_videos]

# 字符串操作和日期解析
# date_string = "20240925-1"
# result = parse_date_string(date_string)
# print(result)  # 輸出: [2024, 9, 25, 1]
def parse_date_string(date_string):
    # 分割日期和序號
    date_part, serial_part = date_string.split('-')
    try:
        int(serial_part)
    except ValueError:
        match = re.match(r'^\d+', serial_part)
        serial_part = match.group(0) if match else ''
        if serial_part == '':
            serial_part = 1
    out = {
        "year": date_part[:4],
        "month": date_part[4:6],
        "day": date_part[6:8],
        "serial": int(serial_part)
    }
    return out

def get_last_eft_title():
    renamedatestr = ''
    top_live = get_top_live_videos()
    titlelist = []
    for video in top_live:
        titlelist.append(video['title'])
    titlelist = sort_videos(titlelist)
    now = datetime.now()
    lastlive = parse_date_string(titlelist[0][10:])
    nowtimestr = str(now.year)+now.strftime("%m")+now.strftime("%d")
    if (lastlive["year"]+lastlive['month']+lastlive['day']) == nowtimestr:
        renamedatestr = nowtimestr+'-'+str(lastlive["serial"]+1)
    else:
        renamedatestr = nowtimestr+"-1"
    return '《逃离塔科夫PVE》'+renamedatestr

def command1():
    if liveing:
        renamedatestr = get_last_eft_title()
        if liveing['title'] == renamedatestr:
            print('名稱正確,無需修改')
            return 0
        updated_broadcast = update_broadcast(liveing['videoId'], renamedatestr, liveing['description'],20,EFT_game_title)
        print("Broadcast updated:", updated_broadcast)
    else:
        print("當前沒有進行中的直播")

def command3():
    renamedatestr = get_last_eft_title()
    start_time = (datetime.utcnow() + timedelta(minutes=3)).isoformat("T") + "Z"  # 設置為當前時間的3分鐘後
    create_broadcast(renamedatestr, "",start_time)

def command2():
    if liveing:
        addstr='\n'
        if input("是否加上時間戳(輸入任意字符代表確定)"):
            addstr =+ get_live_stream_time(live_time)
        while True:
            add = input('請輸入描述內容(一行),完成輸入ok')
            if add == "ok":
                print('內容為:\n'+addstr)
                if input("是否提交修改(輸入任意字符代表確定)"):
                    break
                else:
                    return 0
            else:
                addstr =+ add + '\n'
        update_broadcast(liveing['videoId'], liveing['title'], str(liveing['description']+addstr))
    else:
        print("當前沒有進行中的直播")


if __name__ == "__main__":
    logging.basicConfig(filename='app.log', level=logging.DEBUG, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.INFO)
    # logger.debug('調試日誌')
    # logger.info('信息日誌')
    # logger.warning('警告日誌')
    # logger.error('錯誤日誌')
    # logger.critical('嚴重錯誤日誌')

    # with open('url.json', 'r') as f:
    #     url = json.load(f)

    youtube = get_authenticated_service()
    channel_id = get_channel_id()
    liveing = get_live_stream(channel_id)
    if liveing:
        video_id = liveing['videoId']
        description = get_live_description(video_id)
        live_time = convert_timezone(get_live_stream_start_time(video_id))
    if liveing:
        print("URL:" + liveing)
        print("描述:" + description)
        print("開始時間:" + live_time)
        print("已直播:" + get_live_stream_time(live_time))
    else:
        print("當前沒有進行中的直播")
    commandlist = [command3,command1, command2]
    menu_str = '1:創建直播活動(EFT-PVE),2:獲取當前直播並按日期順序修改名稱(PVE),3:新增描述內容(EFT)'
    for i in menu_str.split(","):
        print(i)
    while True:
        command = int(input("輸入數字:"))
        if 0 < command < len(commandlist):
            commandlist[command-1]()
        elif command == len(commandlist)+1:
            for i in menu_str.split(","):
                print(i)
        else:
            print('沒有定義的操作')




    # print(get_last_eft_title())
    # with open('temp.json', 'r',encoding="utf-8") as f:
    #     temp = json.load(f)
    # itemlist = []
    # titlelist = []
    # for video in temp:
    #     snippet = video['snippet']
    #     out = {'title': snippet['title'],
    #         'videoId': video["id"]['videoId'],
    #         'description': snippet['description'],
    #         'liveBroadcastContent': snippet['liveBroadcastContent'],
    #         'publishTime': snippet["publishTime"],
    #         }
    #     itemlist.append(out)
    # for video in itemlist:
    #     titlelist.append(video['title'])
    # titlelist = sort_videos(titlelist)
    # for s in titlelist:
    #     print(s)