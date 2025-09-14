# Better5e

Better5e is a Django project exploring digital tooling for tabletop games. It currently includes user authentication, configurable dice appearance, and a proxy for loading custom DiceBox themes.

## Getting Started

Follow these steps to run the project locally:

1. **Clone the repository** and change into the project directory:
   ```bash
   git clone <repo-url>
   cd better5e
   ```
2. **Create and activate a virtual environment:**
   ```bash
   python -m venv .venv
   source .venv/bin/activate
   ```
3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```
4. **Apply database migrations:**
   ```bash
   python manage.py migrate
   ```
5. **Run the development server:**
   ```bash
   python manage.py runserver
   ```
   Visit `http://127.0.0.1:8000/` in your browser to access the site.

6. **Run tests:**
   ```bash
   python manage.py test
   ```

## Features

- **User Accounts:** Custom user model with signup and settings pages for selecting dice appearance.
- **Dice Theme Proxy:** Endpoints that validate and proxy remote DiceBox themes, with basic caching and GitHub URL transformation.
- **Protected Dashboard:** Authenticated landing page placeholder for future tools.

## Contributing

See [AGENTS.md](AGENTS.md) for contribution guidelines.

