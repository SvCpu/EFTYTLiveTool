from basic import *
from api import youtubeapi
EFT_game_title = 'escapefromtarkov'
# 主類
# 通過繼承主類編寫操作
# self.api 已初始化的youtubeapi類, 參考api.py
# self.logger 主程序的logger, 可調用logger.info()輸出日誌
# self.liveing 憑證賬戶正在直播的資訊
# self.channel_id 憑證賬戶頻道id
class Command(object):
    inited = False
    singleton = False # 表示函數只能在一個實例裏面運行一次
    def init(self, youtubeapi: youtubeapi, logger, liveing, channel_id: str,data:dict):
        self.name = ''
        self.description = ''
        self.api = youtubeapi
        self.logger = logger
        self.liveing = liveing
        self.channel_id = channel_id
        self.version = ''
        self.author = ''
        self.data = data
        self.inited = True

class Create_live_event_eftpve(Command):
    def __init__(self):
        self.name = "創建直播活動(EFT-PVE)"
        self.author = 'SvCpu'

    def main(self):
        renamedatestr = self.api.get_last_eft_title()
        start_time = (datetime.utcnow() + timedelta(minutes=3)).isoformat("T") + "Z"  # 設置為當前時間的3分鐘後
        pve_playlist = self.data['url']['playlistID']['EFT-PVE']
        pve_playlist = get_nested(self.data['url'],['playlistID', 'EFT-PVE'])
        self.api.create_broadcast(renamedatestr, "#escapefromtarkov #EFT",start_time,playlists=[pve_playlist],categoryId=20,gameTitle=EFT_game_title)


class fix_liveing_name(Command):
    def __init__(self):
        self.name = "獲取當前直播並按日期順序修改名稱(EFT-PVE)"
        self.author = 'SvCpu'

    def main(self):
        if self.liveing:
            renamedatestr = self.api.get_last_eft_title()
            if self.liveing['title'] == renamedatestr:
                print('名稱正確,無需修改')
                return 0
            updated_broadcast = self.api.update_broadcast(
                self.liveing['videoId'], renamedatestr, self.liveing['description'], 20, EFT_game_title)
            print("Broadcast updated:", updated_broadcast)
        else:
            print("當前沒有進行中的直播")


class chage_liveing_description_with_eftlive(Command):
    def __init__(self):
        self.name = "獲取當前直播並新增描述內容"
        self.author = 'SvCpu'

    def main(self):
        if self.inited:
            if self.liveing:
                addstr = '\n'
                if input("是否加上時間戳(輸入任意字符代表確定)"):
                    addstr += str(get_live_stream_time(self.data['live_time']))
                while True:
                    add = input('請輸入描述內容(一行),完成輸入ok')
                    if add == "ok":
                        print('內容為:\n'+addstr)
                        if input("是否提交修改(輸入任意字符代表確定)"):
                            break
                        else:
                            return 0
                    else:
                        addstr += add + '\n'
                self.api.update_broadcast(self.liveing['videoId'], self.liveing['title'], str(
                    self.liveing['description']+addstr))
            else:
                print("當前沒有進行中的直播")
        else:
            print('not init')
