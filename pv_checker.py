#!/usr/bin/env python3

import re
import sys
from epics import caget
from braceexpand import braceexpand
import operator


# Map of operators and dynamic regex creation
OPERATORS = {
    "==": operator.eq,
    "!=": operator.ne,
    "<": operator.lt,
    "<=": operator.le,
    ">": operator.gt,
    ">=": operator.ge,
}

OPERATORS_PATTERN = "|".join(re.escape(op) for op in OPERATORS.keys())


def parse_condition(line):
    match = re.match(rf"(.+?)\s*({OPERATORS_PATTERN})\s*(.+)", line)
    if not match:
        raise ValueError(f"Invalid syntax: {line}")
    pv_pattern, operator, value = match.groups()

    if value.isdigit():
        value = int(value)  # Convert to integer
    elif '.' in value and value.replace('.', '', 1).isdigit():
        value = float(value)  # Convert to float
    elif (value.startswith('"') and value.endswith('"')) or (value.startswith("'") and value.endswith("'")):
        value = value[1:-1]  # Strip surrounding quotes
    else:
        raise ValueError(f"Error parsing value: {value}.")
    return pv_pattern, operator, value


def expand_pvs(pattern):
    return list(braceexpand(pattern))


def check_pv_condition(pv_name, operator, expected_value):
    # ANSI color codes
    GREEN = "\033[92m"
    RED = "\033[91m"
    RESET = "\033[0m"

    # Resolve the operator to its corresponding function
    operator_func = OPERATORS.get(operator)
    if operator_func is None:
        raise ValueError(f"Unknown operator: {operator}")

    pv_value = caget(pv_name)
    if pv_value is None:
        # Couldn't retrieve the PV
        return "Error", None, f"{operator} {expected_value}"

    try:
        # Compare using the resolved operator function
        condition_met = operator_func(pv_value, expected_value)
        result = f"{GREEN}Pass{RESET}" if condition_met else f"{RED}Fail{RESET}"
        return result, pv_value, f"{operator} {expected_value}"

    except Exception as e:
        return f"Error: {e}", pv_value, f"{operator} {expected_value}"


def process_pvchk_file(filename):
    with open(filename, 'r') as file:
        lines = file.readlines()

    results = []
    for line in lines:
        line = line.strip()
        if not line or line.startswith('#'):  # Skip comments or empty lines
            continue
        try:
            pv_pattern, operator, expected_value = parse_condition(line)
            expanded_pvs = expand_pvs(pv_pattern)
            for pv_name in expanded_pvs:
                result, actual, condition = check_pv_condition(
                    pv_name, operator, expected_value)
                results.append((pv_name, result, actual, condition))
        except Exception as e:
            results.append((line, f"Error: {e}", None, None))
    return results


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python pv_checker.py <filename>")
        sys.exit(1)

    filename = sys.argv[1]

    results = process_pvchk_file(filename)
    print(f"{'PV Name':<50} {'Result':<10} {'Actual':<20} {'Expected':<20}")
    print("-" * 100)
    for pv, result, actual, expected in results:
        print(f"{pv:<50} {result:<10} {repr(actual):<20} {expected:<20}")
