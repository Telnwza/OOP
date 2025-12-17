data = input("Input : ")
if not data.isdigit():
  print("Output : Invalid Input")
  quit()
data = int(data)
if data > 9:
  print("Output : Invalid Input")
  quit()
sum = 0
add = 0
for i in range(4):
  add = add*10+data
  sum += add
print("Output :",sum)