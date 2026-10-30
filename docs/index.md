# AgriShield AI — Official Technical Documentation

Welcome to the technical documentation for **AgriShield AI**, a modular platform designed to prevent agricultural post-harvest biological losses across rural India.

---

## 🧭 Documentation Map

| Guide | Description |
| :--- | :--- |
| **[System Architecture](ARCHITECTURE.md)** | Modular design, component interactions, database schema (24 relational tables), and concurrency locking. |
| **[REST API Reference](API_DOCUMENTATION.md)** | Complete HTTP/JSON API specifications, request/response models, and authentication workflows. |
| **[Machine Learning & Agronomic Science](ML_AND_AGRONOMIC_MODELS.md)** | Biochemical $Q_{10}$ equations, Vapor Pressure Deficit (VPD) physics, and Scikit-learn Random Forest regression model ($R^2 = 0.98$). |
| **[Frontend Design System](FRONTEND_GUIDE.md)** | Stitch design tokens, color palette, typography (`Plus Jakarta Sans` / `Inter`), page walkthroughs, and offline simulation. |
| **[Dependencies & Environment](DEPENDENCIES.md)** | Python dependency catalog, installation profiles, version constraints, and verification scripts. |
| **[Deployment & Operations](DEPLOYMENT_GUIDE.md)** | Local development, Alembic database migrations, Docker multi-container stack, and production scaling. |

---

## ⚡ Quick Links
- **Web Dashboard Entrypoint:** [`frontend/index.html`](../frontend/index.html) (or `http://localhost:8000/app/`)
- **Interactive Swagger Docs:** `http://localhost:8000/docs`
- **System Health Endpoint:** `http://localhost:8000/health`
- **Project Repository:** [GitHub Repository](https://github.com/gunjalpratik519-commits/AgriHub)

