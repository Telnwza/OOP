num = input("Input : ")
if not num.isdigit():
  print("Invalid Input")
  quit()
num = int(num)
for i in range(num):
  print(" "*(num-i),end="")
  print("#"*(i+1))