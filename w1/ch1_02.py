digit = input("Enter digits : ")
if not digit.isdigit() or int(digit) < 2:
  print("Invalid Input")
  quit()

max = 0
digit = int(digit)
high = 10 ** digit - 1
low = 10 ** (digit - 1)

for a in range(high, low - 1, -1):
  if a * high < max:
    break
  for b in range(a, low - 1, -1):
    mult = a * b
    if mult < max:
      break
    s = str(mult)
    if s == s[::-1]:
      max = mult
      break

print(max)
