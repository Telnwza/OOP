a = [1,2,3,4]
b = [5,3,4]
c = b

print(c)

b = [1,5,2]

print(c)

number_list = [x for x in range (20) if x % 2 == 0]
print(number_list)

number_list = ["tree" if x == 3 else x for x in range (20) ]
print(number_list)

x = [int(e) for e in input().split]