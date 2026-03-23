import numpy as np

def predict_next(values):
    if len(values) < 3:
        return values[-1]

    x = np.arange(len(values))
    y = np.array(values)

    coeffs = np.polyfit(x, y, 1)
    prediction = np.polyval(coeffs, len(values))

    return round(prediction, 2)
