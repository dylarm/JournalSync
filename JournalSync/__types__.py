from datetime import datetime
from typing import Dict, List, Any

# from jsonschema_typed import JSONSchema

# TODO: fix typing
# The API returns such a convoluted type of str, int, Dict, List, and None.
# Attempting to use JSONSchema, but here: (1) I can't alias it and NewType doesn't
# recognize it as a valid type, and (2) mypy complains that Type[JSONSchema] is
# not indexable. The two comments below are left as a reminder.

# SCHEMA_PATH = str(Path("./api_schema.json").absolute())
# APIResponse = JSONSchema[str(Path("./api_schema.json").absolute())]
Journal = Dict[datetime, Dict[str, List[str]]]
APIResponse = Dict[str, Any]  # ignoring the types that I don't need
Config = Dict[str, Any]
