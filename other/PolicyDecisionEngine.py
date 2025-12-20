class Context:
  def __init__(self, user_role, action, resource, hour) -> None:
    self.__user_role = user_role
    self.__action = action
    self.__resource = resource
    self.__hour = hour
  
  def get_user_role(self):
    return self.__user_role
  def get_resource(self):
    return self.__resource
  def get_action(self):
    return self.__action
  def get_hour(self):
    return self.__hour

class Rule:
  def evaluate(self, context) -> str:
    return 'SKIP'
  
class Policy:
  def __init__(self) -> None:
    self.__rule_list = []

  def add_rule(self, rule):
    if not isinstance(rule, Rule): return 'Error'
    self.__rule_list.append(rule)
    return 'Done'
  
  def decide(self, context):
    for rule in self.__rule_list:
       result = rule.evaluate(context)
       if result != 'SKIP': return result
    return 'DENY'
  
# ============================================================
# FULL (HARD) Test Suite: Policy Decision Engine
# ============================================================
# Assumed you have:
#   class Context(user_role, action, resource, hour)
#   class Rule with method evaluate(context) -> "ALLOW"/"DENY"/"SKIP"
#   class Policy with:
#       add_rule(rule) -> "Done"/"Error"
#       decide(context) -> "ALLOW"/"DENY"
#
# Notes:
# - This suite is "hidden-test style": order matters, SKIP correctness, default deny,
#   type robustness, and "stop at first decision".
# - This suite defines 4 Rule subclasses for testing. Your Policy.add_rule should
#   accept these as valid Rule objects (i.e., isinstance(rule, Rule) should pass).
# ============================================================

def _case(title):
    print("\n" + "=" * 70)
    print(title)
    print("=" * 70)

def _expect(actual, expected, label):
    ok = (actual == expected)
    print(f"{label}: {actual!r} (Expected: {expected!r}) {'PASS' if ok else 'FAIL'}")
    return ok

def _safe_call(fn, label):
    try:
        return fn()
    except Exception as e:
        print(f"{label}: CRASHED ({e})")
        return "__CRASHED__"

# ---------- Context snapshot helpers (tolerant to your design) ----------
def _ctx_get(ctx, name):
    """
    Read a field from Context without assuming your internal design.
    Tries:
      - getter methods: get_<name>(), <name>()
      - public attributes: <name>
    """
    # common getter names
    for g in (f"get_{name}", name):
        try:
            v = getattr(ctx, g, None)
            if callable(v):
                return v()
        except Exception:
            pass
    # public attribute fallback
    try:
        return getattr(ctx, name)
    except Exception:
        return None

def _ctx_snapshot(ctx):
    return (
        _ctx_get(ctx, "user_role"),
        _ctx_get(ctx, "action"),
        _ctx_get(ctx, "resource"),
        _ctx_get(ctx, "hour"),
    )

# ============================================================
# Test Rules (subclass Rule)
# ============================================================

class AdminAllowRule(Rule):
    def evaluate(self, context):
        return "ALLOW" if _ctx_get(context, "user_role") == "admin" else "SKIP"

class DeleteUserDbDenyRule(Rule):
    def evaluate(self, context):
        if _ctx_get(context, "action") == "delete" and _ctx_get(context, "resource") == "user_db":
            return "DENY"
        return "SKIP"

class NightDenyRule(Rule):
    def evaluate(self, context):
        hour = _ctx_get(context, "hour")
        if isinstance(hour, int) and hour >= 22:
            return "DENY"
        return "SKIP"

class SpyRule(Rule):
    """
    A rule that records how many times it was evaluated.
    Useful to confirm Policy stops at the first ALLOW/DENY.
    """
    def __init__(self, decision="SKIP"):
        self.__decision = decision
        self.__count = 0

    def evaluate(self, context):
        self.__count += 1
        return self.__decision

    def get_count(self):
        return self.__count

# ============================================================
# RUN TESTS
# ============================================================

print("\n############################################")
print("FULL HARD TESTS — POLICY DECISION ENGINE")
print("############################################")

_case("0) add_rule type robustness")
p0 = Policy()
_expect(_safe_call(lambda: p0.add_rule("not rule"), "0.1 add_rule invalid type"), "Error", "0.1 add_rule('str') -> Error")
_expect(_safe_call(lambda: p0.add_rule(123), "0.2 add_rule invalid type"), "Error", "0.2 add_rule(123) -> Error")

_case("1) Default DENY when all rules SKIP")
p1 = Policy()
_expect(p1.add_rule(AdminAllowRule()), "Done", "1.0 add AdminAllowRule")
ctx = Context("staff", "read", "report", 10)
# AdminAllow -> SKIP, no more rules, default deny
_expect(_safe_call(lambda: p1.decide(ctx), "1.1 decide"), "DENY", "1.1 decide -> DENY (default)")

_case("2) DENY rule triggers and stops evaluation")
p2 = Policy()
spy_after = SpyRule("ALLOW")  # should NOT run if DENY happens earlier
_expect(p2.add_rule(DeleteUserDbDenyRule()), "Done", "2.0 add DeleteUserDbDenyRule")
_expect(p2.add_rule(spy_after), "Done", "2.0 add SpyRule(ALLOW) after deny")

ctx = Context("staff", "delete", "user_db", 10)
res = _safe_call(lambda: p2.decide(ctx), "2.1 decide")
_expect(res, "DENY", "2.1 decide -> DENY (DeleteUserDbDenyRule)")
_expect(spy_after.get_count(), 0, "2.2 spy_after count should be 0 (must stop at DENY)")

_case("3) ALLOW rule triggers and stops evaluation")
p3 = Policy()
spy_after2 = SpyRule("DENY")  # should NOT run if ALLOW happens earlier
_expect(p3.add_rule(AdminAllowRule()), "Done", "3.0 add AdminAllowRule")
_expect(p3.add_rule(DeleteUserDbDenyRule()), "Done", "3.0 add DeleteUserDbDenyRule")
_expect(p3.add_rule(spy_after2), "Done", "3.0 add SpyRule(DENY) after")

ctx = Context("admin", "delete", "user_db", 23)  # would deny later, but admin allow first
res = _safe_call(lambda: p3.decide(ctx), "3.1 decide")
_expect(res, "ALLOW", "3.1 decide -> ALLOW (AdminAllowRule first)")
_expect(spy_after2.get_count(), 0, "3.2 spy_after2 count should be 0 (must stop at ALLOW)")

_case("4) Order matters (same rules, different order flips result)")
p4a = Policy()
_expect(p4a.add_rule(AdminAllowRule()), "Done", "4.0a add Admin first")
_expect(p4a.add_rule(DeleteUserDbDenyRule()), "Done", "4.0a add Delete deny second")
_expect(p4a.add_rule(NightDenyRule()), "Done", "4.0a add Night deny third")
ctx = Context("admin", "delete", "user_db", 23)
_expect(_safe_call(lambda: p4a.decide(ctx), "4.1a decide"), "ALLOW", "4.1a result should be ALLOW (admin first)")

p4b = Policy()
_expect(p4b.add_rule(DeleteUserDbDenyRule()), "Done", "4.0b add Delete deny first")
_expect(p4b.add_rule(NightDenyRule()), "Done", "4.0b add Night deny second")
_expect(p4b.add_rule(AdminAllowRule()), "Done", "4.0b add Admin last")
ctx = Context("admin", "delete", "user_db", 23)
_expect(_safe_call(lambda: p4b.decide(ctx), "4.1b decide"), "DENY", "4.1b result should be DENY (deny first)")

_case("5) SKIP must not decide (Spy confirms it continues)")
p5 = Policy()
spy_skip = SpyRule("SKIP")     # should run
spy_allow = SpyRule("ALLOW")   # should run and stop
spy_never = SpyRule("DENY")    # must not run
_expect(p5.add_rule(spy_skip), "Done", "5.0 add Spy(SKIP)")
_expect(p5.add_rule(spy_allow), "Done", "5.0 add Spy(ALLOW)")
_expect(p5.add_rule(spy_never), "Done", "5.0 add Spy(DENY) after allow")

ctx = Context("staff", "read", "report", 12)
_expect(_safe_call(lambda: p5.decide(ctx), "5.1 decide"), "ALLOW", "5.1 result should be ALLOW")
_expect(spy_skip.get_count(), 1, "5.2 Spy(SKIP) evaluated exactly once")
_expect(spy_allow.get_count(), 1, "5.3 Spy(ALLOW) evaluated exactly once")
_expect(spy_never.get_count(), 0, "5.4 Spy(DENY) must NOT be evaluated")

_case("6) Context must not be mutated by Policy/Rules (snapshot check)")
p6 = Policy()
_expect(p6.add_rule(AdminAllowRule()), "Done", "6.0 add AdminAllowRule")
_expect(p6.add_rule(NightDenyRule()), "Done", "6.0 add NightDenyRule")
ctx = Context("staff", "read", "report", 23)
before = _ctx_snapshot(ctx)
_ = _safe_call(lambda: p6.decide(ctx), "6.1 decide")
after = _ctx_snapshot(ctx)
print(f"6.2 ctx snapshot before: {before!r}")
print(f"6.3 ctx snapshot after : {after!r}")
print("6.4 context immutability:", "PASS" if before == after else "FAIL")

_case("7) Boundary tests for hour (21 vs 22)")
p7 = Policy()
_expect(p7.add_rule(NightDenyRule()), "Done", "7.0 add NightDenyRule")
ctx21 = Context("staff", "read", "report", 21)
ctx22 = Context("staff", "read", "report", 22)
_expect(_safe_call(lambda: p7.decide(ctx21), "7.1 decide@21"), "DENY", "7.1 @21 -> DENY (default, night rule skips)")
_expect(_safe_call(lambda: p7.decide(ctx22), "7.2 decide@22"), "DENY", "7.2 @22 -> DENY (night rule triggers)")

print("\n############################################")
print("FULL HARD TESTS FINISHED")
print("############################################")