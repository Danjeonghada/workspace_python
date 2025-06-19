import pandas as pd
import requests
import time

# ✅ 디코딩된 서비스키
SERVICE_KEY = "lwBjmfhkrU4JaKRC0HAHPMzUxQCEzIy/Cisc/89UtKOtRUZJT/2dPhh8K5iFsaZDqfQ3czU57+pKbwxpI+J2Qw=="

def get_tm_by_dong(dong_name):
    url = "http://apis.data.go.kr/B552584/MsrstnInfoInqireSvc/getTMStdrCrdnt"
    params = {
        "serviceKey": SERVICE_KEY,
        "returnType": "json",
        "numOfRows": "100",
        "pageNo": "1",
        "umdName": dong_name
    }

    try:
        response = requests.get(url, params=params)
        data = response.json()
        items = data.get("response", {}).get("body", {}).get("items", [])
        if not items:
            return None, None
        # 대전광역시만 필터링
        filtered = [item for item in items if item.get("sidoName") == "대전광역시"]
        if not filtered:
            return None, None
        return filtered[0]["tmX"], filtered[0]["tmY"]
    except Exception as e:
        print(f"[❌] '{dong_name}' 요청 중 오류 발생: {e}")
        return None, None

def save_tm_coords_from_excel(input_path="xy_code_daejeon.xlsx", output_path="tm_coords_from_api.csv"):
    df = pd.read_excel(input_path)
    df['TM_X'] = None
    df['TM_Y'] = None

    for i, row in df.iterrows():
        dong = row['3단계']
        print(f"📍 요청 동: {dong}")
        tm_x, tm_y = get_tm_by_dong(dong)
        if tm_x and tm_y:
            df.at[i, 'TM_X'] = tm_x
            df.at[i, 'TM_Y'] = tm_y
            print(f"✅ TM 좌표: X={tm_x}, Y={tm_y}")
        else:
            print(f"[⚠️] '{dong}' TM 좌표 불러오기 실패")
        time.sleep(0.3)  # 너무 빠른 요청 방지

    df.to_csv(output_path, index=False, encoding="utf-8-sig")
    print(f"\n📁 TM 좌표 저장 완료 → {output_path}")

# ✅ 실행
if __name__ == "__main__":
    save_tm_coords_from_excel()
