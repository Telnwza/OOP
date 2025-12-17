def add_score(subject_score, subject, score):
  subject_score[subject] = score
  return subject_score

def calc_average_score(dic):
  total = 0
  for value in dic.values():
    total += value
  avg = total / len(dic)
  return f"{avg:.2f}"

#----start----#
usr_input = input("Input : ").split('|')

if len(usr_input) != 3:
  print("invalid")
  quit()

subject_score_str, subject_str, score_str = [x for x in usr_input]

try:
  if '.' not in score_str:
    score = int(score_str[1:])
  else:
    score = float(score_str[1:])

  subject_score = dict(eval(subject_score_str[:-1]))
except:
  print("{}, Average score: 0.00")
  quit()

if not (subject_str.startswith(" '") and subject_str.endswith("' ")) or len(subject_str[2:-2]) < 1:
  print("{}, Average score: 0.00")
  quit()
subject = subject_str[2:-2]

subject_score = add_score(subject_score, subject, score)

for value in subject_score.values():
  if not isinstance(value, (int, float)):
    print("{}, Average score: 0.00")
    quit()
  if value < 0 or value > 100:
    print("{}, Average score: 0.00")
    quit()

print(subject_score, end='')
print(f", Average score: {calc_average_score(subject_score)}")
