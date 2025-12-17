input_usr = input("Enter your input : ").split()

if len(input_usr) != 4:
  print("Invalid Input")
  quit()

for i in range(4):
  if not input_usr[i].isnumeric():
    print("Invalid Input")
    quit()

hr_in,mi_in,hr_out,mi_out = [int(e) for e in input_usr]

if hr_in >= 23 or hr_in < 7 or hr_out >= 23 or hr_out < 7:
  print("Invalid Input")
  quit()

if mi_in < 0 or mi_in >= 60 or mi_out < 0 or mi_out >= 60:
  print("Invalid Input")
  quit()

mi_in += hr_in*60
mi_out += hr_out*60

total_mi = mi_out - mi_in

if total_mi <= 0:
  print("Invalid Input")
  quit()

total_hr = int((total_mi/60)+0.999999)

if total_mi <= 15:
  price = 0
elif total_mi <= 180:
  price = total_hr*10
elif total_mi <= 360:
  price = 30 + (total_hr-3)*20
else:
  price = 200

print(price)