def day_of_year(day, month ,year):
  day_of_year = 0
  day_of_month = [0,31,28,31,30,31,30,31,31,30,31,30,31]

  if is_leap(year):
    day_of_month[2] = 29
  elif month == 2 and day == 29:
    return -1
  
  for i in range(month):
    day_of_year += day_of_month[i]
  day_of_year += day

  return day_of_year

def is_leap(year): return year % 4 == 0 and (year % 100 != 0 or year % 400 == 0)

def date_diff(first_cal,second_cal):
  date_first,month_first,year_first = [int(x) for x in first_cal.split('-')]
  date_second,month_second,year_second = [int(x) for x in second_cal.split('-')]
  day_of_first_year = day_of_year(date_first,month_first,year_first)
  day_of_second_year = day_of_year(date_second,month_second,year_second)

#------start -------#
usr_input = input("Enter Input: ").split(',')
if len(usr_input) != 2:
  print('Invalid')
  quit()

first_cal = usr_input[0]
second_cal = usr_input[2]

if len(first_cal.split('-')) != 3 or len(second_cal.split('-')) != 3:
  print('Invalid')
  quit()

date_diff(first_cal,second_cal)