import sqlite3
import uuid
import random
from datetime import datetime, timedelta
from faker import Faker

DB_NAME = "asana_simulation.sqlite"
NUM_USERS = 500
NUM_TEAMS = 10
PROJECTS_PER_TEAM = 3
TASK_RANGE = (10, 25)

fake = Faker()
random.seed(42)

def uid():
    return str(uuid.uuid4())

def random_past_date(days=1500):
    return datetime.now() - timedelta(days=random.randint(0, days))

def chance(p):
    return random.random() < p

SCHEMA = """
PRAGMA foreign_keys = ON;

CREATE TABLE organizations (
    organization_id TEXT PRIMARY KEY,
    name TEXT,
    created_at TIMESTAMP
);

CREATE TABLE users (
    user_id TEXT PRIMARY KEY,
    organization_id TEXT,
    full_name TEXT,
    email TEXT,
    role TEXT,
    created_at TIMESTAMP
);

CREATE TABLE teams (
    team_id TEXT PRIMARY KEY,
    organization_id TEXT,
    name TEXT,
    created_at TIMESTAMP
);

CREATE TABLE team_memberships (
    team_id TEXT,
    user_id TEXT,
    joined_at TIMESTAMP,
    PRIMARY KEY (team_id, user_id)
);

CREATE TABLE projects (
    project_id TEXT PRIMARY KEY,
    team_id TEXT,
    name TEXT,
    status TEXT,
    created_at TIMESTAMP
);

CREATE TABLE sections (
    section_id TEXT PRIMARY KEY,
    project_id TEXT,
    name TEXT,
    position INTEGER
);

CREATE TABLE tasks (
    task_id TEXT PRIMARY KEY,
    project_id TEXT,
    section_id TEXT,
    parent_task_id TEXT,
    name TEXT,
    description TEXT,
    assignee_id TEXT,
    due_date DATE,
    completed BOOLEAN,
    created_at TIMESTAMP,
    completed_at TIMESTAMP
);

CREATE TABLE comments (
    comment_id TEXT PRIMARY KEY,
    task_id TEXT,
    author_id TEXT,
    content TEXT,
    created_at TIMESTAMP
);

CREATE TABLE custom_field_definitions (
    field_id TEXT PRIMARY KEY,
    organization_id TEXT,
    name TEXT,
    field_type TEXT
);

CREATE TABLE custom_field_values (
    task_id TEXT,
    field_id TEXT,
    value TEXT,
    PRIMARY KEY (task_id, field_id)
);

CREATE TABLE tags (
    tag_id TEXT PRIMARY KEY,
    organization_id TEXT,
    name TEXT
);

CREATE TABLE task_tags (
    task_id TEXT,
    tag_id TEXT,
    PRIMARY KEY (task_id, tag_id)
);
"""

conn = sqlite3.connect(DB_NAME)
cursor = conn.cursor()
cursor.executescript(SCHEMA)

org_id = uid()
cursor.execute(
    "INSERT INTO organizations VALUES (?, ?, ?)",
    (org_id, "Acme SaaS Inc.", random_past_date(2000))
)

users = []
for _ in range(NUM_USERS):
    users.append({
        "user_id": uid(),
        "organization_id": org_id,
        "full_name": fake.name(),
        "email": fake.email(),
        "role": random.choices(["admin", "member", "guest"], [0.05, 0.9, 0.05])[0],
        "created_at": random_past_date(1500)
    })

cursor.executemany(
    "INSERT INTO users VALUES (:user_id, :organization_id, :full_name, :email, :role, :created_at)",
    users
)

team_names = [
    "Backend Engineering", "Frontend Engineering", "Infrastructure",
    "Product", "Design", "Marketing", "Sales",
    "Operations", "Finance", "HR"
]

teams = []
for name in team_names[:NUM_TEAMS]:
    teams.append({
        "team_id": uid(),
        "organization_id": org_id,
        "name": name,
        "created_at": random_past_date(1200)
    })

cursor.executemany(
    "INSERT INTO teams VALUES (:team_id, :organization_id, :name, :created_at)",
    teams
)

memberships = []
for user in users:
    team_count = random.choices([1, 2, 3], [0.7, 0.25, 0.05])[0]
    for team in random.sample(teams, team_count):
        memberships.append({
            "team_id": team["team_id"],
            "user_id": user["user_id"],
            "joined_at": user["created_at"] + timedelta(days=random.randint(1, 30))
        })

cursor.executemany(
    "INSERT INTO team_memberships VALUES (:team_id, :user_id, :joined_at)",
    memberships
)

projects = []
sections = []
section_names = ["Backlog", "To Do", "In Progress", "Review", "Done"]

for team in teams:
    for i in range(PROJECTS_PER_TEAM):
        project_id = uid()
        projects.append({
            "project_id": project_id,
            "team_id": team["team_id"],
            "name": f"{team['name']} Initiative {i+1}",
            "status": random.choices(["active", "completed", "archived"], [0.7, 0.2, 0.1])[0],
            "created_at": random_past_date(900)
        })

        for idx, sec in enumerate(section_names):
            sections.append({
                "section_id": uid(),
                "project_id": project_id,
                "name": sec,
                "position": idx
            })

cursor.executemany(
    "INSERT INTO projects VALUES (:project_id, :team_id, :name, :status, :created_at)",
    projects
)

cursor.executemany(
    "INSERT INTO sections VALUES (:section_id, :project_id, :name, :position)",
    sections
)

tasks = []
for project in projects:
    sec_ids = [s["section_id"] for s in sections if s["project_id"] == project["project_id"]]
    for _ in range(random.randint(*TASK_RANGE)):
        created = random_past_date(400)
        completed = chance(0.7)
        tasks.append({
            "task_id": uid(),
            "project_id": project["project_id"],
            "section_id": random.choice(sec_ids),
            "parent_task_id": None,
            "name": fake.sentence(nb_words=6),
            "description": fake.text(120) if chance(0.6) else None,
            "assignee_id": random.choice(users)["user_id"] if chance(0.85) else None,
            "due_date": (created + timedelta(days=random.randint(-5, 30))).date() if chance(0.9) else None,
            "completed": completed,
            "created_at": created,
            "completed_at": created + timedelta(days=random.randint(2, 20)) if completed else None
        })

cursor.executemany(
    "INSERT INTO tasks VALUES (:task_id, :project_id, :section_id, :parent_task_id, :name, :description, :assignee_id, :due_date, :completed, :created_at, :completed_at)",
    tasks
)

comments = []
for task in tasks:
    if chance(0.4):
        for _ in range(random.randint(1, 3)):
            comments.append({
                "comment_id": uid(),
                "task_id": task["task_id"],
                "author_id": random.choice(users)["user_id"],
                "content": random.choice([
                    "Looks good.",
                    "Blocked on dependency.",
                    "Please review.",
                    "Completed."
                ]),
                "created_at": task["created_at"] + timedelta(days=random.randint(0, 10))
            })

cursor.executemany(
    "INSERT INTO comments VALUES (:comment_id, :task_id, :author_id, :content, :created_at)",
    comments
)

priority_field = uid()
cursor.execute(
    "INSERT INTO custom_field_definitions VALUES (?, ?, ?, ?)",
    (priority_field, org_id, "Priority", "enum")
)

for task in tasks:
    if chance(0.5):
        cursor.execute(
            "INSERT INTO custom_field_values VALUES (?, ?, ?)",
            (task["task_id"], priority_field, random.choice(["Low", "Medium", "High"]))
        )

urgent_tag = uid()
blocked_tag = uid()

cursor.executemany(
    "INSERT INTO tags VALUES (?, ?, ?)",
    [
        (urgent_tag, org_id, "urgent"),
        (blocked_tag, org_id, "blocked")
    ]
)

for task in tasks:
    if chance(0.3):
        cursor.execute(
            "INSERT INTO task_tags VALUES (?, ?)",
            (task["task_id"], urgent_tag)
        )

conn.commit()
conn.close()

print("asana_simulation.sqlite created successfully")
