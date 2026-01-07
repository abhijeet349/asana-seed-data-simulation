# Asana Seed Data Simulation

This repository contains a Python-based generator for creating a realistic,
synthetic Asana-like workspace dataset. The dataset is designed to support
reinforcement-learning environments that simulate computer-use tasks within
enterprise project management software.

The generated data reflects how a large B2B SaaS organization might use Asana
across engineering, product, marketing, and operations teams, including realistic
task workflows, collaboration patterns, and common edge cases.

---

## Project Scope

The goal of this project is not to perfectly replicate Asana’s internal systems,
but to generate data that *behaves* like a real enterprise workspace. Special
attention is given to:

- Non-uniform distributions (e.g., due dates, task completion)
- Cross-functional team memberships
- Incomplete, overdue, and unassigned tasks
- Temporal and relational consistency across entities

This avoids overly clean synthetic data that learning agents could exploit.

---

## Requirements

- Python 3.8 or newer
- Dependencies listed in `requirements.txt`

Install dependencies using:

```bash
pip install -r requirements.txt

