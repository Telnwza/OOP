usr_input = input("Sum from 1 to : ")

try:
  num = int(usr_input)
except:
  print("Input Error")
  quit()

if num < 1: 
  print("Input Error")
  quit()

sum = 0
for n in range(1,num+1):
  sum+=n
print(f"Sum from 1 to {num} is {sum}")