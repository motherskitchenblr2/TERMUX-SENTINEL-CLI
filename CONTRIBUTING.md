# Contributing to Termux-Sentinel

Thank you for your interest in contributing to Termux-Sentinel!

## Code of Conduct

Please be respectful and constructive in all discussions, issues, and pull
requests.

## Development Workflow

1. Fork the repository and create your feature branch from `main`:

   ```bash
   git checkout -b feature/my-new-feature
   ```

2. Set up the development environment:

   ```bash
   pip install -r requirements.txt -r requirements-dev.txt
   pre-commit install
   ```

3. Ensure formatting and quality checks pass:

   ```bash
   ruff check .
   black --check .
   pytest
   ```

4. Commit your changes following conventional commit syntax:

   - `feat(...)`: New feature or capability
   - `fix(...)`: Bug fix
   - `chore(...)`: Maintenance or dependencies
   - `docs(...)`: Documentation updates

5. Open a Pull Request against `main`. All GitHub Action workflows must pass.

## Protection Constraints

- Never modify the core safety vault rules in `vault.json` to bypass
  exclusion lists without explicit architectural sign-off.
- Ensure terminal output functions adhere to the <= 44 column mobile width
  constraint.
