# AgriShield AI — Backend Platform

AgriShield AI is a modular, scalable, and secure backend platform designed to prevent agricultural post-harvest loss and deliver actionable decision support for farmers, buyers, transporters, and cooperative societies across rural India.

For full setup documentation, endpoint descriptions, and test reports, please refer to the root [README.md](../README.md) and [DEVELOPMENT_STATUS.md](../DEVELOPMENT_STATUS.md).

### Quick Commands:
- Apply migrations: `alembic upgrade head`
- Seed demonstration data: `python scripts/seed_demo_data.py`
- Run server: `uvicorn app.main:app --reload`
- Run test suite: `pytest -v`

