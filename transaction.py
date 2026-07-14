import customtkinter as ctk
from tkinter import ttk, messagebox
from datetime import date
import re

from database import (
    get_accounts, balance_deposit, cash_deposit, cash_in, cash_out,
    b2b_in, b2b_out, get_transactions, delete_transaction
)


class TransactionWindow(ctk.CTkToplevel):
    def __init__(self, master=None, refresh_callback=None):
        super().__init__(master)
        self.refresh_callback = refresh_callback
        self.account_map = {}
        self.all_transactions = []
        self.selected_transaction_id = None

        self.title("Transaction Management")
        self.geometry("1450x820")
        self.minsize(1150, 700)
        self.protocol("WM_DELETE_WINDOW", self.close_window)

        self.transient(master)
        self.lift()
        self.focus_force()

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        self.create_header()
        self.create_main_area()
        self.create_form()
        self.create_history()
        self.load_accounts()
        self.change_transaction_type("Balance Deposit")
        self.load_transactions()

    def create_header(self):
        header = ctk.CTkFrame(self, corner_radius=0)
        header.grid(row=0, column=0, sticky="ew")
        ctk.CTkLabel(
            header, text="💰 লেনদেন ব্যবস্থাপনা",
            font=ctk.CTkFont(size=28, weight="bold")
        ).pack(pady=18)

    def create_main_area(self):
        self.main_frame = ctk.CTkFrame(self)
        self.main_frame.grid(row=1, column=0, padx=15, pady=(0, 15), sticky="nsew")
        self.main_frame.grid_columnconfigure(1, weight=1)
        self.main_frame.grid_rowconfigure(0, weight=1)

        self.form_frame = ctk.CTkScrollableFrame(self.main_frame, width=380)
        self.form_frame.grid(row=0, column=0, padx=(10, 5), pady=10, sticky="ns")

        self.history_frame = ctk.CTkFrame(self.main_frame)
        self.history_frame.grid(row=0, column=1, padx=(5, 10), pady=10, sticky="nsew")
        self.history_frame.grid_columnconfigure(0, weight=1)
        self.history_frame.grid_rowconfigure(2, weight=1)

    def create_label(self, text):
        label = ctk.CTkLabel(self.form_frame, text=text)
        label.pack(anchor="w", padx=20)
        return label

    def create_form(self):
        ctk.CTkLabel(
            self.form_frame, text="নতুন লেনদেন",
            font=ctk.CTkFont(size=22, weight="bold")
        ).pack(pady=(15, 20))

        self.create_label("লেনদেনের ধরন")
        self.transaction_type = ctk.CTkOptionMenu(
            self.form_frame, width=330, height=42,
            values=[
                "Balance Deposit", "Cash Deposit", "Cash In", "Cash Out",
                "B2B IN", "B2B OUT"
            ],
            command=self.change_transaction_type
        )
        self.transaction_type.pack(pady=(5, 15))
        self.transaction_type.set("Balance Deposit")

        self.account_container = ctk.CTkFrame(self.form_frame, fg_color="transparent")
        self.account_container.pack(fill="x", pady=(0, 10))
        self.account_label = ctk.CTkLabel(self.account_container, text="Financial App")
        self.account_label.pack(anchor="w", padx=20)
        self.account_option = ctk.CTkOptionMenu(
            self.account_container, width=330, height=42,
            values=["No Financial App"]
        )
        self.account_option.pack(pady=(5, 5))

        self.mobile_container = ctk.CTkFrame(self.form_frame, fg_color="transparent")
        ctk.CTkLabel(
            self.mobile_container, text="গ্রাহকের মোবাইল নম্বর"
        ).pack(anchor="w", padx=20)
        self.mobile_entry = ctk.CTkEntry(
            self.mobile_container, width=330, height=42,
            placeholder_text="যেমন: 0171xxxx997"
        )
        self.mobile_entry.pack(pady=(5, 10))

        self.create_label("তারিখ (YYYY-MM-DD)")
        self.date_entry = ctk.CTkEntry(self.form_frame, width=330, height=42)
        self.date_entry.pack(pady=(5, 15))
        self.date_entry.insert(0, date.today().isoformat())

        self.create_label("টাকার পরিমাণ")
        self.amount_entry = ctk.CTkEntry(
            self.form_frame, width=330, height=42, placeholder_text="0.00"
        )
        self.amount_entry.pack(pady=(5, 15))

        self.profit_container = ctk.CTkFrame(self.form_frame, fg_color="transparent")
        ctk.CTkLabel(
            self.profit_container, text="লাভ (Profit)"
        ).pack(anchor="w", padx=20)
        self.profit_entry = ctk.CTkEntry(
            self.profit_container, width=330, height=42,
            placeholder_text="যেমন: 10"
        )
        self.profit_entry.pack(pady=(5, 10))

        self.create_label("নোট")
        self.note_entry = ctk.CTkEntry(
            self.form_frame, width=330, height=42,
            placeholder_text="Optional note"
        )
        self.note_entry.pack(pady=(5, 20))

        ctk.CTkButton(
            self.form_frame, text="💾 Save Transaction",
            width=330, height=48,
            font=ctk.CTkFont(size=16, weight="bold"),
            command=self.save_transaction
        ).pack(pady=(5, 10))

        ctk.CTkButton(
            self.form_frame, text="Clear Form", width=330, height=42,
            fg_color="gray", command=self.clear_form
        ).pack(pady=(0, 20))

    def change_transaction_type(self, selected_type):
        self.mobile_container.pack_forget()
        self.profit_container.pack_forget()

        if selected_type == "Cash Deposit":
            self.account_container.pack_forget()
        else:
            if not self.account_container.winfo_manager():
                self.account_container.pack(fill="x", pady=(0, 10))

            labels = {
                "Balance Deposit": "Financial App",
                "Cash In": "Cash In From App",
                "Cash Out": "Cash Out To App",
                "B2B IN": "B2B IN To App (Cash → App)",
                "B2B OUT": "B2B OUT From App (App → Cash)"
            }
            self.account_label.configure(text=labels.get(selected_type, "Financial App"))

        if selected_type in ("Cash In", "Cash Out"):
            self.mobile_container.pack(fill="x", pady=(0, 5))
            self.profit_container.pack(fill="x", pady=(0, 5))
            self.mobile_entry.focus_set()

    def create_history(self):
        top = ctk.CTkFrame(self.history_frame, fg_color="transparent")
        top.grid(row=0, column=0, padx=15, pady=(15, 5), sticky="ew")

        ctk.CTkLabel(
            top, text="লেনদেনের ইতিহাস",
            font=ctk.CTkFont(size=20, weight="bold")
        ).pack(side="left")

        ctk.CTkButton(
            top, text="🗑 Delete Transaction", width=170,
            fg_color="#C62828", hover_color="#8E0000",
            command=self.delete_selected_transaction
        ).pack(side="right", padx=5)

        ctk.CTkButton(
            top, text="🔄 Refresh", width=100,
            command=self.load_transactions
        ).pack(side="right", padx=5)

        search_frame = ctk.CTkFrame(self.history_frame)
        search_frame.grid(row=1, column=0, padx=15, pady=(5, 10), sticky="ew")
        search_frame.grid_columnconfigure(0, weight=1)

        self.search_entry = ctk.CTkEntry(
            search_frame, height=42,
            placeholder_text="Search: Mobile, Type, App, Date, Amount, Profit or Note"
        )
        self.search_entry.grid(row=0, column=0, padx=(10, 5), pady=10, sticky="ew")
        self.search_entry.bind("<KeyRelease>", self.search_transactions)

        ctk.CTkButton(
            search_frame, text="🔍 Search", width=100, height=42,
            command=self.search_transactions
        ).grid(row=0, column=1, padx=5, pady=10)

        ctk.CTkButton(
            search_frame, text="✖ Clear Search", width=120, height=42,
            fg_color="gray", command=self.clear_search
        ).grid(row=0, column=2, padx=(5, 10), pady=10)

        tree_frame = ctk.CTkFrame(self.history_frame)
        tree_frame.grid(row=2, column=0, padx=15, pady=(0, 15), sticky="nsew")
        tree_frame.grid_columnconfigure(0, weight=1)
        tree_frame.grid_rowconfigure(0, weight=1)

        columns = (
            "id", "date", "type", "mobile", "source",
            "destination", "amount", "profit", "note"
        )
        self.tree = ttk.Treeview(
            tree_frame, columns=columns, show="headings", selectmode="browse"
        )
        headings = {
            "id": "ID", "date": "Date", "type": "Type",
            "mobile": "Mobile Number", "source": "From",
            "destination": "To", "amount": "Amount",
            "profit": "Profit", "note": "Note"
        }
        widths = {
            "id": 50, "date": 100, "type": 120, "mobile": 140,
            "source": 110, "destination": 110, "amount": 110,
            "profit": 90, "note": 180
        }
        for column in columns:
            self.tree.heading(column, text=headings[column])
            self.tree.column(column, width=widths[column], anchor="center")

        sy = ttk.Scrollbar(tree_frame, orient="vertical", command=self.tree.yview)
        sx = ttk.Scrollbar(tree_frame, orient="horizontal", command=self.tree.xview)
        self.tree.configure(yscrollcommand=sy.set, xscrollcommand=sx.set)
        self.tree.grid(row=0, column=0, sticky="nsew")
        sy.grid(row=0, column=1, sticky="ns")
        sx.grid(row=1, column=0, sticky="ew")
        self.tree.bind("<<TreeviewSelect>>", self.on_transaction_select)

    def load_accounts(self):
        try:
            accounts = get_accounts(include_cash=False)
            self.account_map.clear()
            names = []
            for account in accounts:
                name = account["name"]
                self.account_map[name] = account["id"]
                names.append(name)
            values = names or ["No Financial App"]
            self.account_option.configure(values=values)
            self.account_option.set(values[0])
        except Exception as error:
            messagebox.showerror("Database Error", str(error), parent=self)

    def validate_mobile(self, mobile):
        mobile = mobile.strip()
        return bool(
            mobile and len(mobile) == 11 and mobile.startswith("01")
            and re.fullmatch(r"[0-9xX]+", mobile)
        )

    def save_transaction(self):
        transaction_type = self.transaction_type.get()
        transaction_date = self.date_entry.get().strip()
        amount_text = self.amount_entry.get().strip()
        note = self.note_entry.get().strip()

        try:
            date.fromisoformat(transaction_date)
        except ValueError:
            messagebox.showwarning(
                "Invalid Date", "তারিখ YYYY-MM-DD format-এ লিখুন।", parent=self
            )
            return

        try:
            amount = float(amount_text)
            if amount <= 0:
                raise ValueError
        except ValueError:
            messagebox.showwarning(
                "Invalid Amount", "সঠিক টাকার পরিমাণ লিখুন।", parent=self
            )
            return

        account_id = None
        if transaction_type != "Cash Deposit":
            account_id = self.account_map.get(self.account_option.get())
            if not account_id:
                messagebox.showwarning(
                    "Account Required", "Financial App নির্বাচন করুন।", parent=self
                )
                return

        mobile, profit = "", 0.0
        if transaction_type in ("Cash In", "Cash Out"):
            mobile = self.mobile_entry.get().strip()
            if not self.validate_mobile(mobile):
                messagebox.showwarning(
                    "Invalid Mobile",
                    "উদাহরণ: 01712345678 অথবা 0171xxxx997",
                    parent=self
                )
                return
            mobile = mobile.lower()
            try:
                profit = float(self.profit_entry.get().strip() or 0)
                if profit < 0:
                    raise ValueError
            except ValueError:
                messagebox.showwarning(
                    "Invalid Profit", "সঠিক Profit লিখুন।", parent=self
                )
                return

        try:
            if transaction_type == "Balance Deposit":
                balance_deposit(account_id, amount, note, transaction_date)
            elif transaction_type == "Cash Deposit":
                cash_deposit(amount, note, transaction_date)
            elif transaction_type == "Cash In":
                cash_in(account_id, mobile, amount, profit, note, transaction_date)
            elif transaction_type == "Cash Out":
                cash_out(account_id, mobile, amount, profit, note, transaction_date)
            elif transaction_type == "B2B IN":
                b2b_in(account_id, amount, note, transaction_date)
            elif transaction_type == "B2B OUT":
                b2b_out(account_id, amount, note, transaction_date)

            messagebox.showinfo(
                "Success", "লেনদেন সফলভাবে সংরক্ষণ হয়েছে।", parent=self
            )
            self.clear_form()
            self.load_transactions()
            if self.refresh_callback:
                self.refresh_callback()
        except Exception as error:
            messagebox.showerror("Transaction Error", str(error), parent=self)

    def load_transactions(self):
        try:
            self.all_transactions = list(get_transactions(limit=500))
            if self.search_entry.get().strip():
                self.search_transactions()
            else:
                self.display_transactions(self.all_transactions)
        except Exception as error:
            messagebox.showerror("Database Error", str(error), parent=self)

    def display_transactions(self, rows):
        for item in self.tree.get_children():
            self.tree.delete(item)
        for row in rows:
            self.tree.insert("", "end", values=(
                row["id"], row["transaction_date"],
                row["transaction_type"].replace("_", " ").title(),
                row["customer_mobile"] or "-",
                row["source_account"] or "-",
                row["destination_account"] or "-",
                f'{float(row["amount"]):,.2f}',
                f'{float(row["profit"]):,.2f}',
                row["note"] or ""
            ))

    def search_transactions(self, event=None):
        query = self.search_entry.get().strip().lower()
        if not query:
            self.display_transactions(self.all_transactions)
            return
        filtered = []
        for row in self.all_transactions:
            searchable = " ".join([
                str(row["id"]), str(row["transaction_date"] or ""),
                str(row["transaction_type"] or "").replace("_", " "),
                str(row["customer_mobile"] or ""),
                str(row["source_account"] or ""),
                str(row["destination_account"] or ""),
                str(row["amount"] or ""), str(row["profit"] or ""),
                str(row["note"] or "")
            ]).lower()
            if query in searchable:
                filtered.append(row)
        self.display_transactions(filtered)

    def clear_search(self):
        self.search_entry.delete(0, "end")
        self.display_transactions(self.all_transactions)
        self.search_entry.focus_set()

    def on_transaction_select(self, event=None):
        selected = self.tree.selection()
        if not selected:
            self.selected_transaction_id = None
            return
        values = self.tree.item(selected[0], "values")
        self.selected_transaction_id = int(values[0]) if values else None

    def delete_selected_transaction(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning(
                "Select Transaction",
                "Delete করার জন্য একটি Transaction নির্বাচন করুন।",
                parent=self
            )
            return

        values = self.tree.item(selected[0], "values")
        transaction_id = int(values[0])
        if not messagebox.askyesno(
            "Confirm Delete",
            f"ID: {transaction_id}\nType: {values[2]}\nAmount: ৳ {values[6]}\n\n"
            "Delete করলে Balance আগের অবস্থায় ফিরিয়ে নেওয়া হবে।",
            parent=self
        ):
            return

        try:
            result = delete_transaction(transaction_id)
            if isinstance(result, tuple) and not result[0]:
                messagebox.showerror("Delete Failed", result[1], parent=self)
                return
            messagebox.showinfo(
                "Deleted", "Transaction সফলভাবে Delete হয়েছে।", parent=self
            )
            self.selected_transaction_id = None
            self.load_transactions()
            if self.refresh_callback:
                self.refresh_callback()
        except Exception as error:
            messagebox.showerror("Delete Error", str(error), parent=self)

    def clear_form(self):
        for entry in (
            self.mobile_entry, self.amount_entry,
            self.profit_entry, self.note_entry
        ):
            entry.delete(0, "end")
        self.date_entry.delete(0, "end")
        self.date_entry.insert(0, date.today().isoformat())
        if self.transaction_type.get() in ("Cash In", "Cash Out"):
            self.mobile_entry.focus_set()
        else:
            self.amount_entry.focus_set()

    def close_window(self):
        if self.refresh_callback:
            try:
                self.refresh_callback()
            except Exception:
                pass
        self.destroy()
