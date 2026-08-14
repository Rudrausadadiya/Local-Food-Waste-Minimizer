from decimal import Decimal
from typing import Dict, Any
from .repositories import CrossModuleAnalyticsRepository

# Class: DashboardKPIBuilder
class DashboardKPIBuilder:
    @staticmethod
    # Method: get_executive_kpis
    def get_executive_kpis(start_date, end_date, business_id: str = None) -> Dict[str, Any]:
        sales = CrossModuleAnalyticsRepository.get_sales_summary(start_date, end_date, business_id)
        inventory = CrossModuleAnalyticsRepository.get_inventory_summary(business_id)
        donations = CrossModuleAnalyticsRepository.get_donation_impact(start_date, end_date, business_id)
        marketplace = CrossModuleAnalyticsRepository.get_marketplace_summary(start_date, end_date, business_id)
        
        # Calculate derived metrics
        revenue = sales.get('total_revenue') or Decimal('0.00')
        market_revenue = marketplace.get('marketplace_revenue') or Decimal('0.00')
        total_revenue = revenue + market_revenue
        
        # Placeholder estimates
        profit_estimate = total_revenue * Decimal('0.3') # 30% margin assumption
        inventory_turnover = "High" if inventory.get('low_stock_count', 0) > 10 else "Normal"
        customer_retention = "85%" # Placeholder ML forecast
        
        return {
            'sales_revenue': revenue,
            'orders': sales.get('total_orders') or 0,
            'average_order_value': sales.get('average_order_value') or Decimal('0.00'),
            'inventory_value': inventory.get('total_value') or Decimal('0.00'),
            'low_stock_count': inventory.get('low_stock_count') or 0,
            'meals_served': donations.get('meals_served') or 0,
            'carbon_saved_kg': donations.get('carbon_saved') or Decimal('0.00'),
            'food_saved_kg': donations.get('food_saved') or Decimal('0.00'),
            'marketplace_revenue': market_revenue,
            'marketplace_orders': marketplace.get('marketplace_orders') or 0,
            'profit_estimate': profit_estimate,
            'inventory_turnover': inventory_turnover,
            'customer_retention': customer_retention,
        }
