def update_record(dict_rec,id,property,value):
  if id not in dict_rec:
    dict_rec[id] = {}
  if property != 'tracks' and value != "''":
    dict_rec[id][property] = value
  elif property == 'tracks' and not 'tracks' in dict_rec[id] and value != "''":
    track_list = []
    track_list.append(value)
    dict_rec[id][property] = track_list
  elif property == 'tracks' and 'tracks' in dict_rec[id] and value != "''":
    track_list = list(dict_rec[id][property])
    track_list.append(value)
    dict_rec[id][property] = track_list
  elif value == "''":
    if property in dict_rec[id]:
        del dict_rec[id][property]
    else:
      print("Invalid")
      quit()
  print(dict_rec)

#-------start----------#
record_collection = {}
usr_input = input("Input : ")
usr_input = (usr_input).split('|')
if len(usr_input) != 4:
  print("Invalid")
  quit()

dict_rec,id,property,value = [x for x in usr_input]
id = id.replace(" ", "")
property = property.replace(" ", "")
value = value[1:]
dict_rec = eval(dict_rec)

if not type(dict_rec) is dict or not id.isnumeric():
  print("Invalid")
  quit()
if int(id) < 1:
  print("Invalid")
  quit()
if not (property == 'artist' or property == 'albumTitle' or property == 'tracks'):
  print("Invalid")
  quit()

update_record(dict_rec,id,property,value)