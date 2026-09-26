# PR: Add customer SMS reminder preference

**Related story:** APPT-142

This is a fictional PR for trying VerifyChange; the paths below represent a sample appointment service.

## Summary

- Add a saved SMS reminder preference with a default of `true`.
- Expose the preference on the customer's own preferences API.
- Skip SMS in the 24-hour reminder job when the preference is off.
- Keep email reminder behavior independent of the SMS setting.

## Verification reported by author

- Ran `pytest tests/test_preferences.py tests/test_reminders.py` locally; 8 passed.
- Manually toggled the setting off and refreshed the Preferences page.

## Diff

```diff
diff --git a/db/migrations/0042_sms_reminder_preference.sql b/db/migrations/0042_sms_reminder_preference.sql
new file mode 100644
--- /dev/null
+++ b/db/migrations/0042_sms_reminder_preference.sql
@@ -0,0 +1,2 @@
+ALTER TABLE customers
+ADD COLUMN sms_reminders_enabled BOOLEAN NOT NULL DEFAULT TRUE;
diff --git a/app/models.py b/app/models.py
--- a/app/models.py
+++ b/app/models.py
@@ -18,3 +18,4 @@ class Customer(db.Model):
     phone_number = db.Column(db.String(32))
     email = db.Column(db.String(255), nullable=False)
     email_reminders_enabled = db.Column(db.Boolean, nullable=False, default=True)
+    sms_reminders_enabled = db.Column(db.Boolean, nullable=False, default=True)
diff --git a/app/api/preferences.py b/app/api/preferences.py
--- a/app/api/preferences.py
+++ b/app/api/preferences.py
@@ -1,12 +1,24 @@
 from flask import Blueprint, jsonify, request
 from app.auth import current_customer
+from app.database import db
 
 bp = Blueprint("preferences", __name__)
 
 @bp.get("/api/me/preferences")
 def get_preferences():
     customer = current_customer()
     return jsonify({
         "email_reminders_enabled": customer.email_reminders_enabled,
+        "sms_reminders_enabled": customer.sms_reminders_enabled,
     })
 
+@bp.patch("/api/me/preferences")
+def update_preferences():
+    customer = current_customer()
+    payload = request.get_json(silent=True) or {}
+    sms_enabled = payload.get("sms_reminders_enabled")
+    if not isinstance(sms_enabled, bool):
+        return jsonify({"error": "sms_reminders_enabled must be a boolean"}), 400
+    customer.sms_reminders_enabled = sms_enabled
+    db.session.commit()
+    return jsonify({"sms_reminders_enabled": customer.sms_reminders_enabled})
diff --git a/app/jobs/reminders.py b/app/jobs/reminders.py
--- a/app/jobs/reminders.py
+++ b/app/jobs/reminders.py
@@ -22,6 +22,6 @@ def send_24_hour_reminders():
     for appointment in due_appointments():
         customer = appointment.customer
-        if customer.phone_number:
+        if customer.phone_number and customer.sms_reminders_enabled:
             sms_gateway.send(customer.phone_number, reminder_text(appointment))
         if customer.email_reminders_enabled:
             email_gateway.send(customer.email, reminder_email(appointment))
diff --git a/web/PreferencesPage.jsx b/web/PreferencesPage.jsx
--- a/web/PreferencesPage.jsx
+++ b/web/PreferencesPage.jsx
@@ -14,8 +14,24 @@ export function PreferencesPage() {
   const [preferences, setPreferences] = useState(null);
 
   return preferences && (
     <section>
       <h1>Reminder preferences</h1>
+      <label>
+        <input
+          type="checkbox"
+          checked={preferences.sms_reminders_enabled}
+          onChange={async (event) => {
+            const sms_reminders_enabled = event.target.checked;
+            const response = await fetch("/api/me/preferences", {
+              method: "PATCH",
+              headers: { "Content-Type": "application/json" },
+              body: JSON.stringify({ sms_reminders_enabled }),
+            });
+            if (response.ok) setPreferences({ ...preferences, sms_reminders_enabled });
+          }}
+        />
+        Send me SMS appointment reminders
+      </label>
       <EmailReminderToggle preferences={preferences} />
     </section>
   );
diff --git a/tests/test_preferences.py b/tests/test_preferences.py
--- a/tests/test_preferences.py
+++ b/tests/test_preferences.py
@@ -21,2 +21,10 @@ def test_get_preferences(client, customer):
     assert response.json["email_reminders_enabled"] is True
+    assert response.json["sms_reminders_enabled"] is True
 
+def test_customer_can_disable_sms_reminders(client, customer):
+    response = client.patch(
+        "/api/me/preferences", json={"sms_reminders_enabled": False}
+    )
+    assert response.status_code == 200
+    assert response.json["sms_reminders_enabled"] is False
+    assert customer.sms_reminders_enabled is False
diff --git a/tests/test_reminders.py b/tests/test_reminders.py
--- a/tests/test_reminders.py
+++ b/tests/test_reminders.py
@@ -35,3 +35,8 @@ def test_24_hour_reminder_sends_sms_and_email(customer, appointment):
     assert sms_gateway.send.call_count == 1
     assert email_gateway.send.call_count == 1
 
+def test_sms_opt_out_keeps_email_reminder(customer, appointment):
+    customer.sms_reminders_enabled = False
+    send_24_hour_reminders()
+    assert sms_gateway.send.call_count == 0
+    assert email_gateway.send.call_count == 1
```
