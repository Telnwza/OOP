class User:
  def __init__(self, id, name):
    self.__id = id
    self.__name = name
    self.__grant_list = []

  def grant(self, permission):
    if not isinstance(permission, Permission): return 'Error'
    for grant in self.__grant_list:
      if permission == grant.get_permission() and grant.get_staus() == 'active' : return 'Already Granted'
    self.__grant_list.append(Grant(permission))
    return 'Done'
  
  def revoke(self, permission):
    if not isinstance(permission, Permission): return 'Error'
    for index, grant in enumerate(self.__grant_list):
      if permission == grant.get_permission() and grant.get_staus() == 'active':
        self.__grant_list[index].revoke()
        return 'Done'
    return 'Not Found'
  
  def has_permission(self, permission):
    if not isinstance(permission, Permission): return False
    for grant in self.__grant_list:
      if permission == grant.get_permission() and grant.get_staus() == 'active': return True
    return False
  
  def get_active_permissions(self):
    active_per = []
    for grant in self.__grant_list:
      if grant.get_staus() == 'active':
        active_per.append(grant.get_permission().get_code())
    return active_per

class Permission:
  def __init__(self, code, description):
    self.__code = code
    self.__description = description
  
  def get_code(self):
     return self.__code

class Grant:
  def __init__(self, permission):
    self.__permission = permission
    self.__status = 'active'

  def revoke(self):
    self.__status = 'revoked'
  
  def get_permission(self):
    return self.__permission
  
  def get_staus(self):
    return self.__status

# ================================
# HARD Test Suite: Access Control
# ================================

def case(title):
    print("\n" + "-" * 60)
    print(title)
    print("-" * 60)

def expect(actual, expected, label):
    ok = actual == expected
    print(f"{label}: {actual} (Expected: {expected}) {'PASS' if ok else 'FAIL'}")

def expect_true(actual, label):
    ok = actual is True
    print(f"{label}: {actual} (Expected: True) {'PASS' if ok else 'FAIL'}")

def expect_false(actual, label):
    ok = actual is False
    print(f"{label}: {actual} (Expected: False) {'PASS' if ok else 'FAIL'}")

def norm_codes(items):
    """
    แปลงผลจาก get_active_permissions() ให้เป็น list[str] เสมอ
    รองรับทั้ง list[Permission] และ list[str]
    """
    if not isinstance(items, list):
        return []
    codes = []
    for it in items:
        if isinstance(it, str):
            codes.append(it)
        else:
            try:
                codes.append(it.get_code())
            except:
                try:
                    codes.append(it.code)
                except:
                    pass
    return sorted(codes)

print("\n===============================")
print("ACCESS CONTROL — HARD TESTS")
print("===============================")

# ---------- Setup ----------
u = User("U001", "Te")
p_read = Permission("READ_REPORT", "Read report")
p_del  = Permission("DELETE_USER", "Delete user")
p_cfg  = Permission("CFG_WRITE", "Write config")

case("1) Type robustness")
expect(u.grant("READ_REPORT"), "Error", "1.1 grant invalid type")
expect(u.revoke(123), "Error", "1.2 revoke invalid type")
expect_false(u.has_permission("READ_REPORT"), "1.3 has_permission invalid type")

case("2) Grant permission")
expect(u.grant(p_read), "Done", "2.1 grant READ")
expect(u.grant(p_read), "Already Granted", "2.2 grant READ again")
expect_true(u.has_permission(p_read), "2.3 has READ == True")

case("3) Revoke permission")
expect(u.revoke(p_del), "Not Found", "3.1 revoke DELETE (never granted)")
expect(u.revoke(p_read), "Done", "3.2 revoke READ")
expect_false(u.has_permission(p_read), "3.3 has READ after revoke == False")
expect(u.revoke(p_read), "Not Found", "3.4 revoke READ again")

case("4) Re-grant after revoke")
expect(u.grant(p_read), "Done", "4.1 re-grant READ")
expect_true(u.has_permission(p_read), "4.2 has READ again")

case("5) Multiple permissions & list integrity")
expect(u.grant(p_del), "Done", "5.1 grant DELETE")
expect(u.grant(p_cfg), "Done", "5.2 grant CFG_WRITE")
expect(u.revoke(p_del), "Done", "5.3 revoke DELETE")

active = norm_codes(u.get_active_permissions())
print(f"5.4 active permissions: {active}")
ok = ("READ_REPORT" in active) and ("CFG_WRITE" in active) and ("DELETE_USER" not in active)
print("5.4 list integrity:", "PASS" if ok else "FAIL")

case("6) Idempotence")
expect(u.grant(p_cfg), "Already Granted", "6.1 grant CFG again")