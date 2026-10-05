from langchain_core.tools import tool


@tool
def calculate_bmi(weight: float, height: float) -> float:
    """
    Calculate BMI using weight in kilograms and height in meters.
    """

    if weight <= 0 or height <= 0:
        raise ValueError("Weight and height must be greater than zero.")

    bmi = weight / (height * height)

    return round(bmi, 2)