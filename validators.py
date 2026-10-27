import math
import re
from datetime import datetime, date


EMAIL_PATTERN = re.compile(
    r"^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$"
)



def validate_email(email):
    if not email:
        return False

    email = email.strip()
    pattern = r"^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$"

    return re.fullmatch(pattern, email) is not None


def validate_patient(form_data):
    errors = []
    cleaned = {}

    full_name = str(form_data.get("full_name", "")).strip()
    email = str(form_data.get("email", "")).strip()
    dob_input = str(form_data.get("dob", "")).strip()

    if not full_name:
        errors.append("Full name is required.")
    elif len(full_name) > 100:
        errors.append("Full name must not exceed 100 characters.")
    else:
        cleaned["full_name"] = full_name
    if not EMAIL_PATTERN.fullmatch(email):
        errors.append("Invalid email address.")
    else:
        cleaned["email"] = email

    parsed_dob = None
    for date_format in ("%d/%m/%Y", "%d.%m.%Y"):
        try:
            parsed_dob = datetime.strptime(dob_input, date_format).date()
            break
        except ValueError:
            continue

    if parsed_dob is None:
        errors.append(
            "Date of birth must be a valid date in dd/mm/yyyy format."
        )
    elif parsed_dob > date.today():
        errors.append("Date of birth cannot be in the future.")
    else:
        cleaned["dob"] = parsed_dob.strftime("%d/%m/%Y")

    numeric_fields = {
        "glucose": "Glucose",
        "haemoglobin": "Haemoglobin",
        "cholesterol": "Cholesterol",
    }

    for field, label in numeric_fields.items():
        value = str(form_data.get(field, "")).strip()
        try:
            number = float(value)
            if not math.isfinite(number):
                raise ValueError
            if number <= 0:
                errors.append(f"{label} must be greater than zero.")
            elif number > 100000:
                errors.append(f"{label} value is too large.")
            else:
                cleaned[field] = number
        except (ValueError, TypeError):
            errors.append(f"{label} must be a valid numeric value.")

    return cleaned, errors
