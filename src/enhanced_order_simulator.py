#!/usr/bin/env python3
"""
Enhanced Order Simulator with more realistic e-commerce patterns
- Flash sales and promotions
- Seasonal trends  
- Customer behavior patterns
- Product inventory simulation
"""

import os
import json
import time
import random
from datetime import datetime, timedelta
from kafka import KafkaProducer
import logging

# Enhanced product catalog with inventory
ENHANCED_PRODUCTS = [
    # Electronics - high value, flash sales
    {"id": "ELEC001", "name": "Premium Wireless Headphones", "category": "Electronics", "base_price": 299.99, "inventory": 50, "flash_sale": True},
    {"id": "ELEC002", "name": "4K Gaming Monitor", "category": "Electronics", "base_price": 449.99, "inventory": 30, "flash_sale": False},
    {"id": "ELEC003", "name": "Smartphone Pro Max", "category": "Electronics", "base_price": 999.99, "inventory": 25, "flash_sale": True},
    
    # Fashion - seasonal trends
    {"id": "FASH001", "name": "Summer Dress Collection", "category": "Fashion", "base_price": 79.99, "inventory": 100, "seasonal": True},
    {"id": "FASH002", "name": "Designer Sneakers", "category": "Fashion", "base_price": 159.99, "inventory": 75, "seasonal": False},
    
    # Home & Garden - bulk purchases
    {"id": "HOME001", "name": "Smart Home Security Kit", "category": "Home", "base_price": 199.99, "inventory": 40, "bulk_discount": True},
    {"id": "HOME002", "name": "Organic Garden Starter Set", "category": "Home", "base_price": 49.99, "inventory": 200, "seasonal": True},
    
    # Books - consistent demand
    {"id": "BOOK001", "name": "Machine Learning Handbook", "category": "Books", "base_price": 39.99, "inventory": 500, "educational": True},
    {"id": "BOOK002", "name": "Cooking Masterclass Guide", "category": "Books", "base_price": 24.99, "inventory": 300, "trending": True},
]

class EnhancedOrderSimulator:
    def __init__(self):
        self.producer = KafkaProducer(
            bootstrap_servers=['localhost:9092'],
            value_serializer=lambda x: json.dumps(x).encode('utf-8'),
            key_serializer=lambda x: x.encode('utf-8') if x else None
        )
        
        # Enhanced customer segments
        self.customer_segments = {
            'premium': {'probability': 0.2, 'avg_order_value': 200, 'loyalty': 0.8},
            'regular': {'probability': 0.6, 'avg_order_value': 75, 'loyalty': 0.5}, 
            'bargain': {'probability': 0.2, 'avg_order_value': 30, 'loyalty': 0.3}
        }
        
        # Time-based patterns
        self.hourly_multipliers = {
            0: 0.1, 1: 0.05, 2: 0.05, 3: 0.05, 4: 0.05, 5: 0.1,
            6: 0.2, 7: 0.4, 8: 0.6, 9: 0.8, 10: 1.0, 11: 1.2,
            12: 1.5, 13: 1.3, 14: 1.1, 15: 1.0, 16: 0.9, 17: 0.8,
            18: 1.2, 19: 1.4, 20: 1.6, 21: 1.3, 22: 0.8, 23: 0.4
        }
        
        logging.info("Enhanced Order Simulator initialized with realistic patterns")

    def get_current_promotions(self):
        """Get active promotions based on time and inventory"""
        current_hour = datetime.now().hour  
        promotions = []
        
        # Flash sales during peak hours
        if 12 <= current_hour <= 14 or 18 <= current_hour <= 21:
            flash_products = [p for p in ENHANCED_PRODUCTS if p.get('flash_sale')]
            if flash_products:
                promotions.extend(flash_products)
        
        # Seasonal promotions
        current_month = datetime.now().month
        if current_month in [6, 7, 8]:  # Summer
            seasonal_products = [p for p in ENHANCED_PRODUCTS if p.get('seasonal')]
            promotions.extend(seasonal_products)
            
        return promotions

    def generate_enhanced_order(self):
        """Generate order with realistic e-commerce patterns"""
        
        # Select customer segment
        segment_rand = random.random()
        if segment_rand < 0.2:
            segment = 'premium'
        elif segment_rand < 0.8:
            segment = 'regular'  
        else:
            segment = 'bargain'
            
        customer_profile = self.customer_segments[segment]
        
        # Apply time-based ordering patterns
        current_hour = datetime.now().hour
        order_probability = self.hourly_multipliers.get(current_hour, 1.0)
        
        if random.random() > order_probability:
            return None  # Skip order based on time patterns
            
        # Select product based on promotions and segment
        promotions = self.get_current_promotions()
        
        if promotions and random.random() < 0.4:  # 40% chance to buy promoted items
            product = random.choice(promotions)
            price_multiplier = 0.8  # 20% discount
        else:
            product = random.choice(ENHANCED_PRODUCTS)
            price_multiplier = 1.0
            
        # Premium customers buy more expensive items
        if segment == 'premium' and product['base_price'] < 100:
            expensive_products = [p for p in ENHANCED_PRODUCTS if p['base_price'] > 100]
            if expensive_products:
                product = random.choice(expensive_products)
        
        # Generate realistic quantity based on product type and customer
        if product['category'] == 'Electronics':
            quantity = 1  # Usually single items
        elif product.get('bulk_discount'):
            quantity = random.choices([1, 2, 3, 5], weights=[0.4, 0.3, 0.2, 0.1])[0]
        else:
            quantity = random.choices([1, 2, 3], weights=[0.7, 0.2, 0.1])[0]
            
        # Calculate final price with promotions and quantity discounts
        final_price = product['base_price'] * price_multiplier
        if quantity >= 3:
            final_price *= 0.95  # 5% bulk discount
            
        # Generate order
        order = {
            'order_id': f"ORD{random.randint(100000, 999999)}",
            'product_id': product['id'],
            'product_name': product['name'],
            'category': product['category'],
            'price': round(final_price, 2),
            'quantity': quantity,
            'total_value': round(final_price * quantity, 2),
            'customer_id': f"CUST{random.randint(1000, 9999)}",
            'customer_segment': segment,
            'promotion_applied': price_multiplier < 1.0,
            'timestamp': datetime.now().isoformat(),
        }
        
        return order

if __name__ == '__main__':
    simulator = EnhancedOrderSimulator()
    
    print("🚀 Starting Enhanced Order Simulator with realistic patterns...")
    print("📊 Features: Flash sales, customer segments, time patterns, bulk discounts")
    
    try:
        order_count = 0
        while True:
            order = simulator.generate_enhanced_order()
            
            if order:  # Order might be None due to time-based patterns
                simulator.producer.send('orders', value=order, key=order['order_id'])
                order_count += 1
                
                if order_count % 10 == 0:
                    print(f"📦 Sent {order_count} enhanced orders")
                    
            time.sleep(random.uniform(2, 8))  # Variable delay for realism
            
    except KeyboardInterrupt:
        print(f"\n⚠️ Enhanced simulator stopped. Total orders: {order_count}")
    finally:
        simulator.producer.close()
