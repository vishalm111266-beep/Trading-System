# Development Rules

This document defines the mandatory rules and best practices for developing the Trading-System platform. All contributors must adhere to these guidelines.

---

## 1. Data Integrity & Research Rigor

### 1.1 No Look-Ahead Bias
- **NEVER** use future data in past calculations.
- Ensure all data alignment occurs at the correct timestamp.
- Validate that feature engineering only uses information available at the time of the signal.
- All backtests must pass a "look-ahead bias audit" before being considered valid.

### 1.2 Timeframe Discipline
- **Default to Daily (1D) timeframe** for all strategies and research.
- Higher timeframes (weekly/monthly) require explicit approval.
- Intraday data usage requires a specific business case and architectural review.
- Clearly document the timeframe in all strategy configurations.

### 1.3 Data Immutability
- **NEVER overwrite raw data files** without explicit confirmation and backup.
- Raw data directories are read-only for automated processes.
- All data transformations must produce new files with versioned timestamps.

---

## 2. Code Quality & Standards

### 2.1 Type Safety
- **Prefer type hints** for all function arguments and return values.
- Use `Optional` for nullable types.
- Run `mypy` checks in CI/CD; zero tolerance for type errors in core modules.

### 2.2 Documentation
- **Every public function must have a docstring** following Google or NumPy style.
- Docstrings must include:
  - Purpose description
  - Parameter types and descriptions
  - Return value description
  - Raises (if applicable)
- Private functions (`_function`) should have docstrings if logic is non-trivial.

### 2.3 Module Design
- **Keep modules focused on a single responsibility (SRP).**
- Avoid "God objects" or modules exceeding 500 lines of logic.
- If a file grows beyond reasonable limits, refactor into sub-modules.
- Use dependency injection over global state.

---

## 3. Testing Requirements

### 3.1 Mandatory Testing
- **Every new module must include corresponding tests.**
- No feature merge without test coverage.
- Unit tests must be isolated and deterministic.
- Integration tests must verify data flow between components.

### 3.2 Test Coverage
- Aim for >85% line coverage in core logic.
- Critical path functions (risk, execution) require 100% coverage.
- Tests must run successfully in the CI environment before merging.

### 3.3 Backtest Validation
- All strategies must include a "sanity check" backtest (e.g., flat position = zero PnL).
- Verify that transaction costs and slippage are applied correctly in tests.

---

## 4. Architecture & Process

### 4.1 Change Management
- **Explain architectural changes before implementing them.**
- Submit a design document or RFC for any structural changes.
- Discuss cross-cutting concerns (DB schema, API changes) with the team first.

### 4.2 File Safety
- **Never overwrite files without confirmation.**
- Use atomic writes (write to temp file, then move) for critical outputs.
- Implement backup mechanisms for configuration and state files.

### 4.3 Code Review
- All changes require at least one peer review.
- Reviewers must check for look-ahead bias, type safety, and test coverage.
- Refuse merges that violate these rules.

---

## 5. Security & Operations

### 5.1 Secrets Management
- **NEVER commit API keys, passwords, or private credentials.**
- Use environment variables or secure vaults for sensitive data.
- Rotate credentials immediately if accidentally exposed.

### 5.2 Logging & Monitoring
- Log all trading signals, orders, and execution events.
- Avoid logging sensitive market data or PII.
- Ensure logs are structured (JSON) for easy parsing.

### 5.3 Error Handling
- Fail gracefully; never crash the entire system on a single strategy error.
- Implement circuit breakers for unexpected market conditions.
- Log stack traces with context for debugging.

---

## 6. Enforcement

- **CI/CD Pipeline**: Automated checks for linting, type checking, and tests.
- **Pre-commit Hooks**: Enforce formatting and secret scanning.
- **Manual Audit**: Periodic review of backtest logic and data alignment.

> **Note:** Violations of these rules, especially regarding look-ahead bias and data integrity, are considered critical and will result in immediate rejection of the change.