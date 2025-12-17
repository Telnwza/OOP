usr_input = input("Input : ").split('|')

if len(usr_input) < 4 or (len(usr_input) > 4 and len(usr_input) % 3 != 1):
  print("Invalid")
  quit()

try:
  subject_score = dict(eval(usr_input[0][:-1]))

  for st_id, sj_dict in subject_score.items():
    tmp_id = int(st_id)
    if tmp_id < 0: quit()
    if not isinstance(sj_dict, dict): quit()
    for sj, sc in sj_dict.items():
      if not isinstance(sc, (int, float)): quit()
      if sc < 0: quit()

  for index, data in enumerate(usr_input):
    if index == 0:  # dict
      continue
    elif index % 3 == 1:  # id
      usr_input[index] = int(data[1:])
      if usr_input[index] < 0:
        quit()
    elif index % 3 == 2:  # subject
      if not (usr_input[index].startswith(" '") and usr_input[index].endswith("' ")) or len(usr_input[index][2:-2]) < 1: quit()
      usr_input[index] = (data[2:-2])
    elif index % 3 == 0:  # score
      if '.' not in data:
        usr_input[index] = int(data[1:])
      else:
        usr_input[index] = float(data[1:])
      if usr_input[index] < 0:
        quit()
except:
  print("Invalid")
  quit()

for index in range(1, len(usr_input), 3):
  id = str(usr_input[index])
  subject = usr_input[index + 1]
  score = usr_input[index + 2]
  if id not in subject_score:
    subject_score[id] = {}
  subject_score[id][subject] = score

print(subject_score, end='')


avg_score = {}
for sid, subjects in subject_score.items():
  total_sum = 0
  times = 0
  for value in subjects.values():
    total_sum += float(value)
    times += 1
  total_sum = total_sum / times
  avg_score[sid] = f"{total_sum:.2f}"

print(", Average score:", avg_score)