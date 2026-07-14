import customtkinter as ctk
from tkinter import ttk, messagebox
from datetime import date

from database import get_daily_report, get_monthly_report


class ReportsWindow(ctk.CTkToplevel):
    def __init__(self, master=None):
        super().__init__(master)
        self.title("Today & Monthly Reports")
        self.geometry("1500x820")
        self.minsize(1150, 650)
        self.transient(master)
        self.lift()
        self.focus_force()

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(3, weight=1)

        self.create_header()
        self.create_filter_area()
        self.create_summary_area()
        self.create_table()
        self.load_today_report()

    def create_header(self):
        header = ctk.CTkFrame(self, corner_radius=0)
        header.grid(row=0, column=0, sticky="ew")
        ctk.CTkLabel(
            header, text="📊 Today & Monthly Reports",
            font=ctk.CTkFont(size=28, weight="bold")
        ).pack(pady=18)

    def create_filter_area(self):
        frame = ctk.CTkFrame(self)
        frame.grid(row=1, column=0, padx=15, pady=15, sticky="ew")

        ctk.CTkLabel(frame, text="Daily Report").grid(
            row=0, column=0, padx=(15, 5), pady=15
        )
        self.date_entry = ctk.CTkEntry(frame, width=150)
        self.date_entry.grid(row=0, column=1, padx=5, pady=15)
        self.date_entry.insert(0, date.today().isoformat())

        ctk.CTkButton(
            frame, text="Show Today / Date", width=150,
            command=self.load_today_report
        ).grid(row=0, column=2, padx=(5, 25), pady=15)

        ctk.CTkLabel(frame, text="Monthly Report").grid(
            row=0, column=3, padx=(10, 5), pady=15
        )
        self.year_entry = ctk.CTkEntry(frame, width=90)
        self.year_entry.grid(row=0, column=4, padx=5, pady=15)
        self.year_entry.insert(0, str(date.today().year))

        self.month_option = ctk.CTkOptionMenu(
            frame, width=90, values=[f"{i:02d}" for i in range(1, 13)]
        )
        self.month_option.grid(row=0, column=5, padx=5, pady=15)
        self.month_option.set(f"{date.today().month:02d}")

        ctk.CTkButton(
            frame, text="Show Monthly", width=140,
            command=self.load_monthly_report
        ).grid(row=0, column=6, padx=(5, 15), pady=15)

    def create_summary_area(self):
        self.summary_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.summary_frame.grid(row=2, column=0, padx=15, pady=(0, 10), sticky="ew")
        for column in range(8):
            self.summary_frame.grid_columnconfigure(column, weight=1)

        self.balance_deposit_label = self.create_card(0, "Balance Deposit")
        self.cash_deposit_label = self.create_card(1, "Cash Deposit")
        self.cash_in_label = self.create_card(2, "Cash In")
        self.cash_out_label = self.create_card(3, "Cash Out")
        self.b2b_in_label = self.create_card(4, "B2B IN")
        self.b2b_out_label = self.create_card(5, "B2B OUT")
        self.profit_label = self.create_card(6, "Total Profit")
        self.count_label = self.create_card(7, "Transactions", money=False)

    def create_card(self, column, title, money=True):
        card = ctk.CTkFrame(self.summary_frame, height=105)
        card.grid(row=0, column=column, padx=4, pady=5, sticky="ew")
        card.grid_propagate(False)
        ctk.CTkLabel(
            card, text=title, font=ctk.CTkFont(size=12, weight="bold")
        ).pack(pady=(18, 5))
        label = ctk.CTkLabel(
            card, text="৳ 0.00" if money else "0",
            font=ctk.CTkFont(size=18, weight="bold")
        )
        label.pack()
        return label

    def create_table(self):
        frame = ctk.CTkFrame(self)
        frame.grid(row=3, column=0, padx=15, pady=(0, 15), sticky="nsew")
        frame.grid_columnconfigure(0, weight=1)
        frame.grid_rowconfigure(0, weight=1)

        columns = (
            "id", "date", "type", "mobile", "source",
            "destination", "amount", "profit", "note"
        )
        self.tree = ttk.Treeview(frame, columns=columns, show="headings")
        headings = {
            "id": "ID", "date": "Date", "type": "Type",
            "mobile": "Mobile", "source": "From", "destination": "To",
            "amount": "Amount", "profit": "Profit", "note": "Note"
        }
        widths = {
            "id": 55, "date": 100, "type": 120, "mobile": 135,
            "source": 120, "destination": 120, "amount": 110,
            "profit": 90, "note": 220
        }
        for column in columns:
            self.tree.heading(column, text=headings[column])
            self.tree.column(column, width=widths[column], anchor="center")

        y_scroll = ttk.Scrollbar(frame, orient="vertical", command=self.tree.yview)
        x_scroll = ttk.Scrollbar(frame, orient="horizontal", command=self.tree.xview)
        self.tree.configure(
            yscrollcommand=y_scroll.set, xscrollcommand=x_scroll.set
        )
        self.tree.grid(row=0, column=0, sticky="nsew")
        y_scroll.grid(row=0, column=1, sticky="ns")
        x_scroll.grid(row=1, column=0, sticky="ew")

    def load_today_report(self):
        try:
            report = get_daily_report(self.date_entry.get().strip())
            self.show_report(report)
        except Exception as error:
            messagebox.showerror("Report Error", str(error), parent=self)

    def load_monthly_report(self):
        try:
            report = get_monthly_report(
                self.year_entry.get().strip(), self.month_option.get()
            )
            self.show_report(report)
        except Exception as error:
            messagebox.showerror("Report Error", str(error), parent=self)

    def show_report(self, report):
        summary = report["summary"]
        labels = (
            (self.balance_deposit_label, "balance_deposit"),
            (self.cash_deposit_label, "cash_deposit"),
            (self.cash_in_label, "cash_in"),
            (self.cash_out_label, "cash_out"),
            (self.b2b_in_label, "b2b_in"),
            (self.b2b_out_label, "b2b_out"),
            (self.profit_label, "profit"),
        )
        for label, key in labels:
            label.configure(text=f'৳ {summary.get(key, 0):,.2f}')
        self.count_label.configure(text=str(summary.get("transaction_count", 0)))

        for item in self.tree.get_children():
            self.tree.delete(item)

        for row in report["rows"]:
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
