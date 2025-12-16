import requests
import xmlrpc.client
import os

# --- CONFIGURATION ---
# osTicket
OSTICKET_URL = 'http://localhost:8080/api/tickets.json'
OSTICKET_API_KEY = 'YOUR_OSTICKET_API_KEY' # Replace with your actual key

# Odoo
ODOO_URL = 'http://localhost:8069'
ODOO_DB = 'odoo_prod' # The name of your Odoo database
ODOO_USER = 'your_odoo_email@example.com' # Your Odoo username
ODOO_API_KEY = 'YOUR_ODOO_API_KEY' # Replace with your actual key

# --- ODOO API CONNECTION ---
common = xmlrpc.client.ServerProxy(f'{ODOO_URL}/xmlrpc/2/common')
uid = common.authenticate(ODOO_DB, ODOO_USER, ODOO_API_KEY, {})
models = xmlrpc.client.ServerProxy(f'{ODOO_URL}/xmlrpc/2/object')

def get_osticket_ticket_details(ticket_number):
    """Fetches details for a specific ticket number from osTicket."""
    headers = {'X-API-Key': OSTICKET_API_KEY}
    # Note: The osTicket API for fetching a single ticket by number isn't straightforward.
    # A common approach is to get all tickets and filter, or customize the API.
    # For this example, we'll assume a direct endpoint or a workaround.
    # In a real scenario, you might search for the ticket.
    # This is a mock response for demonstration
    print(f"Fetching details for osTicket #{ticket_number}...")
    # This is a mock response for demonstration
    return {
        'subject': f'Repair for iPhone {ticket_number}',
        'user_email': f'customer{ticket_number}@example.com',
        'user_name': f'Customer {ticket_number}'
    }

def get_or_create_odoo_partner(email, name):
    """Finds a partner in Odoo by email, or creates them if they don't exist."""
    partner_id = models.execute_kw(ODOO_DB, uid, ODOO_API_KEY, 'res.partner', 'search', [[['email', '=', email]]], {'limit': 1})
    if partner_id:
        print(f"Found existing partner: ID {partner_id[0]}")
        return partner_id[0]
    else:
        new_partner_id = models.execute_kw(ODOO_DB, uid, ODOO_API_KEY, 'res.partner', 'create', [{'name': name, 'email': email}])
        print(f"Created new partner: ID {new_partner_id}")
        return new_partner_id

def create_odoo_repair_order(ticket_number, partner_id, description):
    """Creates a new repair order in Odoo and links it to the osTicket ID."""
    repair_order_data = {
        'name': description,
        'partner_id': partner_id,
        'x_studio_osticket_id': str(ticket_number), # The custom field we created!
    }
    repair_id = models.execute_kw(ODOO_DB, uid, ODOO_API_KEY, 'repair.order', 'create', [repair_order_data])
    print(f"Successfully created Odoo Repair Order #{repair_id} for osTicket #{ticket_number}")
    return repair_id

if __name__ == '__main__':
    # Example usage: Run from your terminal like `python create_odoo_repair.py 12345`
    import sys
    if len(sys.argv) < 2:
        print("Usage: python create_odoo_repair.py <osticket_ticket_number>")
        sys.exit(1)

    ticket_number_to_process = sys.argv[1]

    # 1. Get Ticket Info from osTicket
    ticket_info = get_osticket_ticket_details(ticket_number_to_process)

    # 2. Find or Create the Customer in Odoo
    customer_id = get_or_create_odoo_partner(ticket_info['user_email'], ticket_info['user_name'])

    # 3. Create the Repair Order in Odoo
    create_odoo_repair_order(ticket_number_to_process, customer_id, ticket_info['subject'])
