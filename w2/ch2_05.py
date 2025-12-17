def gcd(a, b):
  while b:
      a, b = b, a % b
  return a

usr_input = input(" *** Linear Formula ***\nEnter x1 y1 x2 y2: ").split()

if len(usr_input) != 4:
  print("Invaild")
  quit()

try:
  x1 ,y1 ,x2 ,y2 = [int(x) for x in usr_input]
except:
  print("Invaild")
  quit()
print(f"({x1},{y1}) ==> ({x2},{y2})")

a = y2 - y1
b = x1 - x2
c = (x2*y1) - (x1*y2)

print(f"f1 ==> {a}x + {b}y + {c} = 0")

d = abs(gcd(a,gcd(b,c)))
a = int(a / d)
b = int(b / d)
c = int(c / d)

print(f"f2 ==> {a}x + {b}y + {c} = 0")

print(f"f3 ==> ",end='')

if a > 1 or a < -1: print(f"{abs(a)}",end='')
print("x ",end='')

if (a > 0 and b > 0) or (a < 0 and b < 0): print("+ ",end='')
else: print("- ",end='')

if b > 1 or b < -1: print(f"{abs(b)}",end='')
print("y ",end='')

if c != 0:
  if (c > 0 and a > 0) or (c < 0 and a < 0): print("+ ",end='')
  else: print("- ",end='')
  print(f"{abs(c)} ",end='')
  
print("= 0\n===== End of program =====")
