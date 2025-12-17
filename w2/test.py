def day_in_year(year):
  if is_leap(year):
    return 366
  return 365
def is_leap(year): return year % 4 == 0 and (year % 100 != 0 or year % 400 == 0)

date_diff = 0
for i in range(2000,2005):
  date_diff += day_in_year(i)
  print(date_diff)