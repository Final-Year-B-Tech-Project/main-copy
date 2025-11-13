import os

project_name = "ai_interview_system"

structure = {
    "Backend Files (Python Flask)": [
        "requirements.txt",
        "config.py",
        "app.py",
        "run.py",
        "app/__init__.py",
        "app/models.py",
        "app/auth.py",
        "app/main.py",
        "app/ai_service.py",
        "app/utils.py",
    ],
    "Frontend Files (Vanilla JavaScript + Bootstrap)": [
        "templates/base.html",
        "templates/index.html",
        "templates/components/navbar.html",
        "templates/components/alerts.html",
        "templates/components/footer.html",
        "static/css/main.css",
        "static/js/main.js",
    ],
    "Setup & Documentation": [
        "README.md",
        ".env.example",
        ".gitignore",
    ],
}

def create_structure(base_path="."):
    root = os.path.join(base_path, project_name)
    for section, files in structure.items():
        section_path = os.path.join(root, section)
        os.makedirs(section_path, exist_ok=True)
        for file in files:
            file_path = os.path.join(section_path, file)
            os.makedirs(os.path.dirname(file_path), exist_ok=True)
            open(file_path, "w").close()
    print(f"✅ Project '{project_name}' structure created successfully!")

if __name__ == "__main__":
    create_structure()
