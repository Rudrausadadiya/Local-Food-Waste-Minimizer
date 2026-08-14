from django.db.models.functions import TruncDay
from typing import Dict, Any, List

# Class: ChartBuilder
class ChartBuilder:
    @staticmethod
    # Method: build_time_series
    def build_time_series(queryset, date_field: str, metric_field: str, agg_func, trunc_func=TruncDay) -> List[Dict[str, Any]]:
        """
        Generic method to build time-series chart data.
        Returns a list of dicts: [{'date': '2023-01-01', 'value': 1500}, ...]
        """
        qs = queryset.annotate(
            date=trunc_func(date_field)
        ).values('date').annotate(
            value=agg_func(metric_field)
        ).order_by('date')
        
        return [{'date': item['date'].strftime('%Y-%m-%d'), 'value': float(item['value']) if item['value'] else 0} for item in qs]
