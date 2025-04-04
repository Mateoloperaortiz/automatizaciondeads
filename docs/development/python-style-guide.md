# Python Style Guide for AdFlux

This document outlines the Python coding standards and best practices for the AdFlux project. Following these guidelines ensures code consistency, readability, and maintainability across the codebase.

## General Principles

- **Readability**: Code should be easy to read and understand
- **Simplicity**: Prefer simple solutions over complex ones
- **Consistency**: Follow established patterns and conventions
- **Maintainability**: Write code that is easy to maintain and extend
- **Testability**: Write code that is easy to test

## Code Style

### PEP 8

AdFlux follows the [PEP 8](https://www.python.org/dev/peps/pep-0008/) style guide for Python code. Key points include:

- Use 4 spaces for indentation (no tabs)
- Maximum line length of 88 characters (using Black's default)
- Use snake_case for variable and function names
- Use CamelCase for class names
- Use UPPER_CASE for constants
- Use descriptive names for variables, functions, and classes

### Imports

- Group imports in the following order, separated by a blank line:
  1. Standard library imports
  2. Related third-party imports
  3. Local application/library specific imports
- Within each group, imports should be in alphabetical order
- Use absolute imports rather than relative imports

Example:

```python
# Standard library imports
import datetime
import json
import os
from typing import List, Optional, Tuple

# Third-party imports
import flask
from flask import Flask, request
import pandas as pd
from sqlalchemy import Column, Integer, String

# Local application imports
from adflux.extensions import db
from adflux.models import JobOpening, Candidate
from adflux.utils import format_date
```

### Docstrings

Use Google-style docstrings for all modules, classes, and functions:

```python
def calculate_similarity(vector1: List[float], vector2: List[float]) -> float:
    """Calculate cosine similarity between two vectors.
    
    Args:
        vector1: First vector as a list of floats
        vector2: Second vector as a list of floats
        
    Returns:
        Cosine similarity as a float between -1 and 1
        
    Raises:
        ValueError: If vectors have different dimensions
    """
    if len(vector1) != len(vector2):
        raise ValueError("Vectors must have the same dimension")
    
    # Implementation...
    return similarity
```

### Type Hints

Use type hints for function parameters and return values:

```python
def get_job_openings(status: Optional[str] = None, 
                     limit: int = 10) -> List[JobOpening]:
    """Get job openings filtered by status.
    
    Args:
        status: Filter by job status (e.g., 'open', 'closed')
        limit: Maximum number of results to return
        
    Returns:
        List of JobOpening objects
    """
    query = JobOpening.query
    
    if status:
        query = query.filter_by(status=status)
    
    return query.limit(limit).all()
```

## Code Organization

### File Structure

- One class per file (with exceptions for closely related classes)
- Module names should be short, lowercase, and use underscores if necessary
- File names should match the main class or function they contain

### Function and Method Length

- Keep functions and methods focused on a single responsibility
- Aim for functions under 50 lines of code
- If a function is getting too long, consider breaking it into smaller functions

### Class Structure

- Follow this order for class methods:
  1. Class attributes
  2. `__init__` method
  3. Class methods
  4. Static methods
  5. Property methods
  6. Regular instance methods
  7. Special methods (e.g., `__str__`, `__repr__`)
  8. Inner classes

Example:

```python
class CandidateSegmenter:
    """Segments candidates based on their profiles."""
    
    # Class attributes
    DEFAULT_NUM_CLUSTERS = 5
    
    def __init__(self, num_clusters: int = DEFAULT_NUM_CLUSTERS):
        """Initialize the segmenter.
        
        Args:
            num_clusters: Number of clusters to create
        """
        self.num_clusters = num_clusters
        self.model = None
        self.preprocessor = None
    
    @classmethod
    def from_saved_model(cls, model_path: str) -> 'CandidateSegmenter':
        """Create a segmenter from a saved model.
        
        Args:
            model_path: Path to the saved model
            
        Returns:
            Initialized CandidateSegmenter
        """
        # Implementation...
        return instance
    
    @staticmethod
    def normalize_features(features: pd.DataFrame) -> pd.DataFrame:
        """Normalize features to have zero mean and unit variance.
        
        Args:
            features: DataFrame of features
            
        Returns:
            Normalized features
        """
        # Implementation...
        return normalized_features
    
    @property
    def is_trained(self) -> bool:
        """Check if the model is trained."""
        return self.model is not None
    
    def train(self, candidates: List[Candidate]) -> None:
        """Train the segmentation model.
        
        Args:
            candidates: List of candidate objects
        """
        # Implementation...
    
    def predict(self, candidates: List[Candidate]) -> List[int]:
        """Predict segments for candidates.
        
        Args:
            candidates: List of candidate objects
            
        Returns:
            List of segment IDs
        """
        # Implementation...
        return segments
    
    def __str__(self) -> str:
        """Return string representation."""
        return f"CandidateSegmenter(num_clusters={self.num_clusters})"
```

## Best Practices

### Error Handling

- Use specific exception types rather than catching all exceptions
- Provide informative error messages
- Log exceptions with appropriate context
- Handle exceptions at the appropriate level

Example:

```python
try:
    campaign = create_meta_campaign(ad_account_id, name, status, budget)
except FacebookRequestError as e:
    current_app.logger.error(
        f"Failed to create Meta campaign: {e.api_error_message}",
        extra={"ad_account_id": ad_account_id, "error_code": e.api_error_code}
    )
    raise MetaAPIError(f"Failed to create campaign: {e.api_error_message}")
except Exception as e:
    current_app.logger.error(f"Unexpected error creating Meta campaign: {str(e)}")
    raise
```

### Logging

- Use the appropriate log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
- Include relevant context in log messages
- Use structured logging with extra fields for easier filtering

Example:

```python
# Bad
logger.info("Campaign created")

# Good
logger.info(
    "Campaign created successfully",
    extra={
        "campaign_id": campaign.id,
        "platform": campaign.platform,
        "job_id": campaign.job_opening_id,
        "budget": campaign.daily_budget
    }
)
```

### Testing

- Write unit tests for all functions and methods
- Use pytest fixtures for test setup
- Mock external dependencies
- Aim for high test coverage, especially for critical components

Example:

```python
def test_calculate_similarity():
    # Test with identical vectors
    v1 = [1.0, 2.0, 3.0]
    v2 = [1.0, 2.0, 3.0]
    assert calculate_similarity(v1, v2) == 1.0
    
    # Test with orthogonal vectors
    v1 = [1.0, 0.0, 0.0]
    v2 = [0.0, 1.0, 0.0]
    assert calculate_similarity(v1, v2) == 0.0
    
    # Test with different dimensions
    v1 = [1.0, 2.0]
    v2 = [1.0, 2.0, 3.0]
    with pytest.raises(ValueError):
        calculate_similarity(v1, v2)
```

### Database Queries

- Use SQLAlchemy ORM for database operations
- Optimize queries to minimize database load
- Use eager loading to avoid N+1 query problems
- Use transactions for operations that modify multiple records

Example:

```python
# Bad - N+1 query problem
campaigns = Campaign.query.filter_by(status='active').all()
for campaign in campaigns:
    print(campaign.job_opening.title)  # This triggers a separate query for each campaign

# Good - Use eager loading
campaigns = Campaign.query.filter_by(status='active').options(
    joinedload(Campaign.job_opening)
).all()
for campaign in campaigns:
    print(campaign.job_opening.title)  # No additional queries
```

### Security

- Never store sensitive information (API keys, passwords) in code
- Use environment variables or a secure configuration system
- Validate and sanitize all user input
- Use parameterized queries to prevent SQL injection
- Follow the principle of least privilege

Example:

```python
# Bad
api_key = "sk_test_abcdefghijklmnopqrstuvwxyz"

# Good
api_key = os.environ.get("API_KEY")
if not api_key:
    raise ConfigurationError("API_KEY environment variable is not set")
```

## Tools and Enforcement

The following tools are used to enforce code style and quality:

- **Black**: Code formatter
- **isort**: Import sorter
- **flake8**: Linter
- **mypy**: Static type checker
- **pytest**: Testing framework

These tools are configured in the project's `setup.cfg` and `pyproject.toml` files.

## Pre-commit Hooks

Use pre-commit hooks to automatically check code before committing:

```bash
pip install pre-commit
pre-commit install
```

The pre-commit configuration is in `.pre-commit-config.yaml`.

## Continuous Integration

Code style and quality checks are run automatically on pull requests using GitHub Actions. Pull requests that do not pass these checks cannot be merged.

## Resources

- [PEP 8 -- Style Guide for Python Code](https://www.python.org/dev/peps/pep-0008/)
- [PEP 257 -- Docstring Conventions](https://www.python.org/dev/peps/pep-0257/)
- [PEP 484 -- Type Hints](https://www.python.org/dev/peps/pep-0484/)
- [Google Python Style Guide](https://google.github.io/styleguide/pyguide.html)
- [Flask Documentation](https://flask.palletsprojects.com/)
- [SQLAlchemy Documentation](https://docs.sqlalchemy.org/)
