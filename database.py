import sqlite3
from pathlib import Path
from datetime import date

import sqlite3
import os
from pathlib import Path
from datetime import date

APP_NAME = "Financial_Shop_Software"

APP_DATA_DIR = Path(
    os.getenv("LOCALAPPDATA", Path.home())
) / APP_NAME

APP_DATA_DIR.mkdir(
    parents=True,
    exist_ok=True
)

DB_DIR = APP_DATA_DIR / "database"

DB_DIR.mkdir(
    parents=True,
    exist_ok=True
)

DB_PATH = DB_DIR / "account.db"


def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def initialize_database():
    with get_connection() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS accounts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL UNIQUE,
                balance REAL NOT NULL DEFAULT 0,
                is_cash INTEGER NOT NULL DEFAULT 0,
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
            )
        """)

        conn.execute("""
            CREATE TABLE IF NOT EXISTS transactions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                transaction_date TEXT NOT NULL,
                transaction_type TEXT NOT NULL,
                customer_mobile TEXT DEFAULT '',
                source_account_id INTEGER,
                destination_account_id INTEGER,
                amount REAL NOT NULL DEFAULT 0,
                profit REAL NOT NULL DEFAULT 0,
                note TEXT DEFAULT '',
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY(source_account_id) REFERENCES accounts(id),
                FOREIGN KEY(destination_account_id) REFERENCES accounts(id)
            )
        """)

        for name in ("Bkash", "Nagad", "Rocket"):
            conn.execute(
                "INSERT OR IGNORE INTO accounts "
                "(name, balance, is_cash) VALUES (?, 0, 0)",
                (name,)
            )

        conn.execute(
            "INSERT OR IGNORE INTO accounts "
            "(name, balance, is_cash) VALUES ('Cash', 0, 1)"
        )


def _cash_id(conn):
    row = conn.execute(
        "SELECT id FROM accounts "
        "WHERE is_cash = 1 ORDER BY id LIMIT 1"
    ).fetchone()

    if not row:
        cur = conn.execute(
            "INSERT INTO accounts "
            "(name, balance, is_cash) VALUES ('Cash', 0, 1)"
        )
        return cur.lastrowid

    return row["id"]


def _account(conn, account_id):
    row = conn.execute(
        "SELECT * FROM accounts WHERE id = ?",
        (account_id,)
    ).fetchone()

    if not row:
        raise ValueError("Financial App পাওয়া যায়নি।")

    return row


def _add_balance(conn, account_id, amount):
    conn.execute(
        "UPDATE accounts SET balance = balance + ? WHERE id = ?",
        (float(amount), account_id)
    )


def _subtract_balance(conn, account_id, amount):
    row = _account(conn, account_id)
    amount = float(amount)

    if float(row["balance"]) < amount:
        raise ValueError(f'{row["name"]} Balance পর্যাপ্ত নয়।')

    conn.execute(
        "UPDATE accounts SET balance = balance - ? WHERE id = ?",
        (amount, account_id)
    )


def _insert_transaction(
    conn,
    transaction_date,
    transaction_type,
    customer_mobile,
    source_id,
    destination_id,
    amount,
    profit,
    note
):
    conn.execute("""
        INSERT INTO transactions (
            transaction_date,
            transaction_type,
            customer_mobile,
            source_account_id,
            destination_account_id,
            amount,
            profit,
            note
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        transaction_date,
        transaction_type,
        customer_mobile or "",
        source_id,
        destination_id,
        float(amount),
        float(profit),
        note or ""
    ))


def get_accounts(include_cash=True):
    initialize_database()

    with get_connection() as conn:
        if include_cash:
            return conn.execute(
                "SELECT * FROM accounts ORDER BY is_cash, id"
            ).fetchall()

        return conn.execute(
            "SELECT * FROM accounts "
            "WHERE is_cash = 0 ORDER BY id"
        ).fetchall()


def add_account(name):
    name = name.strip()

    if not name:
        raise ValueError("App Name লিখুন।")

    initialize_database()

    with get_connection() as conn:
        conn.execute(
            "INSERT INTO accounts "
            "(name, balance, is_cash) VALUES (?, 0, 0)",
            (name,)
        )


def delete_account(account_id):
    initialize_database()

    with get_connection() as conn:
        row = _account(conn, account_id)

        if row["is_cash"]:
            raise ValueError("Cash account delete করা যাবে না।")

        used = conn.execute("""
            SELECT 1
            FROM transactions
            WHERE source_account_id = ?
               OR destination_account_id = ?
            LIMIT 1
        """, (account_id, account_id)).fetchone()

        if used:
            raise ValueError(
                "এই App-এর Transaction আছে, তাই Delete করা যাবে না।"
            )

        conn.execute(
            "DELETE FROM accounts WHERE id = ?",
            (account_id,)
        )


def get_dashboard_data():
    initialize_database()
    today = date.today().isoformat()

    with get_connection() as conn:
        accounts = conn.execute(
            "SELECT * FROM accounts ORDER BY is_cash, id"
        ).fetchall()

        cash_row = conn.execute("""
            SELECT balance
            FROM accounts
            WHERE is_cash = 1
            ORDER BY id
            LIMIT 1
        """).fetchone()

        cash_balance = (
            float(cash_row["balance"])
            if cash_row else 0.0
        )

        total_balance = sum(
            float(account["balance"])
            for account in accounts
        )

        today_profit_row = conn.execute("""
            SELECT COALESCE(SUM(profit), 0) AS total
            FROM transactions
            WHERE transaction_date = ?
        """, (today,)).fetchone()

        total_profit_row = conn.execute("""
            SELECT COALESCE(SUM(profit), 0) AS total
            FROM transactions
        """).fetchone()

        today_profit = float(
            today_profit_row["total"] or 0
        )

        total_profit = float(
            total_profit_row["total"] or 0
        )

        return {
            "total_balance": total_balance,
            "total_cash": total_balance,
            "cash_balance": cash_balance,
            "today_profit": today_profit,
            "total_profit": total_profit,
            "accounts": accounts
        }


def balance_deposit(
    account_id,
    amount,
    note="",
    transaction_date=None
):
    initialize_database()
    transaction_date = (
        transaction_date or date.today().isoformat()
    )

    with get_connection() as conn:
        _account(conn, account_id)
        _add_balance(conn, account_id, amount)

        _insert_transaction(
            conn,
            transaction_date,
            "balance_deposit",
            "",
            None,
            account_id,
            amount,
            0,
            note
        )


def cash_deposit(
    amount,
    note="",
    transaction_date=None
):
    initialize_database()
    transaction_date = (
        transaction_date or date.today().isoformat()
    )

    with get_connection() as conn:
        cash_id = _cash_id(conn)
        _add_balance(conn, cash_id, amount)

        _insert_transaction(
            conn,
            transaction_date,
            "cash_deposit",
            "",
            None,
            cash_id,
            amount,
            0,
            note
        )


def cash_in(
    account_id,
    mobile,
    amount,
    profit=0,
    note="",
    transaction_date=None
):
    initialize_database()
    transaction_date = (
        transaction_date or date.today().isoformat()
    )

    amount = float(amount)
    profit = float(profit)

    with get_connection() as conn:
        cash_id = _cash_id(conn)

        _subtract_balance(conn, account_id, amount)
        _add_balance(conn, account_id, profit)
        _add_balance(conn, cash_id, amount)

        _insert_transaction(
            conn,
            transaction_date,
            "cash_in",
            mobile,
            account_id,
            cash_id,
            amount,
            profit,
            note
        )


def cash_out(
    account_id,
    mobile,
    amount,
    profit=0,
    note="",
    transaction_date=None
):
    initialize_database()
    transaction_date = (
        transaction_date or date.today().isoformat()
    )

    amount = float(amount)
    profit = float(profit)

    with get_connection() as conn:
        cash_id = _cash_id(conn)

        _subtract_balance(conn, cash_id, amount)
        _add_balance(conn, account_id, amount + profit)

        _insert_transaction(
            conn,
            transaction_date,
            "cash_out",
            mobile,
            cash_id,
            account_id,
            amount,
            profit,
            note
        )


def b2b_in(
    account_id,
    amount,
    note="",
    transaction_date=None
):
    initialize_database()
    transaction_date = (
        transaction_date or date.today().isoformat()
    )
    amount = float(amount)

    with get_connection() as conn:
        cash_id = _cash_id(conn)

        _subtract_balance(conn, cash_id, amount)
        _add_balance(conn, account_id, amount)

        _insert_transaction(
            conn,
            transaction_date,
            "b2b_in",
            "",
            cash_id,
            account_id,
            amount,
            0,
            note
        )


def b2b_out(
    account_id,
    amount,
    note="",
    transaction_date=None
):
    initialize_database()
    transaction_date = (
        transaction_date or date.today().isoformat()
    )
    amount = float(amount)

    with get_connection() as conn:
        cash_id = _cash_id(conn)

        _subtract_balance(conn, account_id, amount)
        _add_balance(conn, cash_id, amount)

        _insert_transaction(
            conn,
            transaction_date,
            "b2b_out",
            "",
            account_id,
            cash_id,
            amount,
            0,
            note
        )


def get_transactions(limit=500):
    initialize_database()

    with get_connection() as conn:
        return conn.execute("""
            SELECT
                t.id,
                t.transaction_date,
                t.transaction_type,
                t.customer_mobile,
                t.amount,
                t.profit,
                t.note,
                s.name AS source_account,
                d.name AS destination_account
            FROM transactions t
            LEFT JOIN accounts s
                ON s.id = t.source_account_id
            LEFT JOIN accounts d
                ON d.id = t.destination_account_id
            ORDER BY t.id DESC
            LIMIT ?
        """, (int(limit),)).fetchall()


def delete_transaction(transaction_id):
    initialize_database()

    with get_connection() as conn:
        row = conn.execute(
            "SELECT * FROM transactions WHERE id = ?",
            (transaction_id,)
        ).fetchone()

        if not row:
            return False, "Transaction পাওয়া যায়নি।"

        transaction_type = row["transaction_type"]
        amount = float(row["amount"])
        profit = float(row["profit"])
        source_id = row["source_account_id"]
        destination_id = row["destination_account_id"]

        if transaction_type == "balance_deposit":
            _subtract_balance(
                conn,
                destination_id,
                amount
            )

        elif transaction_type == "cash_deposit":
            _subtract_balance(
                conn,
                destination_id,
                amount
            )

        elif transaction_type == "cash_in":
            _subtract_balance(
                conn,
                destination_id,
                amount
            )
            _add_balance(
                conn,
                source_id,
                amount
            )
            _subtract_balance(
                conn,
                source_id,
                profit
            )

        elif transaction_type == "cash_out":
            _add_balance(
                conn,
                source_id,
                amount
            )
            _subtract_balance(
                conn,
                destination_id,
                amount + profit
            )

        elif transaction_type == "b2b_in":
            _add_balance(
                conn,
                source_id,
                amount
            )
            _subtract_balance(
                conn,
                destination_id,
                amount
            )

        elif transaction_type == "b2b_out":
            _add_balance(
                conn,
                source_id,
                amount
            )
            _subtract_balance(
                conn,
                destination_id,
                amount
            )

        else:
            return (
                False,
                f"Unknown transaction type: {transaction_type}"
            )

        conn.execute(
            "DELETE FROM transactions WHERE id = ?",
            (transaction_id,)
        )

        return True, "Transaction deleted successfully."


def _report(where_sql, params):
    initialize_database()

    with get_connection() as conn:
        rows = conn.execute(f"""
            SELECT
                t.id,
                t.transaction_date,
                t.transaction_type,
                t.customer_mobile,
                t.amount,
                t.profit,
                t.note,
                s.name AS source_account,
                d.name AS destination_account
            FROM transactions t
            LEFT JOIN accounts s
                ON s.id = t.source_account_id
            LEFT JOIN accounts d
                ON d.id = t.destination_account_id
            WHERE {where_sql}
            ORDER BY t.id DESC
        """, params).fetchall()

    summary = {
        "balance_deposit": 0.0,
        "cash_deposit": 0.0,
        "cash_in": 0.0,
        "cash_out": 0.0,
        "b2b_in": 0.0,
        "b2b_out": 0.0,
        "profit": 0.0,
        "transaction_count": len(rows)
    }

    for row in rows:
        transaction_type = row["transaction_type"]

        if transaction_type in summary:
            summary[transaction_type] += float(
                row["amount"]
            )

        summary["profit"] += float(
            row["profit"]
        )

    return {
        "summary": summary,
        "rows": rows
    }


def get_daily_report(report_date):
    return _report(
        "t.transaction_date = ?",
        (str(report_date),)
    )


def get_monthly_report(year, month):
    prefix = f"{int(year):04d}-{int(month):02d}"

    return _report(
        "substr(t.transaction_date, 1, 7) = ?",
        (prefix,)
    )


initialize_database()
