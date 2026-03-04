# Contributing to LegalFinance RAG

Thank you for your interest in contributing! This document provides guidelines for contributing to the project.

## 🚀 Getting Started

1. Fork the repository
2. Clone your fork: `git clone https://github.com/YOUR_USERNAME/legal-finance-rag.git`
3. Create a branch: `git checkout -b feature/your-feature-name`
4. Install dev dependencies: `make install-dev`

## 💻 Development Workflow

### Code Style

We use automated formatting and linting:

```bash
# Format code
make format

# Check linting
make lint
```

### Pre-commit Hooks

Install pre-commit hooks to automatically check code before commits:

```bash
pre-commit install
```

### Testing

Always run tests before submitting:

```bash
# Run all tests
make test

# Run specific test file
pytest tests/unit/test_retrieval.py -v

# Run with coverage
make test-cov
```

## 📝 Pull Request Process

1. **Update tests**: Add/update tests for your changes
2. **Update docs**: Update README if needed
3. **Run checks**: Ensure `make lint` and `make test` pass
4. **Write clear commit messages**: Use conventional commits
5. **Submit PR**: Fill out the PR template completely

### Commit Message Format

```
type(scope): description

[optional body]
[optional footer]
```

Types: `feat`, `fix`, `docs`, `style`, `refactor`, `test`, `chore`

Examples:
- `feat(retrieval): add domain filtering to vector search`
- `fix(generation): handle empty context gracefully`
- `docs(readme): update installation instructions`

## 🐛 Reporting Issues

When reporting issues, please include:

1. Clear description of the problem
2. Steps to reproduce
3. Expected vs actual behavior
4. Environment details (OS, Python version)
5. Relevant logs or error messages

## 💡 Feature Requests

For feature requests:

1. Check existing issues first
2. Describe the use case
3. Explain the proposed solution
4. Consider implementation complexity

## 📁 Adding Documents

To add new legal/financial documents:

1. Place files in appropriate `data/raw/{domain}/` folder
2. Ensure proper licensing/permissions
3. Run `make ingest-clear` to reindex
4. Run `make evaluate` to verify quality

## 🧪 Adding Evaluation Questions

To add questions to the golden dataset:

1. Edit `evaluation/data/golden_qa.yaml`
2. Follow the existing format
3. Include: question, expected_answer, required_keywords, domain
4. Run `make evaluate` to test

## 📋 Code Review Checklist

- [ ] Tests pass
- [ ] Lint checks pass
- [ ] Documentation updated
- [ ] No hardcoded secrets
- [ ] Error handling is appropriate
- [ ] Logging is useful but not excessive
