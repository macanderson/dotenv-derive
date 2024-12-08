"""

dotenv-derive
=============

Add @dotenv to the class you want to derive environment variables from and
automatically load environment variables from a .env file and map them to
class fields.

author: Mac Anderson (mac@macanderson.com), https://github.com/macanderson
github: https://github.com/macanderson/dotenv-derive

Feel free to contribute to this project!  Submit an issue or pull request.

"""

import os
from functools import wraps
from pathlib import Path
from typing import Any, Dict, Optional, TypeVar

T = TypeVar("T")


def dotenv(dotenv_file: str = ".env", traverse: bool = True, coerce_values: bool = True, extras: str = "ignore"):
    """
    Decorator that automatically loads environment variables from
    a .env file and maps them to class fields.

    This decorator will try to import `load_dotenv`
    from `python-dotenv` if available.  No dependency is
    installed by default.

    Parameters
    ----------
    dotenv_file : str
        Name of the .env file to search for. Defaults to ".env".
        File name must include extension.

    traverse : bool
        Whether to traverse parent directories looking for the file.
        Defaults to True.

    coerce_values : bool
        Whether to coerce environment variable values to the expected types.
        Defaults to True.

    extras : str
        One of: "ignore", "include", "exclude". Whether to include additional
        environment variables in the class.  Defaults to "ignore".  If
        "include", the class will have a field named 'extras' that is a
        dictionary containing the additional environment variables in
        key-value pairs.  If "exclude", the class will not have a field named
        'extras' and will throw an error if any additional environment
        variables are found.

    load_dotenv : bool
        Whether to disable the import of `load_dotenv` from the
        `python-dotenv` package. Defaults to True.  **IMPORTANT**: If a file
        name is provided, load_dotenv will be called with the file name
        provided.

    Returns
    -------
    type[T]
        Decorated class with environment variables mapped to fields

    Raises
    ------
    FileNotFoundError
        If the .env file is not found and traverse is False

    MultipleFilesFoundError
        If multiple .env files are found in the search path

    ValueError
        If an environment variable cannot be converted to the expected type


    Example .env file
    ------------------
    # Example showing how environment variables can collide if not uniquely
    # named
    # Both of these would map to a class field named 'instagram_url':
    instagram_url="https://www.instagram.com"
    INSTAGRAM_URL="https://www.instagram.com"  # overrides the previous value

    # To avoid collisions, use unique names that match your class fields
    # exactly:
    instagram_profile_url="https://www.instagram.com/profile"
    instagram_api_url="https://api.instagram.com"

    ```python
    # Environment variable examples in .env file:

    # The decorator will match environment variables case-insensitively and
    # with various naming conventions.

    # For a class field named DB_HOST, any of these formats will match:

    # Snake case (recommended)
    DB_HOST="localhost"
    db_host="localhost"

    # Camel case
    dbHost="localhost"
    DbHost="localhost"

    # No separator
    DBHOST="localhost"
    dbhost="localhost"

    # Mixed formats (not recommended but supported)
    Db_Host="localhost"

    # The first matching environment variable found will be used.
    # Snake case with consistent casing is recommended for clarity.
    ```
    ```

    ```python
    # This will not call load_dotenv()
    @dotenv(dotenv_file="app.env", load_dotenv=False)
    class Config:
        DB_HOST: str  # Will load DB_HOST from .env
        # possible matches: db_host, dbHost, DbHost, db_host, dbHost, Db_Host,
        # DB_HOST
        API_KEY: str  # Will load API_KEY from .env

    ```
    """
    def decorator(cls: type[T]) -> type[T]:
        """
        Decorator that loads environment variables from a .env file and maps
        them to class fields.

        Parameters
        ----------
        cls : type[T]
            The class to decorate

        Returns
        -------
        type[T]
            The decorated class
        """
        # Get the directory of the module defining the decorated class
        module_dir = Path(cls.__module__).parent

        # Find .env file by traversing up directories
        env_path: Optional[Path] = None
        current_dir = module_dir if traverse else Path.cwd()

        while current_dir != current_dir.parent:
            test_path = current_dir / dotenv_file
            if test_path.exists():
                env_path = test_path
                break
            if not traverse:
                break
            current_dir = current_dir.parent

        # Try to load dotenv if python-dotenv is available and not disabled
        try:
            from dotenv import load_dotenv

            if env_path and load_dotenv:
                load_dotenv(env_path)
        except ImportError:
            pass

        def normalize_name(name: str) -> str:
            """Convert name to snake_case for comparison"""
            # Remove any underscores and convert to lowercase
            name = name.lower()
            # Insert underscore before capital letters
            normalized = "".join("_" + c.lower() if c.isupper() else c for c in name)
            # Remove leading underscore if present and any double underscores
            return normalized.lstrip("_").replace("__", "_")

        def find_matching_env_var(field_name: str) -> Optional[str]:
            """Find environment variable matching field name, ignoring case and format"""
            normalized_field = normalize_name(field_name)
            # Track matched env vars to exclude from extras
            matched_vars: set[str] = set()
            for env_var in os.environ:
                if normalize_name(env_var) == normalized_field:
                    matched_vars.add(env_var)
                    return os.environ[env_var]
            # Store unmatched vars in extras
            extras_dict: Dict[str, str | bool | int | float | None] = {
                k: (
                    coerce_value(v, str)
                    if v.replace(".", "", 1).isdigit() and "." in v
                    else coerce_value(v, int)
                    if v.isdigit()
                    else coerce_value(v, bool)
                    if v.lower() in ("true", "false", "1", "0", "yes", "no", "on", "off")
                    else None
                    if v.lower() in ("none", "null")
                    else v
                )
                for k, v in os.environ.items()
                if k not in matched_vars
            }
            setattr(cls, "extras", extras_dict)
            return None

        def coerce_value(value: str, target_type: type) -> Any:
            """Coerce string value to target type"""
            if target_type is bool:
                return value.lower() in ("true", "1", "yes", "on")
            try:
                return target_type(value)
            except (ValueError, TypeError):
                return None

        # Create init to map env vars to fields
        @wraps(cls.__init__)
        def __init__(self) -> None:
            for field_name, field_type in cls.__annotations__.items():
                env_value = find_matching_env_var(field_name)
                if env_value is not None:
                    coerced_value = coerce_value(env_value, field_type)
                    setattr(self, field_name, coerced_value)
                else:
                    setattr(self, field_name, None)

        cls.__init__ = __init__
        return cls

    return decorator


__all__ = ["dotenv"]
