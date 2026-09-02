# AquaDriver

## 1. Business Description

**AquaDriver** is a lightweight, self-hosted central management system for home and office IoT automation. Designed to operate completely offline within a local network (LAN), it serves as the brain for microcontrollers like ESP8266 and Arduino. 

Instead of relying on third-party cloud services, AquaDriver provides a private, secure, and customizable hub to schedule tasks, monitor sensors, and control physical devices (such as relays, lights, and water pumps). It automatically collects data, evaluates predefined rules, and triggers real-time alerts or subsequent actions, making it ideal for managing aquariums, terrariums, smart lighting, and environmental monitoring.

**Core Value Proposition:**
*   **100% Local Processing:** Fast response times and high privacy with no cloud dependency.
*   **Rule-Based Automation:** Automatically trigger physical actions or notifications (Email, Pushover) when sensor readings hit specific thresholds.
*   **Advanced Scheduling:** Built-in cron and interval task manager for daily routines.
*   **Visual Dashboard:** Centralized web interface to monitor cameras, device statuses, and historical logs.

---

## 2. Technology Stack

*   **Backend:** Python 3, Flask
*   **Task Scheduling:** APScheduler
*   **Database:** SQLite + SQLAlchemy (ORM)
*   **Frontend:** HTML, Bootstrap 5, DataTables
*   **Deployment:** Designed for Docker / Linux environments
*   **IoT Communication:** HTTP, JSON, MJPEG Streaming

---

## 3. Improvement Checkpoints (Known Issues & Suggestions)

Below is a checklist of architectural and security improvements to ensure the application remains stable as it scales.

- [ ] **Fix SQL Injection Vulnerabilities:** Avoid using string concatenation (`+`) to build SQL queries in `__init__.py` and `report_operations.py`. Use parameterized queries (`:variable_name`) built into SQLAlchemy to prevent database corruption.
- [ ] **Solve Circular Imports:** The `routes.py` file imports `models`, but `models` import `db` from `routes.py` (or `mainApp`). This makes the application fragile. Move the `db` initialization to a separate `extensions.py` file.
- [ ] **Handle Synchronous Blocking:** Currently, `requests.get/post` calls to ESP devices happen in the main Flask thread. If a device is offline, Flask waits (blocks) until the timeout, slowing down the whole web interface. *Suggestion:* Move HTTP triggers to background threads or use asynchronous requests.
- [ ] **Scheduler Duplication on Production:** If deployed with multiple Gunicorn workers, `APScheduler` will run multiple times, triggering devices simultaneously. *Suggestion:* Run the scheduler as a completely separate background script or use a lock mechanism.
- [ ] **Unbounded Database Growth:** The `archive` table grows infinitely. *Suggestion:* Add a scheduled maintenance task to automatically delete logs older than 30 days.

---

## 4. Code Simplifications (What to Remove or Move)

The codebase has great logic but can be simplified to make it easier to read and maintain.

- [ ] **Move JSON configs to the Database:** Currently, events, dashboards, and validations are stored in separate `.json` files. This requires complex file reading, caching, and forms. *Move these into SQLite tables*. It will drastically simplify your code, enable direct editing via the dashboard, and remove the need for `config_operations.py`.
- [ ] **Remove "Wrapper" Classes:** Classes like `ArchiveLister`, `EventListerJson`, and `ValidationLister` only do one thing: fetch a list. They add unnecessary complexity. *Suggestion:* Replace them with simple functions (e.g., `def get_all_events():`) or use direct SQLAlchemy queries in your routes.
- [ ] **Stop using `__init__` for Actions:** Classes like `ArchiveAdder` and `ResponseTrigger` execute heavy logic (saving to DB, sending emails) right when they are created. *Suggestion:* Keep `__init__` strictly for assigning variables, and create an `.execute()` or `.save()` method for the actual work (partially done, but requires enforcement across the app).
- [ ] **Implement Flask Blueprints:** `routes.py` is getting too large. Split it into logical modules (Blueprints):
    *   `routes_dashboard.py` (web interface)
    *   `routes_api.py` (ESP communication)
    *   `routes_admin.py` (logs, jobs, config)
- [ ] **Consolidate Config Forms:** You have multiple forms doing the exact same thing (editing JSON text). Once moved to the database, you can replace the JSON text areas with standard CRUD (Create, Read, Update, Delete) tables for easier management.