"""
Trend Analysis Service for Multi-Report Parameter Comparison

This service analyzes parameter values across multiple reports to detect
trends (Improving, Worsening, Stable) and generate plain-language summaries.

Requirements: 8.1-8.8
"""

import logging
from typing import List, Optional, Dict, Any, Tuple
from datetime import datetime
from dataclasses import dataclass
from enum import Enum

logger = logging.getLogger(__name__)


class TrendDirection(Enum):
    """Trend direction classification."""
    IMPROVING = "Improving"
    WORSENING = "Worsening"
    STABLE = "Stable"
    INSUFFICIENT_DATA = "Insufficient Data"


@dataclass
class DataPoint:
    """Single data point in a trend."""
    report_id: str
    date: datetime
    value: float
    unit: str
    risk_level: str
    normal_range: Optional[Tuple[float, float]] = None


@dataclass
class TrendAnalysis:
    """Analysis result for a parameter trend."""
    parameter_name: str
    data_points: List[DataPoint]
    trend_direction: TrendDirection
    change_percent: float
    summary: str
    distance_from_normal_first: float
    distance_from_normal_last: float


class TrendAnalysisService:
    """
    Service for analyzing parameter trends across multiple reports.
    
    This service compares parameter values chronologically to detect
    improvements, deteriorations, or stability over time.
    """
    
    def __init__(self, stable_threshold: float = 5.0):
        """
        Initialize the Trend Analysis Service.
        
        Args:
            stable_threshold: Percentage change threshold for "Stable" classification
        """
        self.stable_threshold = stable_threshold
        logger.info(f"Trend Analysis Service initialized (stable threshold: {stable_threshold}%)")
    
    def analyze_parameter_trend(
        self,
        parameter_name: str,
        reports_data: List[Dict[str, Any]]
    ) -> Optional[TrendAnalysis]:
        """
        Analyze trend for a single parameter across multiple reports.
        
        Requirements: 8.1, 8.2, 8.3, 8.4, 8.5, 8.7, 8.8
        
        Args:
            parameter_name: Name of the parameter to analyze
            reports_data: List of report dictionaries with parameters
        
        Returns:
            TrendAnalysis object or None if insufficient data
        """
        # Extract data points for this parameter
        data_points = self._extract_data_points(parameter_name, reports_data)
        
        if len(data_points) < 2:
            logger.debug(f"Insufficient data for {parameter_name}: {len(data_points)} points")
            return None
        
        # Sort chronologically (Requirement 8.2)
        data_points.sort(key=lambda dp: dp.date)
        
        # Calculate distances from normal range
        first_distance = self._calculate_distance_from_normal(data_points[0])
        last_distance = self._calculate_distance_from_normal(data_points[-1])
        
        # Determine trend direction (Requirements 8.3, 8.4, 8.5)
        trend_direction = self._calculate_trend_direction(first_distance, last_distance)
        
        # Calculate change percentage
        change_percent = self._calculate_change_percent(first_distance, last_distance)
        
        # Generate summary (Requirement 8.7)
        summary = self._generate_trend_summary(
            parameter_name,
            len(data_points),
            trend_direction,
            change_percent,
            data_points[0].value,
            data_points[-1].value,
            data_points[0].unit
        )
        
        return TrendAnalysis(
            parameter_name=parameter_name,
            data_points=data_points,
            trend_direction=trend_direction,
            change_percent=change_percent,
            summary=summary,
            distance_from_normal_first=first_distance,
            distance_from_normal_last=last_distance
        )
    
    def analyze_all_trends(
        self,
        reports_data: List[Dict[str, Any]]
    ) -> Dict[str, TrendAnalysis]:
        """
        Analyze trends for all parameters across reports.
        
        Requirements: 8.1, 8.8
        
        Args:
            reports_data: List of report dictionaries
        
        Returns:
            Dictionary mapping parameter names to TrendAnalysis objects
        """
        # Find all unique parameters (Requirement 8.8 - only matching names/units)
        parameter_keys = self._get_unique_parameter_keys(reports_data)
        
        trends = {}
        for param_key in parameter_keys:
            param_name = param_key.split("|")[0]  # Extract name from "name|unit" key
            
            analysis = self.analyze_parameter_trend(param_name, reports_data)
            if analysis:
                trends[param_name] = analysis
        
        logger.info(f"Analyzed trends for {len(trends)} parameters across {len(reports_data)} reports")
        return trends
    
    def _extract_data_points(
        self,
        parameter_name: str,
        reports_data: List[Dict[str, Any]]
    ) -> List[DataPoint]:
        """
        Extract data points for a parameter from reports.
        
        Requirement 8.8: Only compare matching parameter names and units
        """
        data_points = []
        
        for report in reports_data:
            # Find matching parameter in this report
            for param in report.get("parameters", []):
                if param.get("name", "").lower() == parameter_name.lower():
                    # Create data point
                    dp = DataPoint(
                        report_id=str(report.get("_id", "")),
                        date=report.get("upload_date", datetime.now()),
                        value=param.get("value", 0.0),
                        unit=param.get("unit", ""),
                        risk_level=param.get("risk_level", "Unknown"),
                        normal_range=param.get("normal_range")
                    )
                    data_points.append(dp)
                    break  # Only one parameter per report
        
        return data_points
    
    def _get_unique_parameter_keys(
        self,
        reports_data: List[Dict[str, Any]]
    ) -> set:
        """
        Get unique parameter keys (name|unit) from all reports.
        
        Requirement 8.8: Only compare matching names and units
        """
        keys = set()
        
        for report in reports_data:
            for param in report.get("parameters", []):
                name = param.get("name", "").lower()
                unit = param.get("unit", "")
                key = f"{name}|{unit}"
                keys.add(key)
        
        return keys
    
    def _calculate_distance_from_normal(self, data_point: DataPoint) -> float:
        """
        Calculate distance from normal range.
        
        Requirements: 8.3, 8.4, 8.5
        
        Returns:
            Positive value if above range, negative if below, 0 if within
        """
        if not data_point.normal_range:
            return 0.0
        
        min_val, max_val = data_point.normal_range
        value = data_point.value
        
        if value < min_val:
            # Below range - negative distance
            return value - min_val
        elif value > max_val:
            # Above range - positive distance
            return value - max_val
        else:
            # Within range
            return 0.0
    
    def _calculate_trend_direction(
        self,
        first_distance: float,
        last_distance: float
    ) -> TrendDirection:
        """
        Calculate trend direction based on distance changes.
        
        Requirements: 8.3, 8.4, 8.5
        
        Logic:
        - Improving: Moving toward normal (absolute distance decreasing)
        - Worsening: Moving away from normal (absolute distance increasing)
        - Stable: Change < 5%
        """
        # Calculate absolute distances
        abs_first = abs(first_distance)
        abs_last = abs(last_distance)
        
        # Calculate percentage change in distance
        if abs_first == 0:
            # Was normal, check if still normal
            if abs_last == 0:
                return TrendDirection.STABLE
            else:
                return TrendDirection.WORSENING
        
        change_percent = ((abs_last - abs_first) / abs_first) * 100
        
        # Classify based on change
        if abs(change_percent) < self.stable_threshold:
            return TrendDirection.STABLE
        elif change_percent < 0:
            # Distance decreased = Improving
            return TrendDirection.IMPROVING
        else:
            # Distance increased = Worsening
            return TrendDirection.WORSENING
    
    def _calculate_change_percent(
        self,
        first_distance: float,
        last_distance: float
    ) -> float:
        """Calculate percentage change in distance from normal."""
        abs_first = abs(first_distance)
        abs_last = abs(last_distance)
        
        if abs_first == 0:
            if abs_last == 0:
                return 0.0
            else:
                return 100.0  # Went from normal to abnormal
        
        return ((abs_last - abs_first) / abs_first) * 100
    
    def _generate_trend_summary(
        self,
        parameter_name: str,
        num_reports: int,
        trend_direction: TrendDirection,
        change_percent: float,
        first_value: float,
        last_value: float,
        unit: str
    ) -> str:
        """
        Generate plain-language trend summary.
        
        Requirement 8.7
        """
        # Format parameter name
        param_display = parameter_name.replace("_", " ").title()
        
        # Create summary based on trend
        if trend_direction == TrendDirection.IMPROVING:
            summary = f"Your {param_display} improved over the last {num_reports} reports, "
            summary += f"moving closer to the normal range. "
            summary += f"Changed from {first_value} to {last_value} {unit}."
        
        elif trend_direction == TrendDirection.WORSENING:
            summary = f"Your {param_display} worsened over the last {num_reports} reports, "
            summary += f"moving further from the normal range. "
            summary += f"Changed from {first_value} to {last_value} {unit}. "
            summary += "Discuss this with your doctor."
        
        elif trend_direction == TrendDirection.STABLE:
            summary = f"Your {param_display} remained stable over the last {num_reports} reports. "
            summary += f"Values ranged around {last_value} {unit}."
        
        else:
            summary = f"Insufficient data to determine trend for {param_display}."
        
        return summary


# Singleton instance
_trend_service: Optional[TrendAnalysisService] = None


def get_trend_service(stable_threshold: float = 5.0) -> TrendAnalysisService:
    """Get or create the Trend Analysis service instance."""
    global _trend_service
    
    if _trend_service is None:
        _trend_service = TrendAnalysisService(stable_threshold)
    
    return _trend_service
