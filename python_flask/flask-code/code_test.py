import requests

# data = {"COMM_CD":"JB10"
#        ,"COMM_NM":"IT"
#        ,"COMM_PARENT":"JB00"}
#
# res = requests.post("http://localhost:5000/codes", json=data)
# print("post 응답:", res.json())

data = {"COMM_NM":"DB"}
res = requests.put("http://localhost:5000/codes/JB10", json=data)
print("post 응답:", res.json())

data = {"COMM_CD":"JB10"}
res = requests.delete("http://localhost:5000/codes/JB10", json=data)
print("delete 응답:", res.json())