def day_of_year(day, month, year):
  try:
    day = int(day)
    month = int(month)
    year = int(year)
  except (ValueError, TypeError):
    return 'Invalid'

  if year < 1:
    return 'Invalid'
  if month < 1 or month > 12:
    return 'Invalid'

  leap = is_leap(year)
  days_in_month = [0, 31, 29 if leap else 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]
  if day < 1 or day > days_in_month[month]:
    return 'Invalid'

  day_of_year = sum(days_in_month[:month]) + day
  return day_of_year

def is_leap(year):
  try:
    year = int(year)
  except (ValueError, TypeError):
    return False
  if year < 1:
    return False
  return year % 4 == 0 and (year % 100 != 0 or year % 400 == 0)


#------start -------#
usr_input = input("Enter a date : ").split('-')

if len(usr_input) == 3:
  day, month, year = [x for x in usr_input]
else:
  day = month = year = ''

result = day_of_year(day, month, year)
print("day of year:", result, end='')
print(' ,is_leap:', is_leap(year))
