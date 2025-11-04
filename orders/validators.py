def percentage_validator(value):
    if value<= 100 and value >= 0:
        return True
    else: 
        return "Value must be between 0 and 100"