# 1. formatting
nm = "pangsu"
age = 10

format1 = "My name is %s and I am %d years old." %(nm, age)

num = 123.456789
format2 = "The number is %.2f" % num
percent = 98.5
format3 = "Success! %.1f%%" % percent
print(format1)
print(format2)
print(format3)
# 2. str.format() 매서드 사용
format4 = "My name is {} and I am {} years old.".format(nm, age)
format5 = "number is {:.2f}".format(num)
print(format4)
print(format5)
# 3. python 3.6 부터 사용 가능
format6 = f"My name is {nm} and I am {age} years old."
format7 = f"number is {num:.2f}"
print(format6)
print(format7)