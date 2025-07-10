from atoms import run_query
from decimal import Decimal

def save_expense(id, kind, in_amount, out_amount, account_id=None):
    in_amount = Decimal(str(in_amount))
    out_amount = Decimal(str(out_amount))
    run_query(
        """
        INSERT INTO expenses (id, kind, in_amount, out_amount, account_id)
        VALUES (%s, %s, %s, %s, %s)
        """,
        (id, kind, in_amount, out_amount, account_id)
    )