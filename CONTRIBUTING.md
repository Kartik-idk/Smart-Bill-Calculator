# Contributing to Smart Bill Calculator

Thank you for your interest in contributing! We welcome bug reports, feature suggestions, and code contributions.

## Code of Conduct
Please be polite, constructive, and respectful in all discussions, pull requests, and issues.

## Development Workflow

1. **Fork and clone the repository:**
   ```bash
   git clone https://github.com/<your-username>/smart-bill-calculator.git
   cd smart-bill-calculator
   ```

2. **Verify Python version:**
   Python 3.9 or higher is required.

3. **Run the test suite:**
   Ensure all existing tests pass before making any modifications:
   ```bash
   python3 -m unittest discover tests -v
   ```

4. **Code Guidelines:**
   - Adhere strictly to **PEP 8**.
   - Zero external runtime dependencies: use Python Standard Library only.
   - Always use `decimal.Decimal` with `ROUND_HALF_UP` for currency and tax math.
   - Add unit tests under `tests/` for any new logic or bug fixes.

5. **Submit a Pull Request:**
   - Write clear, concise commit messages following Conventional Commits (e.g. `feat: ...`, `fix: ...`, `test: ...`).
   - Open a PR describing your changes.

