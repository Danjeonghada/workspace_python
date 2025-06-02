import pandas as pd
from pyproj import Transformer

tm_cache = {}

# TM 좌표 변환
def wgs84_to_tm(lat, lon):
    transformer = Transformer.from_crs("epsg:4326", "epsg:2097", always_xy=True)
    return transformer.transform(lon, lat)

# 캐시 활용한 TM 좌표 변환
def get_tm_coords(lat, lon):
    key = (lat, lon)
    if key in tm_cache:
        return tm_cache[key]
    tm_x, tm_y = wgs84_to_tm(lat, lon)
    tm_cache[key] = (tm_x, tm_y)
    return tm_x, tm_y

# 엑셀에서 모든 동의 위경도 → TM 좌표 변환 후 저장
def save_all_tm_coords(excel_path="xy_code_daejeon.xlsx", output_csv="tm_coords.csv"):
    df = pd.read_excel(excel_path)

    # 결과 저장용 리스트
    results = []

    for _, row in df.iterrows():
        dong = row['3단계']
        lat = float(row['위도(초/100)'])
        lon = float(row['경도(초/100)'])
        tm_x, tm_y = get_tm_coords(lat, lon)

        results.append({
            "동": dong,
            "위도": lat,
            "경도": lon,
            "TM_X": tm_x,
            "TM_Y": tm_y
        })

    # 저장
    result_df = pd.DataFrame(results)
    result_df.to_csv(output_csv, index=False, encoding='utf-8-sig')
    print(f"✅ TM 좌표 변환 결과가 '{output_csv}' 파일에 저장되었습니다.")

# ✅ 실행 예시
if __name__ == "__main__":
    save_all_tm_coords()

