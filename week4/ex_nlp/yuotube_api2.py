# pip install --upgrade google-api-python-client
from googleapiclient.discovery import build
api_key = 'AIzaSyCvDIfrEaiqBwesvsoryF1sHbF3dpZuU0U'
youtube = build('youtube', 'v3', developerKey=api_key)
video_id = 'PXYKL-kG9PM'
# 댓글 검색
request = youtube.commentThreads().list(
    part='snippet'
   ,videoId=video_id
   ,textFormat='plainText'
)
response = request.execute()
# 결과
for item in response['items']:
    comment = item['snippet']['topLevelComment']['snippet']
    print(f"작성자:{comment['authorDisplayName']}")
    print(f"댓글:{comment['textDisplay']}")
    print(f"좋아요:{comment['likeCount']}")
    print("-" * 30)
