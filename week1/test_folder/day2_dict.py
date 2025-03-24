# 딕셔너리 dict
test = {}      # 비어 있는 dict
test2 = set()  # 비어 있는 set
person = {"name" : "pangsu", "age" : 10}
print(person, type(person))
print(person["name"])
# 수정
person["age"] = 11
# 추가
person["city"] = "NewYork"
person["hobby"] = ["참치잡기", "노래"]
print(person)
# 삭제
del person["city"]
# key 가져오기
keys = person.keys()
print(keys)
for key in person.keys():
    print(key, person[key])
# value 가져오기
print(person.values())
for v in person.values():
    print(v)
for k, v in person.items():
    print(k, v)