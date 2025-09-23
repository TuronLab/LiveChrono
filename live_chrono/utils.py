
def validate_time_format(display_format: str):
    """
    Validates that the format string does not skip time units.
    Allowed tokens: %D, %H, %M, %S, %f, %ms
    Rules:
        - Units must form a contiguous hierarchy.
        - Milliseconds (%f or %ms) can only appear if seconds (%S) are present.
    Raises ValueError if invalid.
    """
    time_units = ["D", "H", "M", "S", "f"]
    token_map = {"D": "%D", "H": "%H", "M": "%M", "S": "%S"}
    ms_tokens = ["%f", "%ms"]

    # Detect which units are present
    present = []
    for unit in time_units:
        if unit == "f":
            if any(token in display_format for token in ms_tokens):
                present.append(unit)
        else:
            if token_map[unit] in display_format:
                present.append(unit)

    if not present:
        return  # nothing to validate

    # Check that units are contiguous in the hierarchy
    first_idx = time_units.index(present[0])
    for i, unit in enumerate(present):
        expected_unit = time_units[first_idx + i]
        if unit != expected_unit:
            raise ValueError(
                f"Invalid format: units skip levels. Found '{unit}' after "
                f"'{present[i-1] if i>0 else 'start'}'"
            )


