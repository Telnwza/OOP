data_list = input("Input : ").split()
if len(data_list) == 0 or len(data_list) > 10:
  print("Invalid Input")
  quit()
for i in data_list:
  if len(i) != 1 or not i.isdecimal():
    print("Invalid Input")
    quit()
data_list.sort()
if all(num == "0" for num in data_list):
  print("Invalid Input")
  quit()
for i in range(len(data_list)):
  if data_list[i] != "0":
    data_list[0], data_list[i] = data_list[i], data_list[0]
    break
for num in data_list:
  print(num, end='')
