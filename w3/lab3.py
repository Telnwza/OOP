# =========================
# Class: Teacher
# =========================
class Teacher:
  def __init__(self, id, name):
    # เก็บข้อมูลประจำตัวอาจารย์
    self.__id = id
    self.__name = name


# =========================
# Class: Student
# =========================
class Student:
  def __init__(self, id, name):
      # เก็บข้อมูลนักศึกษา
      self.__id = id
      self.__name = name
      # เก็บ “รายการการลงทะเบียน” เป็นลิสต์ของ Enroll (ไม่เก็บ Subject ตรง ๆ)
      self.__enrolled = []
      
  # -------------------------
  # enroll(subject): ลงทะเบียนเรียนรายวิชา
  # -------------------------
  def enroll(self, subject):
      # ป้องกันการส่งชนิดข้อมูลผิด (ต้องเป็น Subject)
      if not isinstance(subject, Subject):
          return 'Error'
      
      # สร้างความสัมพันธ์การลงทะเบียน 1 รายการ
      subject_en = Enroll(subject)
      
      # กันลงซ้ำ: ถ้ามีวิชานี้อยู่แล้วให้ปฏิเสธ
      for enrolled in self.__enrolled:
        if enrolled.get_sub() == subject:
          return 'Already Enrolled'
      
      # ผ่านเงื่อนไข → บันทึกการลงทะเบียน
      self.__enrolled.append(subject_en)
      return 'Done'

  # -------------------------
  # drop(subject): ถอนรายวิชา
  # -------------------------
  def drop(self, subject):
      # ตรวจชนิดข้อมูล
      if not isinstance(subject, Subject):
          return 'Error'
      
      # หา Enroll ที่ผูกกับ subject แล้วลบออก
      for enrolled in self.__enrolled:
          if enrolled.get_sub() == subject:
            self.__enrolled.remove(enrolled)
            return 'Done'
      
      # ไม่พบวิชานี้ในรายการที่ลง
      return 'Not Found'
  
  # -------------------------
  # assign_grade(subject, grade): ใส่/แก้ไขเกรดของวิชาที่ลงทะเบียน
  # -------------------------
  def assign_grade(self, subject, grade):
      # วนหา Enroll ที่ตรงกับวิชา แล้วตั้งค่า grade
      for index, enrolled in enumerate(self.__enrolled):
        if enrolled.get_sub() == subject:
          self.__enrolled[index].set_grade(grade)
          return 'Done'
      
      # ถ้าไม่เคยลงทะเบียนวิชานี้ → ให้เกรดไม่ได้
      return 'Not Found'
      
  # -------------------------
  # get_enrolled_subjects(): คืน “รายชื่อวิชา” ที่ลงทะเบียน (เป็น list ของ Subject)
  # -------------------------
  def get_enrolled_subjects(self):
      subject = []
      for enrolled in self.__enrolled:
          subject.append(enrolled.get_sub())
      return subject
  
  # -------------------------
  # get_gps(): คำนวณ GPA จากเกรดและหน่วยกิต
  # แนวคิด: GPA = (Σ(grade_point * credit)) / (Σ credit)
  # -------------------------
  def get_gps(self):
    total_c = 0   # ผลรวมหน่วยกิต
    total_g = 0   # ผลรวมคะแนนถ่วงน้ำหนัก (grade point * credit)
    
    for enrolled in self.__enrolled:
      sub = enrolled.get_sub()
      grade = enrolled.get_grade()
      credit = sub.get_credit()
      
      total_c += credit
      
      # แปลงเกรดเป็นคะแนนมาตรฐานแล้วคูณหน่วยกิต
      match grade:
          case 'A': total_g += 4 * credit
          case 'B': total_g += 3 * credit
          case 'C': total_g += 2 * credit
          case 'D': total_g += 1 * credit
          case _:   total_g += 0  # ยังไม่ให้เกรด / F
    
    # กันหารศูนย์: ถ้ายังไม่ลงทะเบียนวิชาใดเลย
    if total_c == 0:
        return 0.0
    
    return total_g / total_c


# =========================
# Class: Subject
# =========================
class Subject:
  def __init__(self, id, subject_name, credit):
      # เก็บข้อมูลรายวิชา
      self.__id = id
      self.__subject_name = subject_name
      self.__credit = credit
      # เก็บอาจารย์ผู้สอน (เริ่มต้นยังไม่กำหนด)
      self.__teacher_id = ''
  
  # assign_teacher(teacher): ผูกอาจารย์ผู้สอนให้รายวิชา
  def assign_teacher(self, teacher):
      self.__teacher_id = teacher
  
  # get_credit(): คืนหน่วยกิต เพื่อให้ Student ใช้คำนวณ GPA
  def get_credit(self):
      return self.__credit


# =========================
# Class: Enroll
# =========================
class Enroll:
  def __init__(self, subject):
      # เก็บวิชาที่ลงทะเบียน (อ้างอิง Subject object)
      self.__subject = subject
      # เก็บเกรดของ “การลงทะเบียนครั้งนี้” (แยกจาก Subject)
      self.__grade = ''
    
  # get_sub(): คืนวิชาที่ลงทะเบียน
  def get_sub(self):
      return self.__subject
  
  # get_grade(): คืนเกรดปัจจุบัน
  def get_grade(self):
      return self.__grade
  
  # set_grade(grade): ตั้ง/แก้เกรด
  def set_grade(self, grade):
      self.__grade = grade

print("---------------------------------------")
print("Testing Student Registration System (Full Test Suite)")
print("---------------------------------------")

# --- Setup Data (เตรียมข้อมูล) ---
teacher1 = Teacher('T001', "Mr. Welsh")
subject1 = Subject('CS101', "Computer Programming 1", 3)
subject2 = Subject('CS102', "Computer Programming 2", 3)
subject3 = Subject('CS103', "Data Structure", 4)

# Test Setup: Assign Teacher
try:
  subject1.assign_teacher(teacher1)
  print(f"Setup Teacher: PASS") 
except Exception as e:
  print(f"Setup Teacher: FAIL ({e})")

student1 = Student('66010001', "Keanu Welsh")
student2 = Student('66010002', "Khadijah Burton")

# ---------------------------------------------------------
# Test Case 1: Enrollment Logic (การลงทะเบียน)
# ---------------------------------------------------------
print("\n[1] Testing Enrollment Logic")

# 1.1 ลงทะเบียนปกติ
res1 = student1.enroll(subject1)
print(f" - Enroll CS101: {res1} (Expected: Done)")

# 1.2 ลงทะเบียนซ้ำ
res2 = student1.enroll(subject1)
print(f" - Enroll CS101 Again: {res2} (Expected: Already Enrolled)")

# 1.3 ลงทะเบียนวิชาเพิ่ม
student1.enroll(subject2)
print(f" - Enroll CS102: Done")

# ---------------------------------------------------------
# Test Case 2: Drop Logic (การถอนรายวิชา)
# ---------------------------------------------------------
print("\n[2] Testing Drop Logic")

# 2.1 ถอนรายวิชาที่มีอยู่
res_drop = student1.drop(subject2)
print(f" - Drop CS102: {res_drop} (Expected: Done)")

# 2.2 ตรวจสอบว่าวิชาหายไปจริงหรือไม่
subjects = student1.get_enrolled_subjects()
if len(subjects) == 1 and subjects[0] == subject1:
      print(" - Verify Remaining Subjects: PASS")
else:
      print(f" - Verify Remaining Subjects: FAIL (Found {len(subjects)} subjects)")

# ---------------------------------------------------------
# Test Case 3: GPA Calculation (การคำนวณเกรดเฉลี่ย)
# ---------------------------------------------------------
print("\n[3] Testing GPA Calculation")

# Setup: ลง 3 วิชา
student2.enroll(subject1)
student2.enroll(subject2)
student2.enroll(subject3)

# ใส่เกรด
student2.assign_grade(subject1, "A") # 3 หน่วยกิต * 4 = 12
student2.assign_grade(subject2, "B") # 3 หน่วยกิต * 3 = 9
student2.assign_grade(subject3, "C") # 4 หน่วยกิต * 2 = 8
# Total Points = 29, Total Credits = 10 -> GPA = 2.90

gps = student2.get_gps()
print(f" - Student2 GPS: {gps:.2f} (Expected: 2.90)")

# ---------------------------------------------------------
# Test Case 4: Grade Update (การแก้ไขเกรด)
# ---------------------------------------------------------
print("\n[4] Testing Grade Update")

# เปลี่ยนเกรดวิชา CS102 จาก B เป็น A
student2.assign_grade(subject2, "A") 
# Points เดิม 29 -> เพิ่มมา 3 แต้ม (เพราะ B->A ต่างกัน 1 คะแนน * 3 หน่วยกิต) = 32
# GPA ใหม่ = 32 / 10 = 3.20

new_gps = student2.get_gps()
print(f" - Student2 New GPS: {new_gps:.2f} (Expected: 3.20)")

# ---------------------------------------------------------
# Test Case 5: Edge Cases (กรณีพิเศษ)
# ---------------------------------------------------------
print("\n[5] Testing Edge Cases")
student_fresh = Student('999', "Freshy")

# 5.1 ยังไม่ลงทะเบียนเลย
print(f" - No Subjects GPS: {student_fresh.get_gps()} (Expected: 0.0)")

# 5.2 ลงทะเบียนแล้ว แต่ยังไม่มีเกรด
student_fresh.enroll(subject1)
print(f" - No Grade GPS: {student_fresh.get_gps()} (Expected: 0.0)")

# ---------------------------------------------------------
# Test Case 6: Robustness (ทดสอบความทนทาน - Type Check)
# ---------------------------------------------------------
print("\n[6] Testing Robustness (Object vs String)")

# 6.1 Enroll ด้วย String
try:
  res = student_fresh.enroll("CS101 String")
  if res == "Error":
          print(f" - Enroll with String: PASS (Correctly returned 'Error')")
  else:
          print(f" - Enroll with String: FAIL (Returned '{res}', Expected 'Error')")
except AttributeError:
  print(" - Enroll with String: CRASHED ❌ (Code tried to access string attributes)")
except Exception as e:
  print(f" - Enroll with String: CRASHED ({e})")

# 6.2 Drop ด้วย String
try:
  res = student_fresh.drop("CS101 String")
  if res == "Error":
          print(f" - Drop with String: PASS (Correctly returned 'Error')")
  else:
          print(f" - Drop with String: FAIL (Returned '{res}', Expected 'Error')")
except Exception as e:
  print(f" - Drop with String: CRASHED ({e})")

# ---------------------------------------------------------
# Test Case 7: Logic Consistency (ความสอดคล้องของข้อมูล)
# ---------------------------------------------------------
print("\n[7] Testing Logic Consistency (Non-enrolled Subjects)")

# 7.1 Drop วิชาที่ไม่ได้ลงทะเบียน (student1 ถอน CS102 ไปแล้วใน Case 2)
# ลองถอน CS103 ที่ไม่เคยลงเลย
res_drop_not_found = student1.drop(subject3) 
if res_drop_not_found == "Not Found":
  print(f" - Drop Non-enrolled Subject: PASS (Returned 'Not Found')")
else:
  print(f" - Drop Non-enrolled Subject: FAIL (Returned '{res_drop_not_found}', Expected 'Not Found')")

# 7.2 ให้เกรดวิชาที่ไม่ได้ลงทะเบียน
res_grade_not_found = student1.assign_grade(subject3, "A")
if res_grade_not_found == "Not Found" or res_grade_not_found == "Error":
  print(f" - Grade Non-enrolled Subject: PASS (Returned '{res_grade_not_found}')")
else:
  print(f" - Grade Non-enrolled Subject: FAIL (Returned '{res_grade_not_found}', Expected 'Not Found')")

