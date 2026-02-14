# Contributing to Market Regime Detection System

Thank you for your interest in contributing! This document provides guidelines and instructions for contributing to the project.

---

## 📋 Table of Contents

- [Code of Conduct](#code-of-conduct)
- [Getting Started](#getting-started)
- [Development Setup](#development-setup)
- [How to Contribute](#how-to-contribute)
- [Coding Standards](#coding-standards)
- [Testing Guidelines](#testing-guidelines)
- [Documentation](#documentation)
- [Pull Request Process](#pull-request-process)
- [Areas for Contribution](#areas-for-contribution)

---

## 🤝 Code of Conduct

### Our Pledge

We pledge to make participation in our project a harassment-free experience for everyone, regardless of age, body size, disability, ethnicity, gender identity and expression, level of experience, nationality, personal appearance, race, religion, or sexual identity and orientation.

### Our Standards

**Positive behavior includes:**
- Using welcoming and inclusive language
- Being respectful of differing viewpoints
- Gracefully accepting constructive criticism
- Focusing on what is best for the community
- Showing empathy towards other community members

**Unacceptable behavior includes:**
- Use of sexualized language or imagery
- Trolling, insulting/derogatory comments, and personal attacks
- Public or private harassment
- Publishing others' private information without permission
- Other conduct which could reasonably be considered inappropriate

---

## 🚀 Getting Started

### Prerequisites

- Python 3.9+
- Git
- GitHub account
- Basic knowledge of machine learning and finance

### First Steps

1. **Star the repository** ⭐ to show your support
2. **Read the documentation** - [README.md](README.md), [EVALUATION_GUIDE.md](EVALUATION_GUIDE.md)
3. **Browse existing issues** to find something to work on
4. **Join our community** (Discord/Slack if available)

---

## 💻 Development Setup

### Fork and Clone

```bash
# Fork the repository on GitHub first, then:
git clone https://github.com/YOUR_USERNAME/Market-Regime-Detection-System.git
cd Market-Regime-Detection-System

# Add upstream remote
git remote add upstream https://github.com/shamiquekhan/Market-Regime-Detection-System.git
```

### Create Virtual Environment

```bash
# Windows
python -m venv .venv
.venv\Scripts\Activate.ps1

# macOS/Linux
python3 -m venv .venv
source .venv/bin/activate
```

### Install Dependencies

```bash
# Install production dependencies
pip install -r requirements.txt

# Install development dependencies
pip install -r requirements-dev.txt
```

**requirements-dev.txt** (create if doesn't exist):
```
pytest>=7.4.0
pytest-cov>=4.1.0
black>=23.7.0
flake8>=6.0.0
mypy>=1.4.0
pre-commit>=3.3.0
```

### Setup Pre-commit Hooks

```bash
pre-commit install
```

This ensures code quality checks run automatically before each commit.

### Verify Setup

```bash
# Run tests
pytest tests/

# Run linter
flake8 src/

# Run type checker
mypy src/

# Run formatter (check only)
black --check src/
```

---

## 🤲 How to Contribute

### Types of Contributions

We welcome:
- 🐛 **Bug reports and fixes**
- ✨ **New features**
- 📝 **Documentation improvements**
- 🧪 **Test coverage enhancements**
- 🎨 **UI/UX improvements**
- 🌐 **Localization and translations**
- 📊 **Performance optimizations**

### Finding Something to Work On

1. **Check [Issues](https://github.com/shamiquekhan/Market-Regime-Detection-System/issues)**
   - Look for `good first issue` label
   - Look for `help wanted` label

2. **Check [Discussions](https://github.com/shamiquekhan/Market-Regime-Detection-System/discussions)**
   - Feature proposals
   - Questions and answers

3. **Check the [Roadmap](README.md#roadmap)**
   - Planned features
   - Future enhancements

### Workflow

1. **Create an issue** (if one doesn't exist)
   - Describe the problem or feature
   - Get feedback before starting work

2. **Create a branch**
   ```bash
   git checkout -b feature/your-feature-name
   # or
   git checkout -b fix/bug-description
   ```

3. **Make your changes**
   - Write code
   - Add tests
   - Update documentation

4. **Commit your changes**
   ```bash
   git add .
   git commit -m "Add feature: description"
   ```

5. **Push to your fork**
   ```bash
   git push origin feature/your-feature-name
   ```

6. **Create a Pull Request**
   - Go to GitHub
   - Click "New Pull Request"
   - Fill out the PR template

---

## 📐 Coding Standards

### Python Style Guide

We follow **PEP 8** with some modifications:

- **Line length:** 100 characters (not 79)
- **Indentation:** 4 spaces (no tabs)
- **Quotes:** Single quotes for strings (except docstrings)
- **Imports:** Grouped and sorted (use `isort`)

### Code Formatting

We use **Black** for automatic code formatting:

```bash
# Format code
black src/ tests/

# Check formatting
black --check src/ tests/
```

### Linting

We use **flake8** for code linting:

```bash
# Run linter
flake8 src/ tests/

# Or with specific rules
flake8 --max-line-length=100 --ignore=E203,W503 src/
```

### Type Hints

Use type hints for all function signatures:

```python
from typing import List, Dict, Optional, Tuple
import pandas as pd
import numpy as np

def compute_features(
    data: pd.DataFrame,
    windows: List[int] = [1, 5, 21],
    include_momentum: bool = True
) -> pd.DataFrame:
    """
    Compute technical indicators.
    
    Args:
        data: Raw OHLCV data
        windows: Return calculation windows
        include_momentum: Whether to compute momentum indicators
        
    Returns:
        DataFrame with computed features
    """
    # Implementation
    pass
```

### Docstrings

Use **Google-style docstrings**:

```python
def backtest_strategy(regimes: np.ndarray, returns: np.ndarray) -> Dict[str, float]:
    """
    Backtest trading strategy based on regime predictions.
    
    This function simulates a trading strategy that goes long in favorable
    regimes and hedges in unfavorable regimes.
    
    Args:
        regimes: Array of regime labels for each time period
        returns: Array of market returns for each time period
        
    Returns:
        Dictionary containing:
            - sharpe_ratio: Risk-adjusted returns
            - max_drawdown: Maximum portfolio decline
            - total_return: Cumulative strategy return
            
    Raises:
        ValueError: If regimes and returns have different lengths
        
    Example:
        >>> regimes = np.array([0, 1, 2, 3])
        >>> returns = np.array([0.01, 0.02, -0.01, -0.03])
        >>> results = backtest_strategy(regimes, returns)
        >>> print(f"Sharpe: {results['sharpe_ratio']:.2f}")
    """
    # Implementation
    pass
```

---

## 🧪 Testing Guidelines

### Writing Tests

- Use **pytest** framework
- Write tests for all new features
- Maintain >80% code coverage
- Test edge cases and error conditions

**Example test:**

```python
# tests/test_models.py
import pytest
import numpy as np
from src.models.hmm_model import HMMRegimeDetector

def test_hmm_initialization():
    """Test HMM model initialization with default parameters."""
    model = HMMRegimeDetector(n_states=4)
    assert model.n_states == 4
    assert model.covariance_type == 'full'

def test_hmm_fit_predict():
    """Test HMM training and prediction."""
    # Create synthetic data
    X = np.random.randn(100, 3)
    
    # Train model
    model = HMMRegimeDetector(n_states=3)
    model.fit(X)
    
    # Predict regimes
    regimes = model.predict(X)
    
    # Assertions
    assert len(regimes) == 100
    assert set(regimes).issubset({0, 1, 2})
    assert hasattr(model.model, 'transmat_')

def test_hmm_invalid_input():
    """Test HMM error handling for invalid input."""
    model = HMMRegimeDetector(n_states=4)
    
    with pytest.raises(ValueError):
        model.fit(np.array([]))  # Empty array should raise error
```

### Running Tests

```bash
# Run all tests
pytest tests/

# Run specific test file
pytest tests/test_models.py

# Run with coverage
pytest --cov=src --cov-report=html tests/

# Run specific test
pytest tests/test_models.py::test_hmm_initialization
```

### Test Structure

```
tests/
├── __init__.py
├── test_data_collection.py     # Data fetching tests
├── test_features.py            # Feature engineering tests
├── test_models.py              # Model training/prediction tests
├── test_evaluation.py          # Evaluation metrics tests
└── fixtures/                   # Test data fixtures
    ├── sample_data.csv
    └── mock_responses.json
```

---

## 📚 Documentation

### Code Documentation

- Add docstrings to all classes and functions
- Include type hints
- Add inline comments for complex logic
- Update API.md for new public APIs

### User Documentation

- Update README.md for new features
- Add examples to QUICKSTART.md
- Update EVALUATION_GUIDE.md for new metrics
- Create tutorials for major features

### Changelog

Update [CHANGELOG.md](CHANGELOG.md) with your changes:

```markdown
## [Unreleased]

### Added
- New LSTM regime detection model (#123)
- Real-time NSE API integration (#145)

### Fixed
- Transition matrix persistence calculation bug (#156)

### Changed
- Improved Sharpe ratio calculation accuracy (#142)
```

---

## 🔄 Pull Request Process

### Before Submitting

**Checklist:**
- [ ] Code follows style guide (PEP 8)
- [ ] All tests pass (`pytest tests/`)
- [ ] Code coverage >80% for new code
- [ ] Documentation updated
- [ ] Changelog updated
- [ ] No linting errors (`flake8 src/`)
- [ ] Type hints added (`mypy src/`)
- [ ] Commit messages are clear and descriptive

### PR Template

```markdown
## Description
Brief description of changes

## Motivation and Context
Why is this change required? What problem does it solve?

## Type of Change
- [ ] Bug fix (non-breaking change which fixes an issue)
- [ ] New feature (non-breaking change which adds functionality)
- [ ] Breaking change (fix or feature that would cause existing functionality to change)
- [ ] Documentation update

## How Has This Been Tested?
Describe the tests you ran to verify your changes

## Screenshots (if applicable)
Add screenshots for UI changes

## Checklist
- [ ] My code follows the code style of this project
- [ ] I have updated the documentation accordingly
- [ ] I have added tests to cover my changes
- [ ] All new and existing tests passed
```

### Review Process

1. **Automated checks** run on PR submission
   - GitHub Actions CI/CD
   - Code coverage check
   - Linting and type checking

2. **Code review** by maintainers
   - At least 1 approval required
   - Address all review comments

3. **Merge**
   - Squash and merge for clean history
   - Delete branch after merge

---

## 🎯 Areas for Contribution

### High Priority

1. **Out-of-sample Validation UI** 
   - Train/test split selector in dashboard
   - Walk-forward analysis visualization

2. **Event Validation**
   - Mark known events on charts (COVID, elections)
   - Regime accuracy scoring

3. **Additional ML Models**
   - LSTM for temporal patterns
   - Transformer-based models

### Medium Priority

4. **Performance Optimization**
   - Parallel feature computation
   - Model training speedups

5. **Data Sources**
   - NSE API integration (replace yfinance)
   - Alternative data (news sentiment, macro indicators)

6. **Testing**
   - Increase coverage to >90%
   - Integration tests
   - Performance benchmarks

### Low Priority (Nice to Have)

7. **UI Enhancements**
   - Dark mode toggle
   - Custom color schemes
   - Mobile responsive design

8. **Localization**
   - Hindi language support
   - Regional number formatting

9. **Documentation**
   - Video tutorials
   - Blog post walkthroughs

---

## 💡 Contribution Ideas

### For Beginners

- Improve error messages
- Add more unit tests
- Fix typos in documentation
- Add code comments
- Improve logging

### For Intermediate

- Add new technical indicators
- Implement GMM enhancements
- Create visualization utilities
- Add data validation
- Improve performance

### For Advanced

- Implement LSTM model
- Add real-time data streaming
- Create portfolio optimization
- Build auto-rebalancing system
- Add options strategy recommendations

---

## 🏆 Recognition

Contributors will be recognized in:
- README.md acknowledgments section
- Contributors page on project website
- Release notes

---

## 📞 Getting Help

**Questions?**
- Open a [Discussion](https://github.com/shamiquekhan/Market-Regime-Detection-System/discussions)
- Join our Discord/Slack
- Email: shamiquekhan@example.com

**Found a bug?**
- Open an [Issue](https://github.com/shamiquekhan/Market-Regime-Detection-System/issues)
- Include steps to reproduce
- Attach error logs/screenshots

---

## 📜 License

By contributing, you agree that your contributions will be licensed under the MIT License.

---

**Thank you for contributing! 🎉**

Your time and expertise help make this project better for everyone.
