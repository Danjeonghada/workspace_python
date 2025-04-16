# pip install --upgrade google-api-python-client
from googleapiclient.discovery import build
api_key = 'AIzaSyCvDIfrEaiqBwesvsoryF1sHbF3dpZuU0U'
youtube = build('youtube', 'v3', developerKey=api_key)
# 검색어 기반 영상 검색 search.list
# 비디오 정보 검색 videos.list
# 채널 정보 조회 channels.list
# 댓글 조회 commentThreads.list
# 구독자 목록 조회 subscriptions.list
# 채널 활동 내역 조회 activities.list


# 영상 검색
request = youtube.search().list(
    part='snippet'
   ,q='fc온라인 전술'
   ,type='video'
   ,maxResults=10
)
response = request.execute()
# 결과
for item in response['items']:
    print(f"제목:{item['snippet']['title']}")
    print(f"영상ID:{item['id']['videoId']}")
    print(f"게시자:{item['snippet']['channelTitle']}")
    print("-" * 30)
