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
