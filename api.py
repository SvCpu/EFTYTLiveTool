import time
from basic import *

class youtubeapi:
    def __init__(self,youtube, logger) -> None:
        self.youtube = youtube
        self.logger = logger
    # 獲取頻道 ID
    # Api usage 1 time
    def get_channel_id(self):
        request = self.youtube.channels().list(
            part='id',
            mine=True
        )
        response = request.execute()
        if 'items' in response and len(response['items']) > 0:
            return response['items'][0]['id']
        else:
            return None

    # 獲取正在直播的鏈接
    # Api usage 1 time
    def get_live_stream(self, channel_id):
        request = self.youtube.search().list(
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

    # 獲取頻道直播影片列表前10部的直播影片(非排名)
    # Api usage 1 time
    def get_top_live_videos(self,channel_id='', maxResults=10):
        if channel_id == '':
            channel_id = self.get_channel_id()
        request = self.youtube.search().list(
            part='snippet',
            channelId=channel_id,
            eventType='completed',
            type='video',
            maxResults=maxResults,
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

    # 獲取直播描述
    # Api usage 1 time
    def get_live_description(self,video_id):
        request = self.youtube.videos().list(
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
    # Api usage 1 time
    def get_video_details(self, video_id):
        request = self.youtube.videos().list(
            part="snippet",
            id=video_id
        )
        response = request.execute()
        return response.get('items', [])

    # 獲取直播開始的時間
    # Api usage 1 time
    def get_live_stream_start_time(self, video_id):
        request = self.youtube.videos().list(
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
    # Api usage 1 time
    def update_live_description(self, video_id, new_description):
        request = self.youtube.videos().update(
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

    # 將指定影片加入到播放清單中
    # Api usage 1 time
    def add_to_playlist(self, id,playlistid):
        playlistsaddrequest = self.youtube.playlistItems().insert(
            part="snippet",
            body={
                "snippet": {
                    "playlistId": playlistid,
                    "resourceId": {
                        "kind": "youtube#video",
                        "videoId": id
                    }
                }
            }
        )
        try:
            playlistsaddrequest.execute()
        except Exception as e:
            self.logger.error('An error occurred while sending the request to add video '+id+' to playlist '+playlistid+',error info is:'+str(e))
        else:
            self.logger.info('Request to add video '+id+' to playlist '+playlistid+' has been sent')

    # 創建直播
    # Api usage 3~4 time
    # title = "New Live Broadcast"
    # description = "This is a test broadcast."
    # start_time = "2024-09-22T15:00:00Z"
    # end_time = "2024-09-22T16:00:00Z"
    # create_broadcast(title, description, start_time, end_time,playlists=['playlistid1','playlistid2'],categoryId='20',gameTitle='EFT')
    def create_broadcast(self, title, description, start_time, end_time='',playlists=[],categoryId='',gameTitle=''):
        requestbody = {
                'snippet': {
                    'title': title,
                    'description': description,
                    'scheduledStartTime': start_time
                },
                'status': {
                    'privacyStatus': 'public',
                    "selfDeclaredMadeForKids": False
                },
                'contentDetails':{
                    'monitorStream':{
                        'enableMonitorStream':False
                    },
                    'enableAutoStop':True
                }
            }
        if end_time:
            requestbody["snippet"]['scheduledEndTime'] = end_time
        request = self.youtube.liveBroadcasts().insert(
            part='snippet,status,contentDetails',
            body=requestbody
        )
        try:
            broadcast_response = request.execute()
        except Exception as e:
            self.logger.error('Broadcast '+title+' create request error,error info is '+str(e))
            print('發送請求時出錯, 請查詢日誌')
        else:
            broadcast_id = broadcast_response["id"]
            self.logger.info('Broadcast '+title+' create request Sent,start time is '+start_time)
        if broadcast_id:
            self.logger.info("The live broadcast with activity ID "+broadcast_id+" has been created")
            print('ID為'+broadcast_id+'的直播已建立')
            print('直播聊天室ID:'+broadcast_response['snippet']['liveChatId'])
            input('為避免浪費API查詢額度, 請確定直播已傳送到YouTube後按下任意鍵繼續')
            print('查詢活動狀態的直播流並綁定到直播活動')
            streamId = ''
            if playlists:
                for playlist in playlists:
                    if is_playlist_id(playlist):
                        self.add_to_playlist(broadcast_id,playlist)
            for _ in range(3):
                # 獲取直播流信息
                streams_request = self.youtube.liveStreams().list (
                    part='snippet,contentDetails,status',
                    mine=True
                )
                self.logger.info('Query live stream status information')
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
                bind_request = self.youtube.liveBroadcasts().bind(
                    part='id,contentDetails',
                    id=broadcast_id,
                    streamId=streamId
                )
                try:
                    bind_response = bind_request.execute()
                except Exception as e:
                    self.logger.error('Live Streaming '+streamId+' Bind to Live Event '+broadcast_id+' Request Sent,error info is '+str(e))
                else:
                    self.logger.info('Live Streaming '+streamId+' Bind to Live Event '+broadcast_id+' Request Sent')
                    print('直播流'+streamId+'已與直播活動'+broadcast_id+'繫結')
                    startlive_request=self.youtube.liveBroadcasts().transition(
                        part = "snippet,status",
                        broadcastStatus="live",
                        id=broadcast_id
                    )
                    self.logger.info('Live broadcast '+broadcast_id+' Start Request Sent')
                    startlive_request.execute()
                    print('直播'+broadcast_id+'已設置爲活動狀態')
                    if categoryId:
                        gameTitlelog = ''
                        categoryIdrequestbody = {
                            'id': broadcast_id,
                            'snippet': {
                                'title':title,
                                'description': description,
                                'defaultAudioLanguage':'zh-Hant',
                                'categoryId' : str(categoryId)
                            }
                        }
                        if gameTitle:
                            categoryIdrequestbody['snippet']['gameTitle'] = gameTitle
                            gameTitlelog = ' and game title is '+gameTitle
                        categoryIdrequest = self.youtube.videos().update(
                        part='snippet',
                        body=categoryIdrequestbody
                            )
                        print(categoryIdrequestbody)
                        categoryIdrequest.execute()
                        self.logger.info('request Broadcast '+ broadcast_id + 'CategoryId chage of '+str(categoryId)+ gameTitlelog)
            else:
                print('沒有活動狀態的直播流')
                bind_response = None
        return (broadcast_response, bind_response)

    # 更新直播活動
    # Api usage 1 time
    def update_broadcast(self, broadcast_id, title, description,CategoryId='',GameTitle='',selfDeclaredMadeForKids=None):
        requestbody = {
                'id': broadcast_id,
                'snippet': {
                    'title': title,
                    'description': description
                }
            }
        if CategoryId:
            requestbody['snippet']['categoryId'] = CategoryId
        if GameTitle:
            requestbody['snippet']['gameTitle'] = GameTitle
        if selfDeclaredMadeForKids != None:
            requestbody['status']['selfDeclaredMadeForKids'] = selfDeclaredMadeForKids
            requestpart = 'snippet,status'
        else:
            requestpart = 'snippet'
        request = self.youtube.liveBroadcasts().update(
            part=requestpart,
            body=requestbody
        )
        response = request.execute()
        self.logger.info('request Broadcast '+ broadcast_id + ' chage of '+title+ ' '+description)
        return response

    # 刪除直播活動
    # Api usage 1 time
    # delete_response = delete_broadcast(broadcast_id)
    def delete_broadcast(self, broadcast_id):
        request = self.youtube.liveBroadcasts().delete(
            id=broadcast_id
        )
        try:
            request.execute()
        except Exception as e:
            self.logger.error('Broadcast '+ broadcast_id + ' del request error with:'+str(e))
        else:
            self.logger.info('Broadcast '+ broadcast_id + ' del request Sent')

    # 獲取直播聊天信息
    # Api usage 1 time
    # live_chat_id = "YOUR_LIVE_CHAT_ID"
    # chat_messages = get_live_chat_messages(live_chat_id)
    # for message in chat_messages['items']:
    #     print(f"{message['authorDetails']['displayName']}: {message['snippet']['displayMessage']}")
    def get_live_chat_messages(self, live_chat_id):
        request = self.youtube.liveChatMessages().list(
            liveChatId=live_chat_id,
            part='snippet,authorDetails'
        )
        response = request.execute()
        return response

    # 獲取live_chat_id
    # Api usage 1 time
    def get_live_chat_id(self, video_id):
        request = self.youtube.videos().list(
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
    # Api usage 1 time
    def get_live_stream_details(self, video_id):
        request = self.youtube.videos().list(
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

    # 判斷指定 id 的資源是否爲直播
    # Api usage 1 time
    def is_video_live(self, video_id):
        request = self.youtube.videos().list(
            part='snippet,liveStreamingDetails',
            id=video_id
        )
        response = request.execute()
        if 'items' in response and len(response['items']) > 0:
            live_broadcast_content = response['items'][0]['snippet']['liveBroadcastContent']
            return live_broadcast_content
        else:
            return False

    # 獲取指定播放列表中最後新增的視頻
    # Api usage 1 time
    def get_latest_video_title(self, playlist_id):
        request = self.youtube.playlistItems().list(
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
        
    # 獲取頻道最新的十條影片(直播)
    # 並根據最新的影片來生成最新的時間序列字符
    # 例.20240921-1
    # 注:此函數只適用於規範的名稱 《逃离塔科夫PVE》+ 時間序列
    # Api usage 1 time
    def get_last_eft_title(self):
        renamedatestr = ''
        top_live = self.get_top_live_videos()
        titlelist = []
        for video in top_live:
            titlelist.append(video['title'])
        titlelist = sort_videos(titlelist,10)
        now = datetime.now()
        lastlive = parse_date_string(titlelist[0][10:])
        nowtimestr = str(now.year)+now.strftime("%m")+now.strftime("%d")
        if (lastlive["year"]+lastlive['month']+lastlive['day']) == nowtimestr:
            renamedatestr = nowtimestr+'-'+str(lastlive["serial"]+1)
        else:
            renamedatestr = nowtimestr+"-1"
        return '《逃离塔科夫PVE》'+renamedatestr