from urllib.parse import urlparse, parse_qs
from googleapiclient.discovery import build
from wordcloud import WordCloud
api_key = '키'
youtube = build('youtube', 'v3', developerKey=api_key)

def extract_id(url):
    """
    :param url: youtube URL
    :return: youtube video id
    """
    # url을 구성 요소별로 쪼갬
    parsed_url = urlparse(url)
    domain = parsed_url.netloc.replace("www.","").replace("m.","")
    if domain == 'youtu.be':
        return parsed_url.path.lstrip("/")
    if domain == 'youtube.com':
        # 쿼리 문자열을 딕셔너리로 바꿔줌
        query_params = parse_qs(parsed_url.query)
        return query_params.get('v', [None])[0]
    return None

def get_comments(video_id, max_results=100):
    """
    :param video_id: youtube video id
    :param max_results: 최대 수집 댓글 수
    :return: 댓글 배열
    """
    comments = []
    next_page_token = None
    while len(comments) < max_results:
        request = youtube.commentThreads().list(
              part='snippet'
            , videoId=video_id
            , maxResults=min(100, max_results - len(comments))
            , pageToken=next_page_token
            , textFormat='plainText'
        )
        response = request.execute()
        for item in response['items']:
            comment = item['snippet']['topLevelComment']['snippet']
            comment_text = comment['textDisplay']
            like_count = comment['likeCount']
            comments.append({"comment": comment_text
                           , "like_count": like_count})
        next_page_token = response.get('nextPageToken')
        if not next_page_token:
            break
    return comments

def fn_wordcloud(fileNm, comments):
    comments_text = ' '.join(comments['comment'].tolist())
    wordcloud = WordCloud(width=800, height=400, background_color='white'
                          , font_path='../../dataset/NanumGothicBold.ttf').generate(comments_text)
    img_path = f'static/img/{fileNm}.png'
    wordcloud.to_file(img_path)
    return img_path

if __name__ == '__main__':
    urls = ['https://www.youtube.com/watch?v=fh_hDo6imko&t=93s'
           ,'https://youtu.be/fh_hDo6imko?si=kbS8W5G-dy3E2I8-'
           ,'https://m.youtube.com/watch?v=fh_hDo6imko&t=93s']
    for url in urls:
        print(f"{url} -> {extract_id(url)}")

