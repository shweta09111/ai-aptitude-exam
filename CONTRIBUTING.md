# Contributing to AI-Augmented Online Aptitude Exam System

Thank you for considering contributing to our project! We welcome contributions from the community and are grateful for your support.

## 📋 Code of Conduct

By participating in this project, you agree to maintain a respectful and collaborative environment. Please:

- Be respectful and considerate of others
- Welcome newcomers and help them get started
- Focus on constructive feedback
- Respect differing viewpoints and experiences

## 🚀 How to Contribute

### Reporting Bugs

If you find a bug, please create an issue with:

1. **Clear title**: Summarize the problem
2. **Description**: Detailed explanation of the issue
3. **Steps to reproduce**: How to recreate the bug
4. **Expected behavior**: What should happen
5. **Actual behavior**: What actually happens
6. **Environment**: OS, Python version, browser, etc.
7. **Screenshots**: If applicable

### Suggesting Features

We love new ideas! To suggest a feature:

1. Check if it's already been suggested in Issues
2. Create a new issue with the "feature request" label
3. Describe the feature and its benefits
4. Explain use cases and examples

### Pull Requests

1. **Fork the repository**
   ```bash
   git clone https://github.com/shweta09111/ai-aptitude-exam.git
   ```

2. **Create a feature branch**
   ```bash
   git checkout -b feature/YourFeatureName
   ```

3. **Make your changes**
   - Write clean, readable code
   - Follow PEP 8 style guidelines
   - Add comments for complex logic
   - Write docstrings for functions

4. **Test your changes**
   - Ensure all existing tests pass
   - Add new tests for new features
   - Test on multiple browsers (if frontend changes)

5. **Commit your changes**
   ```bash
   git add .
   git commit -m "Add: Brief description of your changes"
   ```

   Commit message format:
   - `Add:` for new features
   - `Fix:` for bug fixes
   - `Update:` for updates to existing features
   - `Refactor:` for code refactoring
   - `Docs:` for documentation changes

6. **Push to your fork**
   ```bash
   git push origin feature/YourFeatureName
   ```

7. **Create a Pull Request**
   - Go to the original repository
   - Click "New Pull Request"
   - Select your branch
   - Fill in the PR template
   - Wait for review

## 💻 Development Setup

### Prerequisites

- Python 3.11+
- Git
- Virtual environment tool

### Local Setup

```bash
# Clone your fork
git clone https://github.com/YOUR_USERNAME/ai-aptitude-exam.git
cd ai-aptitude-exam/project

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: .\venv\Scripts\Activate.ps1

# Install dependencies
pip install -r requirements_local.txt

# Run the application
python app.py
```

### Running Tests

```bash
# Run all tests
python -m pytest

# Run specific test file
python -m pytest tests/test_question_generator.py

# Run with coverage
python -m pytest --cov=.
```

## 📝 Coding Standards

### Python Style Guide

Follow PEP 8 guidelines:

```python
# Good
def generate_question(context: str, max_length: int = 100) -> dict:
    """
    Generate a question from given context.
    
    Args:
        context: Text context for generation
        max_length: Maximum question length
        
    Returns:
        Dictionary containing question data
    """
    # Implementation
    pass

# Bad
def gen_q(c,ml=100):
    # No docstring, unclear variable names
    pass
```

### File Organization

```
project/
├── app.py                 # Main application
├── models/               # Database models
├── ml_models/           # ML-related code
│   ├── question_generator.py
│   └── bert_analyzer.py
├── api/                 # API endpoints
├── templates/           # HTML templates
├── static/             # CSS, JS, images
├── tests/              # Test files
└── docs/               # Documentation
```

### Documentation

- Add docstrings to all functions and classes
- Update README.md for major changes
- Comment complex algorithms
- Keep comments up-to-date

## 🧪 Testing Guidelines

### Writing Tests

```python
def test_question_generation():
    """Test question generation with valid context."""
    generator = QuestionGenerator()
    context = "Python is a programming language."
    questions = generator.generate_questions_from_context(context, max_questions=3)
    
    assert len(questions) > 0
    assert all('question' in q for q in questions)
```

### Test Coverage

- Aim for >80% code coverage
- Test edge cases
- Test error handling
- Mock external dependencies

## 🎯 Areas for Contribution

We especially welcome contributions in:

- **ML Models**: Improving question generation quality
- **UI/UX**: Enhancing user interface design
- **Testing**: Adding comprehensive test coverage
- **Documentation**: Improving guides and tutorials
- **Performance**: Optimizing slow operations
- **Accessibility**: Making the platform more accessible
- **Internationalization**: Adding multi-language support

## 📚 Resources

- [Flask Documentation](https://flask.palletsprojects.com/)
- [Transformers Documentation](https://huggingface.co/docs/transformers)
- [OpenCV Documentation](https://docs.opencv.org/)
- [PEP 8 Style Guide](https://pep8.org/)

## ❓ Questions?

If you have questions:

1. Check existing issues and discussions
2. Create a new discussion in GitHub Discussions
3. Reach out via GitHub Issues

## 🙏 Thank You!

Every contribution, no matter how small, is valued and appreciated. Thank you for helping make this project better!

---

**Happy Coding! 🚀**
