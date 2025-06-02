# Django Shell Testing Checklist: Event Management System

## User Roles

- [x] **Create user with invalid or empty fields (username, mail, etc.)**  
      Expected: Raises `ValidationError`.

- [x] **Create `creator` user**  
      Expected: User is created with `role='creator'`.

- [x] **Create `visitor` user**  
      Expected: User is created with `role='visitor'`.

- [x] **Create `admin` user**  
      Expected: User has `is_staff=True`, `is_superuser=True`.

---

## Event Creation

- [x] **Create event with invalid or empty fields (title, location, etc.)**  
      Expected: Raises `ValidationError`.
      
- [x] **Creator creates a future event**  
      Expected: Saved with `status='published'`.

- [x] **Visitor tries to create an event**  
      Expected: Raises `PermissionError`.

- [x] **Creator creates a past event with `status='completed'`**  
      Expected: Saved successfully.

- [x] **Creator creates a past event with `status='published'`**  
      Expected: Status auto-updates to `completed`.

---

## Event Status Logic

- [x] **Past event automatically marked as `completed`**  
      Expected: `status == 'completed'`.

- [x] **Creator cancels a published event**  
      Expected: `status == 'cancelled'`, all registrations cancelled.

- [x] **Cancel an already cancelled event**  
      Expected: Raises `ValueError`.

- [x] **Visitor attempts to cancel an event**  
      Expected: Raises `PermissionError`.

---

## Visitor Registration Logic

- [x] **Visitor registers for a future published event**  
      Expected: `Registration` created with `status='registered'`.

- [x] **Visitor tries to register twice**  
      Expected: Raises `ValidationError`.

- [x] **Creator tries to register for event**  
      Expected: Raises `ValidationError`.

- [x] **Visitor tries to register for cancelled or past (completed) event**  
      Expected: Raises `ValidationError`.

---

## Cancel Registration

- [x] **Visitor cancels their registration**  
      Expected: `status='cancelled'`.

- [x] **Cancel registration after event date**  
      Expected: Raises `ValueError`.

- [x] **Cancel registration twice**
      Expected: Raises `ValueError`.
