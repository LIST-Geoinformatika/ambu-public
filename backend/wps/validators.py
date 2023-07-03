import json
from django.core.exceptions import ValidationError


def validate_monthly_json_values(value):
    # Check if the value is a valid JSON object
    try:
        json.dumps(value)
    except (TypeError, ValueError):
        raise ValidationError("Invalid JSON format")

    json_data = value

    # Check if the JSON object contains exactly 12 months
    if len(json_data) != 12:
        raise ValidationError("The JSON object should contain 12 months")

    # Check if the JSON object contains valid month values
    for month in range(1, 13):
        month_str = str(month)
        if month_str not in json_data.keys():
            raise ValidationError(f"Missing value for month {month}")

        value = json_data[month_str]
        if not isinstance(value, (int, float)) or value < 0:
            raise ValidationError(f"Invalid value for month {month}")


def validate_point_within_water_body(value):
    water_body = value.water_body

    if not water_body:
        return  # Skip validation if water_body is not set

    # Check if the geom is within the buffer200 of the related water_body
    if not water_body.buffer200.contains(value.geom):
        raise ValidationError("The geom should be within the buffer200 of the related WaterCourse")
