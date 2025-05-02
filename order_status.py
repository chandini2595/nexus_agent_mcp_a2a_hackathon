import sqlite3
from datetime import datetime
from mcp.server.fastmcp import FastMCP

# Initialize FastMCP server
mcp = FastMCP("order_status")

# Initialize SQLite database
def init_db():
    conn = sqlite3.connect('orders.db')
    c = conn.cursor()
    
    # Create orders table if it doesn't exist
    c.execute('''
        CREATE TABLE IF NOT EXISTS orders (
            order_id TEXT PRIMARY KEY,
            customer_name TEXT,
            status TEXT,
            created_at TEXT,
            updated_at TEXT
        )
    ''')
    
    # Insert some dummy data if table is empty
    c.execute('SELECT COUNT(*) FROM orders')
    if c.fetchone()[0] == 0:
        dummy_data = [
            ('ORD001', 'John Doe', 'Processing', '2024-03-25 10:00:00', '2024-03-25 10:00:00'),
            ('ORD002', 'Jane Smith', 'Shipped', '2024-03-24 15:30:00', '2024-03-25 09:15:00'),
            ('ORD003', 'Bob Johnson', 'Delivered', '2024-03-23 12:00:00', '2024-03-25 14:20:00'),
            ('ORD004', 'Alice Brown', 'Processing', '2024-03-25 11:45:00', '2024-03-25 11:45:00')
        ]
        c.executemany('INSERT INTO orders VALUES (?, ?, ?, ?, ?)', dummy_data)
    
    conn.commit()
    conn.close()

@mcp.tool()
async def get_order_status(order_id: str):
    """
    Fetches the status of an order from the SQLite database.
    
    Args:
        order_id (str): The ID of the order to look up
        
    Returns:
        dict: Order details including status and timestamps
    """
    conn = sqlite3.connect('orders.db')
    c = conn.cursor()
    
    c.execute('SELECT * FROM orders WHERE order_id = ?', (order_id,))
    result = c.fetchone()
    
    if result:
        order_info = {
            'order_id': result[0],
            'customer_name': result[1],
            'status': result[2],
            'created_at': result[3],
            'updated_at': result[4]
        }
        conn.close()
        return order_info
    else:
        conn.close()
        return {'error': f'Order {order_id} not found'}

@mcp.tool()
async def list_all_orders():
    """
    Retrieves all orders from the database.
    
    Returns:
        list: List of all orders and their details
    """
    conn = sqlite3.connect('orders.db')
    c = conn.cursor()
    
    c.execute('SELECT * FROM orders')
    results = c.fetchall()
    
    orders = []
    for result in results:
        orders.append({
            'order_id': result[0],
            'customer_name': result[1],
            'status': result[2],
            'created_at': result[3],
            'updated_at': result[4]
        })
    
    conn.close()
    return orders

@mcp.tool()
async def update_order_status(order_id: str, new_status: str):
    """
    Updates the status of an existing order.
    
    Args:
        order_id (str): The ID of the order to update
        new_status (str): The new status to set
        
    Returns:
        dict: Updated order details or error message
    """
    conn = sqlite3.connect('orders.db')
    c = conn.cursor()
    
    # Check if order exists
    c.execute('SELECT * FROM orders WHERE order_id = ?', (order_id,))
    if not c.fetchone():
        conn.close()
        return {'error': f'Order {order_id} not found'}
    
    # Update the order status
    current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    c.execute('''
        UPDATE orders 
        SET status = ?, updated_at = ?
        WHERE order_id = ?
    ''', (new_status, current_time, order_id))
    
    conn.commit()
    
    # Fetch and return updated order
    c.execute('SELECT * FROM orders WHERE order_id = ?', (order_id,))
    result = c.fetchone()
    
    updated_order = {
        'order_id': result[0],
        'customer_name': result[1],
        'status': result[2],
        'created_at': result[3],
        'updated_at': result[4]
    }
    
    conn.close()
    return updated_order

if __name__ == "__main__":
    # Initialize the database
    init_db()
    
    # Start the server
    print("Starting Order Status MCP server...")
    mcp.run(transport="stdio")
    print("Order Status MCP server is running.") 