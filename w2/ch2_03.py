usr_input = input(" *** even integer summation from 1 to n ***\nEnter an integer(n) : ")

try:
  num = int(usr_input)
except:
  print("Invaild")
  quit()
if num < 2:
  print("Invaild")
  quit()

print("Summation => ",end='')
plus = '2'
sum = 2
for i in range(4,num+1,2):
  plus+='+'
  plus+=str(i)
  sum+=i
print(plus,"=",sum)
