import pandas as pd
import math

def dfs_xy_conv(lat, lon):
    RE = 6371.00877    # 지구 반경(km)
    GRID = 5.0         # 격자 간격(km)
    SLAT1 = 30.0       # 표준위도1
    SLAT2 = 60.0       # 표준위도2
    OLON = 126.0       # 기준점 경도
    OLAT = 38.0        # 기준점 위도
    XO = 43            # 기준점 X좌표
    YO = 136           # 기준점 Y좌표

    DEGRAD = math.pi / 180.0

    re = RE / GRID
    slat1 = SLAT1 * DEGRAD
    slat2 = SLAT2 * DEGRAD
    olon = OLON * DEGRAD
    olat = OLAT * DEGRAD

    sn = math.tan(math.pi * 0.25 + slat2 * 0.5) / math.tan(math.pi * 0.25 + slat1 * 0.5)
    sn = math.log(math.cos(slat1) / math.cos(slat2)) / math.log(sn)
    sf = math.tan(math.pi * 0.25 + slat1 * 0.5)
    sf = math.pow(sf, sn) * math.cos(slat1) / sn
    ro = math.tan(math.pi * 0.25 + olat * 0.5)
    ro = re * sf / math.pow(ro, sn)
    ra = math.tan(math.pi * 0.25 + lat * DEGRAD * 0.5)
    ra = re * sf / math.pow(ra, sn)
    theta = lon * DEGRAD - olon
    if theta > math.pi:
        theta -= 2.0 * math.pi
    if theta < -math.pi:
        theta += 2.0 * math.pi
    theta *= sn
    x = (ra * math.sin(theta)) + XO + 0.5
    y = (ro - ra * math.cos(theta)) + YO + 0.5
    return int(x), int(y)


# 1. 미등록 동 파일 읽기
df_missing = pd.read_csv('미존재_동목록_좌표.csv')  # 동이름, 위도, 경도

# 2. 격자 X, Y 변환
def get_grid(row):
    try:
        if pd.notnull(row['위도']) and pd.notnull(row['경도']):
            x, y = dfs_xy_conv(float(row['위도']), float(row['경도']))
            return pd.Series({'격자X': x, '격자Y': y})
        else:
            return pd.Series({'격자X': None, '격자Y': None})
    except:
        return pd.Series({'격자X': None, '격자Y': None})

df_missing[['격자X', '격자Y']] = df_missing.apply(get_grid, axis=1)

# 3. 기존 좌표목록.csv 읽기
df_coords = pd.read_csv('좌표목록.csv')

# 4. 컬럼명 맞추기/통일
# 기존 좌표목록에 '동이름', '격자X', '격자Y' 컬럼이 없다면 맞게 변경
# 예시: '3단계' → '동이름', '격자 X' → '격자X', '격자 Y' → '격자Y'
df_coords = df_coords.rename(columns={
    '3단계': '동이름',
    '격자 X': '격자X',
    '격자 Y': '격자Y'
})

# 5. 두 데이터 합치기 (아래 컬럼이 있으면 좋음)
df_final = pd.concat([df_coords, df_missing], ignore_index=True)

# 6. 원하는 컬럼만 선택해서 저장 (위도/경도는 제외!)
columns_to_save = ['동이름', '격자X', '격자Y']  # 추가 컬럼 필요하면 여기에
df_final[columns_to_save].to_csv('좌표목록_최종.csv', index=False, encoding='utf-8-sig')

print("좌표목록_최종.csv 저장 완료!")
