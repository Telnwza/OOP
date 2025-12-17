a = 10
b = 10
c = [1,'a',2.5]
d = c
print(id(a))
print(id(b))
print(id(c))

b = 20
c[2] = 5.5
d[0] = 2 #เปลี่ยนค่าของตัวที่ชี้ immutable ทำให้ c เปลี่ยนไปด้วย ทำให้ c กลายเป็นกึ่งๆ gobal เพราะ d ไปชี้ pointer ค่าตัวเดียวกันกับ c


print(id(a))
print(id(b)) #change value เพราะเป็น immutable และไปสร้าง place holder ใหม่ที่ชี้ไปที่ค่่าใหม่ 
print(id(c)) #id no change > no value change 
print(c[0]) #c[0] เปลี่ยนตาม d[0] เพราะ list เป็น mutable ใช้ place holder เดิม แล้วไปเปลี่ยนค่าที่ place holder ชี้ เลยทำให้ค่าที่ตัวแปรที่ชี้ pointer เดียวกันเปลี่ยนไปด้วย