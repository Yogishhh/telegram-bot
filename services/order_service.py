from database import db
from utils.logger import logger

def format_order_summary(order):
    """Formats an order object into a readable string."""
    return (
        f"🆔 *Order #{order['order_id']}*\n"
        f"🔹 Service: {order['service_type']}\n"
        f"📌 Title: {order['title']}\n"
        f"📊 Status: `{order['status']}`\n"
        f"💳 Payment: `{order['payment_status']}`\n"
    )

def create_new_order(user_id, service_type, title, description, budget, deadline, contact):
    """Business logic for creating a new order."""
    logger.info(f"Creating new order for user {user_id} - {service_type}")
    order_id = db.create_order(user_id, service_type, title, description, budget, deadline, contact)
    return order_id

def update_order(order_id, status=None, payment_status=None):
    """Business logic for updating an order."""
    if status:
        db.update_order_status(order_id, status)
    if payment_status:
        db.update_payment_status(order_id, payment_status)
    logger.info(f"Order {order_id} updated: status={status}, payment={payment_status}")
