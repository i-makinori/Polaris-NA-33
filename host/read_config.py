# -*- coding: utf-8 -*-

import yaml

# Read Config YAML
class YAMLParseError(Exception):
    """Custom Error for Parsing Configure File"""
    pass


def validate_config(conf, required_schemas):
    """
    Main interface for configuration validation.
    The actual recursive logic is delegated to the auxiliary function.
    """

    # Delegate to the auxiliary function
    return _validate_config_aux(conf, required_schemas, selections="")

def _validate_config_aux(conf, schema, selections):
    """
    Auxiliary recursive function to traverse and validate the config tree.
    """
    for key, expected in schema.items():
        current_selections = f"{selections}.{key}" if selections else key

        # 1. Existence check: Verify the key exists in the provided config
        if key not in conf:
            raise ValueError(f"Configuration Error: Missing required key '{current_selections}'.")

        actual_val = conf[key]

        # 2. Recursive step: If the expected value is a dict, dive deeper (Vertical traversal)
        if isinstance(expected, dict):
            if not isinstance(actual_val, dict):
                raise TypeError(f"Configuration Error: '{current_selections}' must be a dictionary.")
            _validate_config_aux(actual_val, expected, current_selections)

        # 3. Base case: Validate the leaf node's type
        else:
            if not isinstance(actual_val, expected):
                raise TypeError(
                    f"Configuration Error: '{current_selections}' must be of type {expected.__name__}. "
                    f"Got {type(actual_val).__name__} instead."
                )
    return True

def read_config_yaml(config_path, required_schemas):
    # Open config file and Valuate to conf
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            conf = yaml.safe_load(f)
    except Exception as e:
        print(f"Config Error: {e}")
        sys.exit(1)

    # Validate conf
    validate_config(conf, required_schemas)

    # Return
    return conf
