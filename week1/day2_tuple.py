# 튜플 : 수정이 안됨.
from week1.day1_list import repeated

nums = (1, 2, 3, 4)
print(nums[1])
print(nums[-1])  # 사용은 배열과 동일 단 수정이 안됨.
nums2 = (5, 6)
# 병합, 반복 가능
nums3 = nums + nums2
print(nums3)
repeated = nums3 * 10
print(repeated)
for v in nums3:
    print(v)