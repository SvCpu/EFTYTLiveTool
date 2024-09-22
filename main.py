# pip install google-auth-oauthlib google-auth-httplib2

import os
import google.auth.transport.requests
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from datetime import datetime, timezone
import requests

SCOPES = ['https://www.googleapis.com/auth/youtube.force-ssl']

# 如果修改範圍，刪除 token.json 文件
def get_authenticated_service():
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
        live_video = response['items'][0]
        live_link = f"https://www.youtube.com/watch?v={live_video['id']['videoId']}"
        return live_link
    else:
        return None

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

# 獲取直播經過的時間
def get_live_stream_duration(video_id):
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

# 創建直播活動
# title = "New Live Broadcast"
# description = "This is a test broadcast."
# start_time = "2024-09-22T15:00:00Z"
# end_time = "2024-09-22T16:00:00Z"
# broadcast = create_broadcast(title, description, start_time, end_time)
# print("Broadcast created:", broadcast)
def create_broadcast(title, description, start_time, end_time):
    request = youtube.liveBroadcasts().insert(
        part='snippet,status',
        body={
            'snippet': {
                'title': title,
                'description': description,
                'scheduledStartTime': start_time,
                'scheduledEndTime': end_time
            },
            'status': {
                'privacyStatus': 'public'
            }
        }
    )
    response = request.execute()
    return response

# 更新直播活動
    broadcast_id = broadcast['id']
    new_title = "Updated Live Broadcast Title"
    new_description = "This is an updated description."
    updated_broadcast = update_broadcast(broadcast_id, new_title, new_description)
    print("Broadcast updated:", updated_broadcast)
def update_broadcast(broadcast_id, new_title, new_description):
    request = youtube.liveBroadcasts().update(
        part='snippet',
        body={
            'id': broadcast_id,
            'snippet': {
                'title': new_title,
                'description': new_description
            }
        }
    )
    response = request.execute()
    return response

# 刪除直播活動
# delete_response = delete_broadcast(broadcast_id)
# print("Broadcast deleted:", delete_response)
def delete_broadcast(broadcast_id):
    request = youtube.liveBroadcasts().delete(
        id=broadcast_id
    )
    response = request.execute()
    return response

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
        return live_details
    else:
        return None

if __name__ == "__main__":
    youtube = get_authenticated_service()
    channel_id = get_channel_id()
    live_link = get_live_stream(channel_id)
    if live_link:
        video_id = live_link.split('=')[-1]
        description = get_live_description(video_id)
        live_time = get_live_stream_duration(video_id)
    print(live_link)
    if live_link:
        print(description)
        print(live_time)

