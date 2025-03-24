# python 자료 구조 list(배열), dict(key:value), tuple(수정X), set(중복X)

# list 동적 배열, 타입과 사이즈가 자유로움
arr = [1, 2, 'pangsu', [3, 4], True]
print(arr[2]) # index로 접근
print(arr[4])
print(arr[3][0]) # arr 인덱스 3의 인덱스 0번째 value
print(arr[-1]) # 배열의 마지막 요소
print(arr[1:3]) # 슬라이스 1 인덱스 ~ 3-1 인덱스 까지
# 요소 추가
arr.append("추가")
print(arr)
# 요소 수정
arr[0] = "nick" # 이전 타입 무시됨.
# 요소 삭제
del arr[0] # 인덱스가 당겨짐.
print(arr)
arr2 = ["jack", "judy"]
# 병합
arr3 = arr + arr2
print(arr3);
# 반복
repeated = arr3 * 5
print(repeated)
print(len(repeated)) # len : length
