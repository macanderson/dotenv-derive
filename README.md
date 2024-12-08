# dotenv-derive

[![PyPI version](https://badge.fury.io/py/dotenv-derive.svg)](https://badge.fury.io/py/dotenv-derive)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

**A simple and lightweight environment variable loader for Python**, designed to streamline the process of mapping environment variables to class fields without the overhead of complex configurations.

## Welcome to `dotenv-derive`!

`dotenv-derive` provides a decorator that automatically loads environment variables from a `.env` file and maps them to class fields. The goal is to make this process as simple as possible while still supporting a variety of use cases.

## Features

- Automatic loading of environment variables into class fields.
- Supports various naming conventions (snake_case, camelCase, etc.).
- Optional coercion of values to expected types.
- Configurable inclusion or exclusion of extra environment variables.
- Supports Python 3.11+.

## Installation

```bash
pip install dotenv-derive
```

## Requirements

- Python 3.11 or higher
- Optionally, the `python-dotenv` package to enable the `load_dotenv` argument (installed automatically).

## Usage

To use `dotenv-derive`, import the `dotenv` decorator and apply it to your configuration class. Environment variables defined in your `.env` file or the system environment will be automatically mapped to the class fields.

```python
from dotenv_derive import dotenv

@dotenv(dotenv_file="app.env", load_dotenv=True)
class Config:
    DB_HOST: str
    API_KEY: str

config = Config()
print(config.DB_HOST)
print(config.API_KEY)
```

### Example `.env` file

```dotenv
DB_HOST="localhost"
API_KEY="your-api-key"
```

## Decorator Parameters

- **dotenv_file** *(str)*: Name of the `.env` file to search for. Defaults to `".env"`. The file name must include the extension.
- **traverse** *(bool)*: Whether to traverse parent directories looking for the file. Defaults to `True`.
- **coerce_values** *(bool)*: Whether to coerce environment variable values to the expected types. Defaults to `True`.
- **extras** *(str)*: One of: `"ignore"`, `"include"`, `"exclude"`. Determines how to handle additional environment variables not mapped to class fields. Defaults to `"ignore"`.
  - `"ignore"`: Ignores extra variables.
  - `"include"`: Includes extra variables in a dictionary assigned to the `extras` attribute.
  - `"exclude"`: Raises an error if extra variables are found.
- **load_dotenv** *(bool)*: Whether to import and use `load_dotenv` from the `python-dotenv` package. Defaults to `True`. If a file name is provided, `load_dotenv` will be called with the provided file name.

### Returns

- **type[T]**: Decorated class with environment variables mapped to fields.

### Raises

- **FileNotFoundError**: If the `.env` file is not found and `traverse` is `False`.
- **ValueError**: If an environment variable cannot be converted to the expected type.

## Environment Variable Matching

The decorator matches environment variables case-insensitively and supports various naming conventions. For a class field named `DB_HOST`, any of these formats will match:

```dotenv
# Snake case (recommended)
DB_HOST="localhost"
db_host="localhost"

# Camel case
dbHost="localhost"
DbHost="localhost"

# No separator
DBHOST="localhost"
dbhost="localhost"

# Mixed formats
Db_Host="localhost"
```

The first matching environment variable found will be used. Snake case with consistent casing is recommended for clarity.

## Advanced Usage

### Handling Extra Environment Variables

By setting the `extras` parameter to `"include"`, you can capture any additional environment variables not explicitly mapped to class fields:

```python
from dotenv_derive import dotenv

@dotenv(extras="include")
class Config:
    DB_HOST: str

config = Config()
print(config.DB_HOST)
print(config.extras)  # Dictionary of extra environment variables
```

### Disabling `load_dotenv`

If you prefer to manually manage the loading of environment variables or want to avoid using `python-dotenv`, you can disable `load_dotenv`:

```python
from dotenv_derive import dotenv

@dotenv(load_dotenv=False)
class Config:
    DB_HOST: str

# Manually load environment variables here if needed
```

## Contributing

Contributions are welcome! Please open an issue or submit a pull request on [GitHub](https://github.com/macanderson/dotenv-derive). For major changes, please open an issue first to discuss what you would like to change.

Before contributing, please ensure you have read our [Contributing Guidelines](CONTRIBUTING.md) and adhere to the [Code of Conduct](CODE_OF_CONDUCT.md).

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Testing

To run the tests, install the development dependencies and run `pytest`:

```bash
pip install -r requirements-dev.txt
pytest
```

## Changelog

See the [CHANGELOG](CHANGELOG.md) for a detailed list of changes and updates.

## Acknowledgments

- [python-dotenv](https://github.com/theskumar/python-dotenv) for inspiration on environment variable loading.
- All contributors and users for their support.

---

Feel free to contact me if you have any questions or suggestions.

Thank you for using `dotenv-derive`!

