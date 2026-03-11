"""
Predictive Alert Engine
SPRINT 10 - AGENT 3: Predictive Alerting

Features:
- Anomaly prediction using historical patterns
- Threshold breach forecasting
- Alert scoring and prioritization
- Multi-factor analysis
- ML-based predictions (linear regression, moving average)
"""
from typing import List, Dict, Optional, Tuple
from datetime import datetime, timedelta
from decimal import Decimal
import logging
from dataclasses import dataclass
from statistics import mean, stdev
import math

logger = logging.getLogger(__name__)


@dataclass
class Prediction:
    """Prediction result"""
    predicted_value: float
    confidence: float  # 0.0 to 1.0
    threshold_breach_probability: float  # 0.0 to 1.0
    prediction_time: datetime
    predicted_for: datetime
    factors: Dict[str, any]


@dataclass
class Alert:
    """Alert with priority scoring"""
    alert_id: str
    alert_type: str  # anomaly, threshold_breach, trend_warning
    severity: str  # info, warning, critical
    priority_score: float  # 0.0 to 100.0
    message: str
    predicted_value: float
    threshold_value: Optional[float]
    factors: Dict[str, any]
    created_at: datetime


class PredictiveAlertEngine:
    """
    Predictive alerting engine for proactive monitoring

    Uses multiple prediction methods:
    - Linear regression for trending data
    - Moving average for smoothed predictions
    - Standard deviation for anomaly detection
    - Multi-factor scoring for alert prioritization
    """

    def __init__(self):
        self.prediction_window_hours = 24  # Predict 24 hours ahead
        self.historical_window_days = 7  # Use 7 days of history
        self.anomaly_threshold_std = 2.5  # 2.5 standard deviations = anomaly
        self.confidence_threshold = 0.7  # Minimum confidence for alerts

    def predict_threshold_breach(
        self,
        historical_data: List[Dict[str, any]],
        threshold_value: float,
        metric_name: str,
    ) -> Optional[Prediction]:
        """
        Predict if a threshold will be breached in the near future

        Args:
            historical_data: List of historical data points with 'timestamp' and 'value'
            threshold_value: Threshold to check against
            metric_name: Name of the metric being predicted

        Returns:
            Prediction if breach is likely, None otherwise
        """
        if len(historical_data) < 10:
            logger.warning(f"Insufficient data for prediction: {len(historical_data)} points")
            return None

        try:
            # Sort by timestamp
            sorted_data = sorted(historical_data, key=lambda x: x['timestamp'])

            # Extract values and timestamps
            values = [float(d['value']) for d in sorted_data]
            timestamps = [d['timestamp'] for d in sorted_data]

            # Calculate trend using linear regression
            predicted_value, confidence = self._linear_regression_predict(
                values, self.prediction_window_hours
            )

            # Calculate breach probability
            breach_probability = self._calculate_breach_probability(
                predicted_value, threshold_value, values
            )

            # Calculate prediction time
            last_timestamp = timestamps[-1]
            predicted_for = last_timestamp + timedelta(hours=self.prediction_window_hours)

            return Prediction(
                predicted_value=predicted_value,
                confidence=confidence,
                threshold_breach_probability=breach_probability,
                prediction_time=datetime.utcnow(),
                predicted_for=predicted_for,
                factors={
                    'metric_name': metric_name,
                    'threshold_value': threshold_value,
                    'data_points': len(values),
                    'trend': 'increasing' if predicted_value > values[-1] else 'decreasing',
                }
            )

        except Exception as e:
            logger.error(f"Error predicting threshold breach: {str(e)}")
            return None

    def detect_anomalies(
        self,
        historical_data: List[Dict[str, any]],
        current_value: float,
    ) -> Tuple[bool, float, Dict[str, any]]:
        """
        Detect if current value is an anomaly based on historical patterns

        Args:
            historical_data: List of historical data points with 'value'
            current_value: Current value to check

        Returns:
            Tuple of (is_anomaly, anomaly_score, factors)
        """
        if len(historical_data) < 5:
            return False, 0.0, {}

        try:
            values = [float(d['value']) for d in historical_data]

            # Calculate statistics
            avg = mean(values)
            std = stdev(values) if len(values) > 1 else 0.0

            if std == 0:
                # No variation in data
                is_anomaly = current_value != avg
                anomaly_score = abs(current_value - avg)
            else:
                # Calculate z-score
                z_score = abs((current_value - avg) / std)
                is_anomaly = z_score > self.anomaly_threshold_std
                anomaly_score = min(z_score / self.anomaly_threshold_std, 1.0) * 100

            factors = {
                'mean': avg,
                'std_dev': std,
                'z_score': z_score if std > 0 else 0,
                'threshold_std': self.anomaly_threshold_std,
                'deviation_percent': ((current_value - avg) / avg * 100) if avg != 0 else 0,
            }

            return is_anomaly, anomaly_score, factors

        except Exception as e:
            logger.error(f"Error detecting anomaly: {str(e)}")
            return False, 0.0, {}

    def create_alert(
        self,
        alert_type: str,
        metric_name: str,
        current_value: float,
        prediction: Optional[Prediction] = None,
        anomaly_score: Optional[float] = None,
        threshold_value: Optional[float] = None,
    ) -> Alert:
        """
        Create prioritized alert

        Args:
            alert_type: Type of alert (anomaly, threshold_breach, trend_warning)
            metric_name: Name of the metric
            current_value: Current value
            prediction: Prediction result (if applicable)
            anomaly_score: Anomaly score (if applicable)
            threshold_value: Threshold value (if applicable)

        Returns:
            Alert with priority scoring
        """
        # Calculate priority score (0-100)
        priority_score = self._calculate_priority_score(
            alert_type, current_value, prediction, anomaly_score, threshold_value
        )

        # Determine severity
        if priority_score >= 80:
            severity = 'critical'
        elif priority_score >= 50:
            severity = 'warning'
        else:
            severity = 'info'

        # Build message
        if alert_type == 'anomaly':
            message = (
                f"Anomaly detected in {metric_name}. "
                f"Current value: {current_value:.2f}, "
                f"Anomaly score: {anomaly_score:.1f}%"
            )
        elif alert_type == 'threshold_breach':
            message = (
                f"Threshold breach predicted for {metric_name}. "
                f"Predicted value: {prediction.predicted_value:.2f}, "
                f"Threshold: {threshold_value:.2f}, "
                f"Breach probability: {prediction.threshold_breach_probability * 100:.1f}%"
            )
        elif alert_type == 'trend_warning':
            message = (
                f"Concerning trend detected in {metric_name}. "
                f"Current value: {current_value:.2f}"
            )
        else:
            message = f"Alert for {metric_name}: {current_value:.2f}"

        factors = {
            'metric_name': metric_name,
            'alert_type': alert_type,
        }

        if prediction:
            factors.update(prediction.factors)
        if anomaly_score is not None:
            factors['anomaly_score'] = anomaly_score

        return Alert(
            alert_id=str(uuid.uuid4()),
            alert_type=alert_type,
            severity=severity,
            priority_score=priority_score,
            message=message,
            predicted_value=prediction.predicted_value if prediction else current_value,
            threshold_value=threshold_value,
            factors=factors,
            created_at=datetime.utcnow(),
        )

    def _linear_regression_predict(
        self, values: List[float], hours_ahead: int
    ) -> Tuple[float, float]:
        """
        Simple linear regression prediction

        Args:
            values: Historical values
            hours_ahead: Hours to predict ahead

        Returns:
            Tuple of (predicted_value, confidence)
        """
        n = len(values)
        if n < 2:
            return values[-1], 0.5

        # Simple linear regression: y = mx + b
        x = list(range(n))
        x_mean = mean(x)
        y_mean = mean(values)

        # Calculate slope (m)
        numerator = sum((x[i] - x_mean) * (values[i] - y_mean) for i in range(n))
        denominator = sum((x[i] - x_mean) ** 2 for i in range(n))

        if denominator == 0:
            return values[-1], 0.5

        m = numerator / denominator
        b = y_mean - m * x_mean

        # Predict for future point
        future_x = n + hours_ahead
        predicted_value = m * future_x + b

        # Calculate R-squared for confidence
        y_pred = [m * xi + b for xi in x]
        ss_res = sum((values[i] - y_pred[i]) ** 2 for i in range(n))
        ss_tot = sum((values[i] - y_mean) ** 2 for i in range(n))

        r_squared = 1 - (ss_res / ss_tot) if ss_tot != 0 else 0
        confidence = max(0.0, min(1.0, r_squared))

        return predicted_value, confidence

    def _calculate_breach_probability(
        self, predicted_value: float, threshold_value: float, historical_values: List[float]
    ) -> float:
        """
        Calculate probability of threshold breach

        Args:
            predicted_value: Predicted value
            threshold_value: Threshold to check
            historical_values: Historical values for variance calculation

        Returns:
            Breach probability (0.0 to 1.0)
        """
        # If predicted value already exceeds threshold
        if predicted_value >= threshold_value:
            return 1.0

        # Calculate how close to threshold
        distance = threshold_value - predicted_value
        avg = mean(historical_values)
        std = stdev(historical_values) if len(historical_values) > 1 else 0.1

        # Z-score based probability
        z_score = distance / std if std > 0 else 0
        probability = 1.0 / (1.0 + math.exp(z_score))  # Sigmoid function

        return probability

    def _calculate_priority_score(
        self,
        alert_type: str,
        current_value: float,
        prediction: Optional[Prediction],
        anomaly_score: Optional[float],
        threshold_value: Optional[float],
    ) -> float:
        """
        Calculate alert priority score (0-100)

        Factors:
        - Alert type weight
        - Breach probability
        - Anomaly score
        - Confidence level
        - Proximity to threshold
        """
        score = 0.0

        # Base score by alert type
        type_weights = {
            'threshold_breach': 30,
            'anomaly': 25,
            'trend_warning': 15,
        }
        score += type_weights.get(alert_type, 10)

        # Add prediction factors
        if prediction:
            score += prediction.threshold_breach_probability * 40
            score += prediction.confidence * 20

        # Add anomaly factors
        if anomaly_score is not None:
            score += min(anomaly_score, 30)

        # Add proximity factor
        if threshold_value is not None:
            proximity = abs(current_value - threshold_value) / threshold_value
            score += max(0, 10 - proximity * 10)

        return min(score, 100.0)


# Module imports
import uuid
