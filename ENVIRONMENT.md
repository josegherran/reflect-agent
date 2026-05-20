# Environment Setup Instructions

1. **Create a .env file**
   - Copy `.env.example` to `.env`:
     ```sh
     cp .env.example .env
     ```
   - Edit `.env` and fill in your configuration values.

2. **Create and activate the virtual environment**
   - If not already created:
     ```sh
     python3 -m venv .venv
     ```
   - Activate:
     - On Linux/macOS:
       ```sh
       source .venv/bin/activate
       ```
     - On Windows:
       ```sh
       .venv\Scripts\activate
       ```

3. **Install dependencies**
   - Using uv (recommended):
     ```sh
     uv pip install -r requirements.txt
     ```
   - Or, if using pyproject.toml:
     ```sh
     uv pip install -r requirements.txt
     # or
     pip install -e .
     ```

4. **Run the project**
   - Add your run instructions here (e.g., `python main.py`)

---

## Notes
- Use `.env` for local development only. Never commit it to version control.
- Update `.env.example` when adding new environment variables.
