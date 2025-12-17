usr_input = input(" *** Multiplicaiton table ***\nEnter an integer(n) : ")
try:
  num = int(usr_input)
except:
  print("Invaild")
  quit()
if num > 50 or num < 1:
  print("Invaild")
  quit()
for i in range(1,13):
  print(f"{num:>2} x {i:<2} ={num*i:>4}")