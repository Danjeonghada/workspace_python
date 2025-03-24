# 중복을 허용 하지 않는 set
# {}
fruits_set = {"apple","banana","cherry"}
# 요소 추가
fruits_set.add("orange")
fruits_set.add("orange")
print(fruits_set)  # 중복을 허용 하지 않기 때문에 orange 1개
# 여러 개 추가
fruits_set.update(["mango", "grape"])
# 집합 연산
set1 = {"apple", "melon"}
intersection = fruits_set & set1  # 교집합
union = fruits_set | set1         # 합집합
minus = fruits_set - set1         # 차집합
print("교집합", intersection)
print("합집합", union)
print("차집합", minus)