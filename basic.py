import re
import pytz
from datetime import datetime, timedelta, timezone

class description:
    def __init__(self):
        self.description = []
        self.tags = []
        self.timeline = []

# 解析日期字串並排序
# 注:此函數只可輸入一維列表, 只適用於規範的名稱
def sort_videos(video_list, start_index):
    parsed_videos = [(video, parse_date_string(video[start_index:])) for video in video_list]
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

# 解析描述字符串
def parse_description(descriptiontext):
    out_description = description()
    splits = descriptiontext.split('\n')
    if splits:
        for s in splits:
            if s.count('#') >0:
                tags = [word.strip('#') for word in s.split() if word.startswith('#')]
                tags = [item for item in tags if item != '']
                out_description.tags += tags
            elif has_time(s):
                out_description.timeline += [[time, text.strip()] for time, text in re.findall(r'(\d{1,2}:\d{2}:\d{2}|\d{2}:\d{2})\s*([^\d\n]+)', s)]
            else:
                out_description.description.append(s)
    else:
        out_description.description.append(descriptiontext)
    return out_description

def has_time(string):
    """
    檢查字符串是否包含HH:MM:SS或MM:SS格式中的時間
    """
    time_pattern = r'\b(\d{1,2}:\d{2}:\d{2}|\d{2}:\d{2})\b'
    return bool(re.search(time_pattern, string))

def get_live_stream_time(start_time):
    now = datetime.now(timezone.utc)
    duration = now - start_time
    return datetime.strptime(str(duration), '%H:%M:%S.%f').strftime('%H:%M:%S')


def convert_timezone(utc_time_str):
    utc_time = datetime.strptime(utc_time_str, "%Y-%m-%dT%H:%M:%SZ") # 解析 UTC 時間字串
    macau_tz = pytz.timezone("Asia/Macau") # 設定時區
    macau_time = utc_time.replace(tzinfo=pytz.utc).astimezone(macau_tz) # 將 UTC 時間轉換為澳門時間
    return macau_time

# 通過正則表達式來檢查字串符是否爲 YouTube PlayList ID
def is_playlist_id(string):
    pattern = re.compile(r'^[a-zA-Z0-9_-]{34}$')
    return bool(pattern.match(string))

def id_to_link(id):
    return f"https://www.youtube.com/watch?v={id}"

# 獲取json嵌套數據, 否則返回預設值
def get_nested(data, keys, default=None):
    """
    get_nested(data, ["user", "details", "address", "city"], "Unknown")
    """
    if not keys:
        return data
    if isinstance(data, dict):
        return get_nested(data.get(keys[0], default), keys[1:], default)
    return default
