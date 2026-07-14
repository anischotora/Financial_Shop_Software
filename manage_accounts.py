import sqlite3
import customtkinter as ctk
from tkinter import ttk, messagebox

from database import (
    get_accounts,
    add_account,
    DB_PATH
)


class ManageAccountsWindow(ctk.CTkToplevel):

    def __init__(self, master=None, refresh_callback=None):
        super().__init__(master)

        self.refresh_callback = refresh_callback
        self.selected_account_id = None

        self.title("Manage Financial Apps")
        self.geometry("950x650")
        self.minsize(800, 550)

        self.transient(master)
        self.lift()
        self.focus_force()

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(2, weight=1)

        self.ensure_active_column()

        self.create_header()
        self.create_add_area()
        self.create_accounts_table()

        self.load_accounts()


    # =====================================================
    # DATABASE ACTIVE COLUMN
    # =====================================================

    def ensure_active_column(self):

        with sqlite3.connect(DB_PATH) as conn:

            columns = conn.execute(
                "PRAGMA table_info(accounts)"
            ).fetchall()

            column_names = [
                column[1]
                for column in columns
            ]

            if "is_active" not in column_names:

                conn.execute(
                    """
                    ALTER TABLE accounts
                    ADD COLUMN is_active INTEGER
                    NOT NULL DEFAULT 1
                    """
                )


    # =====================================================
    # HEADER
    # =====================================================

    def create_header(self):

        header = ctk.CTkFrame(
            self,
            corner_radius=0
        )

        header.grid(
            row=0,
            column=0,
            sticky="ew"
        )

        ctk.CTkLabel(
            header,
            text="➕ Manage Financial Apps",
            font=ctk.CTkFont(
                size=28,
                weight="bold"
            )
        ).pack(
            pady=18
        )


    # =====================================================
    # ADD / ACTION AREA
    # =====================================================

    def create_add_area(self):

        frame = ctk.CTkFrame(self)

        frame.grid(
            row=1,
            column=0,
            padx=20,
            pady=20,
            sticky="ew"
        )

        frame.grid_columnconfigure(
            0,
            weight=1
        )


        # APP NAME

        self.name_entry = ctk.CTkEntry(
            frame,
            height=45,
            placeholder_text="নতুন Financial App-এর নাম লিখুন"
        )

        self.name_entry.grid(
            row=0,
            column=0,
            padx=(15, 8),
            pady=15,
            sticky="ew"
        )

        self.name_entry.bind(
            "<Return>",
            lambda event: self.add_new_account()
        )


        # ADD BUTTON

        ctk.CTkButton(
            frame,
            text="➕ Add App",
            width=120,
            height=45,
            command=self.add_new_account
        ).grid(
            row=0,
            column=1,
            padx=5,
            pady=15
        )


        # DEACTIVATE BUTTON

        ctk.CTkButton(
            frame,
            text="⛔ Deactivate",
            width=130,
            height=45,
            fg_color="#D35400",
            hover_color="#A04000",
            command=self.deactivate_selected_account
        ).grid(
            row=0,
            column=2,
            padx=5,
            pady=15
        )


        # ACTIVATE BUTTON

        ctk.CTkButton(
            frame,
            text="✅ Activate",
            width=120,
            height=45,
            fg_color="#198754",
            hover_color="#146C43",
            command=self.activate_selected_account
        ).grid(
            row=0,
            column=3,
            padx=(5, 15),
            pady=15
        )


    # =====================================================
    # TABLE
    # =====================================================

    def create_accounts_table(self):

        frame = ctk.CTkFrame(self)

        frame.grid(
            row=2,
            column=0,
            padx=20,
            pady=(0, 20),
            sticky="nsew"
        )

        frame.grid_columnconfigure(
            0,
            weight=1
        )

        frame.grid_rowconfigure(
            0,
            weight=1
        )


        columns = (
            "id",
            "name",
            "balance",
            "status"
        )


        self.tree = ttk.Treeview(
            frame,
            columns=columns,
            show="headings",
            selectmode="browse"
        )


        self.tree.heading(
            "id",
            text="ID"
        )

        self.tree.heading(
            "name",
            text="Financial App"
        )

        self.tree.heading(
            "balance",
            text="Current Balance"
        )

        self.tree.heading(
            "status",
            text="Status"
        )


        self.tree.column(
            "id",
            width=70,
            anchor="center"
        )

        self.tree.column(
            "name",
            width=300,
            anchor="center"
        )

        self.tree.column(
            "balance",
            width=220,
            anchor="center"
        )

        self.tree.column(
            "status",
            width=150,
            anchor="center"
        )


        self.tree.grid(
            row=0,
            column=0,
            sticky="nsew"
        )


        scrollbar = ttk.Scrollbar(
            frame,
            orient="vertical",
            command=self.tree.yview
        )

        scrollbar.grid(
            row=0,
            column=1,
            sticky="ns"
        )

        self.tree.configure(
            yscrollcommand=scrollbar.set
        )

        self.tree.bind(
            "<<TreeviewSelect>>",
            self.on_select
        )


    # =====================================================
    # LOAD ACCOUNTS
    # =====================================================

    def load_accounts(self):

        try:

            for item in self.tree.get_children():

                self.tree.delete(item)


            with sqlite3.connect(DB_PATH) as conn:

                conn.row_factory = sqlite3.Row

                accounts = conn.execute(
                    """
                    SELECT
                        id,
                        name,
                        balance,
                        is_active
                    FROM accounts
                    WHERE is_cash = 0
                    ORDER BY id
                    """
                ).fetchall()


            for account in accounts:

                status = (
                    "Active"
                    if account["is_active"] == 1
                    else "Deactive"
                )


                self.tree.insert(
                    "",
                    "end",
                    values=(
                        account["id"],
                        account["name"],
                        f'৳ {float(account["balance"]):,.2f}',
                        status
                    )
                )


            self.selected_account_id = None


        except Exception as error:

            messagebox.showerror(
                "Database Error",
                str(error),
                parent=self
            )


    # =====================================================
    # SELECT ACCOUNT
    # =====================================================

    def on_select(
        self,
        event=None
    ):

        selected = self.tree.selection()


        if not selected:

            self.selected_account_id = None

            return


        values = self.tree.item(
            selected[0],
            "values"
        )


        if values:

            self.selected_account_id = int(
                values[0]
            )


    # =====================================================
    # ADD ACCOUNT
    # =====================================================

    def add_new_account(self):

        name = (
            self.name_entry
            .get()
            .strip()
        )


        if not name:

            messagebox.showwarning(
                "App Name Required",
                "Financial App-এর নাম লিখুন।",
                parent=self
            )

            self.name_entry.focus_set()

            return


        try:

            add_account(
                name
            )


            # নতুন Account Active নিশ্চিত করা

            with sqlite3.connect(DB_PATH) as conn:

                conn.execute(
                    """
                    UPDATE accounts
                    SET is_active = 1
                    WHERE name = ?
                    """,
                    (name,)
                )


            self.name_entry.delete(
                0,
                "end"
            )


            self.load_accounts()


            if self.refresh_callback:

                self.refresh_callback()


            messagebox.showinfo(
                "Success",
                f'"{name}" সফলভাবে Add হয়েছে।',
                parent=self
            )


            self.name_entry.focus_set()


        except Exception as error:

            messagebox.showerror(
                "Add App Error",
                str(error),
                parent=self
            )


    # =====================================================
    # DEACTIVATE ACCOUNT
    # =====================================================

    def deactivate_selected_account(self):

        if self.selected_account_id is None:

            messagebox.showwarning(
                "Select App",
                "Deactivate করার জন্য একটি App নির্বাচন করুন।",
                parent=self
            )

            return


        selected = self.tree.selection()

        if not selected:

            return


        values = self.tree.item(
            selected[0],
            "values"
        )


        account_name = values[1]

        current_status = values[3]


        if current_status == "Deactive":

            messagebox.showinfo(
                "Already Deactive",
                f'"{account_name}" ইতিমধ্যে Deactive আছে।',
                parent=self
            )

            return


        confirm = messagebox.askyesno(
            "Confirm Deactivate",
            f'আপনি কি "{account_name}" Deactivate করতে চান?\n\n'
            "Account Delete হবে না।\n"
            "Balance এবং পুরোনো Transaction অক্ষত থাকবে।",
            parent=self
        )


        if not confirm:

            return


        try:

            with sqlite3.connect(DB_PATH) as conn:

                conn.execute(
                    """
                    UPDATE accounts
                    SET is_active = 0
                    WHERE id = ?
                    AND is_cash = 0
                    """,
                    (
                        self.selected_account_id,
                    )
                )


            self.load_accounts()


            if self.refresh_callback:

                self.refresh_callback()


            messagebox.showinfo(
                "Deactivated",
                f'"{account_name}" সফলভাবে Deactivate হয়েছে।',
                parent=self
            )


        except Exception as error:

            messagebox.showerror(
                "Deactivate Error",
                str(error),
                parent=self
            )


    # =====================================================
    # ACTIVATE ACCOUNT
    # =====================================================

    def activate_selected_account(self):

        if self.selected_account_id is None:

            messagebox.showwarning(
                "Select App",
                "Activate করার জন্য একটি App নির্বাচন করুন।",
                parent=self
            )

            return


        selected = self.tree.selection()

        if not selected:

            return


        values = self.tree.item(
            selected[0],
            "values"
        )


        account_name = values[1]

        current_status = values[3]


        if current_status == "Active":

            messagebox.showinfo(
                "Already Active",
                f'"{account_name}" ইতিমধ্যে Active আছে।',
                parent=self
            )

            return


        try:

            with sqlite3.connect(DB_PATH) as conn:

                conn.execute(
                    """
                    UPDATE accounts
                    SET is_active = 1
                    WHERE id = ?
                    AND is_cash = 0
                    """,
                    (
                        self.selected_account_id,
                    )
                )


            self.load_accounts()


            if self.refresh_callback:

                self.refresh_callback()


            messagebox.showinfo(
                "Activated",
                f'"{account_name}" সফলভাবে Activate হয়েছে।',
                parent=self
            )


        except Exception as error:

            messagebox.showerror(
                "Activate Error",
                str(error),
                parent=self
            )