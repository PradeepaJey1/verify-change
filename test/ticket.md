# User story: Control SMS appointment reminders

**Story ID:** APPT-142

As a customer with an account, I want to turn SMS appointment reminders on or off so that I can choose whether appointment messages are sent to my phone.

## Background

The appointment service currently sends an SMS reminder 24 hours before each appointment when the customer has a phone number. Customers can already receive email reminders. The new setting should affect SMS reminders only.

## Acceptance criteria

1. An authenticated customer can see the current SMS reminder setting on the Preferences page.
2. An authenticated customer can turn SMS reminders off or on. The selected value remains after a page refresh or a new sign-in.
3. SMS reminders are enabled by default for new customers and for existing customers when this feature is released.
4. When the setting is off, the 24-hour reminder job does not send that customer an SMS. Email reminders continue according to the existing email setting.
5. A customer cannot change another customer's reminder setting.
6. The API rejects a setting value that is not a boolean and leaves the saved value unchanged.

## Out of scope

This story does not change booking confirmations, appointment cancellation messages, or the existing email reminder preference.
