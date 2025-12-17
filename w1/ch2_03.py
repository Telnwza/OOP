input_usr = input("Enter your input : ")
if (not (input_usr.startswith('[') and input_usr.endswith(']')) or (len(input_usr) <= 2)):
  print("Invalid Input")
  quit()

input_usr = input_usr[1:-1]
data = input_usr.split(',')

if len(data) < 2:
  print("Invalid Input")
  quit()

for i in data:
  if not i.isdigit() and (i.isalpha() or i[1].isalpha()):
    print("Invalid Input")
    quit()

for i in range(len(data)):
  data[i] = int(data[i])

data = sorted(data)

left = data[0] * data[1]
right = data[-1] * data[-2]

if left > right:
  print(left)
else:
  print(right)