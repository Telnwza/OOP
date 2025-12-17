def day_of_year(day, month ,year):
  day_of_year = 0
  if month > 12 or month < 1:
    print('Invalid')
    quit()
  if day > day_of_month[month] or day < 1:
    print('Invalid')
    quit()

  if is_leap(year):
    day_of_month[2] = 29
  elif month == 2 and day == 29:
    print('Invalid')
    quit()
  
  for i in range(month):
    day_of_year += day_of_month[i]
  day_of_year += day

  return day_of_year

def is_leap(year): return year % 4 == 0 and (year % 100 != 0 or year % 400 == 0)

def day_in_year(year):
  if is_leap(year):
    return 366
  return 365

def date_diff(first_cal,second_cal):
  first_cal = first_cal.replace(" ", "")
  second_cal = second_cal.replace(" ", "")

  for x in first_cal.split('-'):
    if not x.isnumeric():
      print('Invalid')
      quit()
  for x in second_cal.split('-'):
    if not x.isnumeric():
      print(x)
      print('Invalid')
      quit()
  
  date_first,month_first,year_first = [int(x) for x in first_cal.split('-')]
  date_second,month_second,year_second = [int(x) for x in second_cal.split('-')]
  day_of_first_year = day_of_year(date_first,month_first,year_first)
  day_of_second_year = day_of_year(date_second,month_second,year_second)
  if year_first > year_second :
    min_year = year_second
    more_year = year_first
    day_more = day_of_first_year
    day_less = day_of_second_year
  else:
    min_year = year_first
    more_year = year_second
    day_less = day_of_first_year
    day_more = day_of_second_year
  date_diff = 0
  for year in range(min_year,more_year):
    date_diff += day_in_year(year)
  date_diff += day_more - day_less
  return date_diff + 1

#------start -------#
day_of_month = [0,31,28,31,30,31,30,31,31,30,31,30,31]
usr_input = input("Enter Input: ").split(',')
if len(usr_input) != 2:
  print('Invalid')
  quit()

first_cal = usr_input[0]
second_cal = usr_input[1]

if len(first_cal.split('-')) != 3 or len(second_cal.split('-')) != 3:
  print('Invalid')
  quit()

print(date_diff(first_cal,second_cal))