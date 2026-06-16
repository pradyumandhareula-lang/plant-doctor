# 🌿 Plant Doctor: Intelligent MVP

An intelligent plant health assessment application.

### 🗄️ Database Architecture

This project uses SQLAlchemy to define the data structures for managing historical plant scans. The schema maps diagnostic information into a structured relational format.

* **Database Schema Definitions**: View the structured fields, indexes, and tables defined in [backend/models.py](./backend/models.py).

#### Data Model Fields:
* `id`: Primary Key (Integer, Auto-incremented)
* `timestamp`: Execution Log Time (DateTime, Defaults to UTC)
* `plant_species`: Identified Botanical Name (String, Indexed)
* `health_status`: Diagnosed Vitality Condition/Issue Metrics (String)
* `remedy_plan`: Generated Actionable Recovery Steps (String)

