"""Generate synthetic, public reviewer fixtures. No real invoice or customer data."""
import json
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
order = {
    'order_id': 'PO-HOTEL-001', 'currency': 'EUR', 'minor_exponent': 2,
    'price_tolerance_minor': 0, 'total_tolerance_minor': 0,
    'terms': 'Supply the specified cotton towels. No polyester substitutions. Delivery must identify grade and size. Prices exclude VAT; tax is rounded half-up per line.',
    'lines': [{'id': 'TOWEL', 'description': 'White 100 percent cotton bath towel, 500 gsm, 70 x 140 cm.',
               'unit': 'piece', 'quantity': 20, 'unit_price_minor': 850, 'tax_bps': 2000}]
}
delivery = {'order_id': order['order_id'], 'receipt_id': 'GRN-001', 'lines': [
    {'id': 'TOWEL', 'description': 'Received white pure cotton bath towels, 500 gsm, size 70 x 140 cm.',
     'unit': 'piece', 'quantity': 20}]}
invoice = {'order_id': order['order_id'], 'invoice_id': 'INV-001', 'currency': 'EUR',
           'total_minor': 20400, 'lines': [
               {'id': 'TOWEL', 'description': 'White bath towels, 100 percent cotton, 500 gsm, 70 x 140 cm.',
                'unit': 'piece', 'quantity': 20, 'unit_price_minor': 850,
                'net_minor': 17000, 'tax_minor': 3400}]}
for name, value in [('order', order), ('delivery', delivery), ('invoice', invoice)]:
    (ROOT / 'examples' / (name + '.json')).write_text(json.dumps(value, indent=2) + '\n')
