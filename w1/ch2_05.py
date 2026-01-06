print(" *** ID card ****")
data = input("Enter your student_ID firstname nickname : ").split()
if len(data) != 3:
  print("Invaid input")
  quit()

std_id = data[0]
std_first_name = data[1]
std_nick_name = data[2]

print('----------------------------------')
print('| »-(¯`·.·´¯)->CARD<-(¯`·.·´¯)-« |')
print('|                                |')
print(f'| {std_first_name:<15}{std_id:>15} |')
print(f'|{std_nick_name:^32}|')
print('|                                |')
print('| (-.-)Zzz....           (╯︵╰,) |')
print('----------------------------------')