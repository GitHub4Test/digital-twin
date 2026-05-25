import logging
import numpy as np

logger = logging.getLogger(__name__)

def predict_next(values):
    logger.debug(f"Predicting next value with {len(values)} historical data points")
    
    if len(values) < 3:
        logger.info(f"Insufficient data for prediction ({len(values)} points), returning last value")
        return values[-1]

    x = np.arange(len(values))
    y = np.array(values)

    coeffs = np.polyfit(x, y, 1)
    prediction = np.polyval(coeffs, len(values))
    result = round(prediction, 2)
    
    logger.info(f"Predicted next value: {result}")
    return result
