import customtkinter as ctk
from tkinter import messagebox
from database import get_dashboard_data, get_accounts
from ui.transaction import TransactionWindow

class Dashboard(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.transaction_window=None; self.report_window=None; self.manage_window=None
        self.title("Financial Shop Software - Dashboard"); self.geometry("1300x750"); self.minsize(1100,650)
        self.grid_columnconfigure(1,weight=1); self.grid_rowconfigure(0,weight=1)
        self.create_sidebar(); self.create_content_area(); self.refresh_dashboard()
        self.bind("<F5>",lambda event:self.refresh_dashboard())

    def create_sidebar(self):
        self.sidebar=ctk.CTkFrame(self,width=230,corner_radius=0); self.sidebar.grid(row=0,column=0,sticky="nsew"); self.sidebar.grid_propagate(False)
        ctk.CTkLabel(self.sidebar,text="💰",font=ctk.CTkFont(size=45)).pack(pady=(30,5))
        ctk.CTkLabel(self.sidebar,text="Financial Shop",font=ctk.CTkFont(size=24,weight="bold")).pack()
        ctk.CTkLabel(self.sidebar,text="Account Software",font=ctk.CTkFont(size=14)).pack(pady=(0,30))
        for text,cmd in [("🏠 Dashboard",self.refresh_dashboard),("💳 Transaction",self.open_transaction),("➕ Manage Apps",self.open_manage_accounts),("📊 Reports",self.open_reports),("🔄 Refresh",self.refresh_dashboard)]:
            ctk.CTkButton(self.sidebar,text=text,width=190,height=45,command=cmd).pack(padx=20,pady=7)
        ctk.CTkButton(self.sidebar,text="❌ Exit",width=190,height=45,fg_color="#C0392B",hover_color="#922B21",command=self.close_application).pack(side="bottom",padx=20,pady=30)
        ctk.CTkLabel(self.sidebar,text="© 2026 Financial Shop Software",font=ctk.CTkFont(size=11)).pack(side="bottom",pady=5)

    def create_content_area(self):
        self.content_frame=ctk.CTkFrame(self,corner_radius=0,fg_color="transparent"); self.content_frame.grid(row=0,column=1,sticky="nsew")
        self.content_frame.grid_columnconfigure(0,weight=1); self.content_frame.grid_rowconfigure(2,weight=1)
        h=ctk.CTkFrame(self.content_frame,height=90); h.grid(row=0,column=0,padx=20,pady=(20,10),sticky="ew"); h.grid_columnconfigure(0,weight=1)
        ctk.CTkLabel(h,text="📊 Dashboard",font=ctk.CTkFont(size=30,weight="bold")).grid(row=0,column=0,padx=25,pady=20,sticky="w")
        ctk.CTkButton(h,text="🔄 Refresh",width=120,command=self.refresh_dashboard).grid(row=0,column=1,padx=25)
        self.summary_frame=ctk.CTkFrame(self.content_frame,fg_color="transparent"); self.summary_frame.grid(row=1,column=0,padx=20,pady=10,sticky="ew")
        for i in range(4): self.summary_frame.grid_columnconfigure(i,weight=1)
        self.total_balance_card=self.create_summary_card(0,"💰 Total Cash"); self.cash_balance_card=self.create_summary_card(1,"💵 Cash")
        self.today_profit_card=self.create_summary_card(2,"📈 Today's Profit"); self.total_profit_card=self.create_summary_card(3,"🏆 Total Profit")
        container=ctk.CTkScrollableFrame(self.content_frame); container.grid(row=2,column=0,padx=20,pady=(5,20),sticky="nsew"); container.grid_columnconfigure(0,weight=1)
        ctk.CTkLabel(container,text="Financial App Balances",font=ctk.CTkFont(size=22,weight="bold")).grid(row=0,column=0,padx=10,pady=(10,5),sticky="w")
        self.account_cards_frame=ctk.CTkFrame(container,fg_color="transparent"); self.account_cards_frame.grid(row=1,column=0,padx=5,pady=5,sticky="ew")
        for i in range(3): self.account_cards_frame.grid_columnconfigure(i,weight=1)

    def create_summary_card(self,column,title):
        card=ctk.CTkFrame(self.summary_frame,height=125); card.grid(row=0,column=column,padx=8,sticky="ew"); card.grid_propagate(False)
        ctk.CTkLabel(card,text=title,font=ctk.CTkFont(size=15)).pack(pady=(22,5))
        label=ctk.CTkLabel(card,text="৳ 0.00",font=ctk.CTkFont(size=25,weight="bold")); label.pack(pady=(3,15)); return label

    def refresh_dashboard(self):
        try:
            s=get_dashboard_data()
            self.total_balance_card.configure(text=f'৳ {s["total_balance"]:,.2f}'); self.cash_balance_card.configure(text=f'৳ {s["cash_balance"]:,.2f}')
            self.today_profit_card.configure(text=f'৳ {s["today_profit"]:,.2f}'); self.total_profit_card.configure(text=f'৳ {s["total_profit"]:,.2f}')
            for w in self.account_cards_frame.winfo_children(): w.destroy()
            accounts=get_accounts(include_cash=False)
            if not accounts:
                ctk.CTkLabel(self.account_cards_frame,text="কোন Financial App পাওয়া যায়নি।",font=ctk.CTkFont(size=16)).grid(row=0,column=0,columnspan=3,pady=50); return
            for i,a in enumerate(accounts): self.create_account_card(a,i//3,i%3)
        except Exception as e: messagebox.showerror("Dashboard Error",str(e))

    def create_account_card(self,account,row,column):
        card=ctk.CTkFrame(self.account_cards_frame,height=160); card.grid(row=row,column=column,padx=10,pady=10,sticky="ew"); card.grid_propagate(False)
        ctk.CTkLabel(card,text="📱",font=ctk.CTkFont(size=26)).pack(pady=(15,2))
        ctk.CTkLabel(card,text=account["name"],font=ctk.CTkFont(size=18,weight="bold")).pack()
        ctk.CTkLabel(card,text=f'App Balance: ৳ {float(account["balance"]):,.2f}',font=ctk.CTkFont(size=18,weight="bold")).pack(pady=(10,3))

    def open_transaction(self):
        if self.transaction_window is not None and self.transaction_window.winfo_exists():
            self.transaction_window.deiconify(); self.transaction_window.lift(); self.transaction_window.focus_force(); return
        self.transaction_window=TransactionWindow(master=self,refresh_callback=self.refresh_dashboard)
        self.transaction_window.transient(self); self.transaction_window.lift(); self.transaction_window.focus_force()
        self.transaction_window.after(100,lambda:(self.transaction_window.lift(),self.transaction_window.focus_force()))

    def open_reports(self):
        try:
            from ui.reports import ReportsWindow
            if self.report_window is not None and self.report_window.winfo_exists():
                self.report_window.deiconify(); self.report_window.lift(); self.report_window.focus_force(); return
            self.report_window=ReportsWindow(master=self); self.report_window.transient(self); self.report_window.lift(); self.report_window.focus_force()
        except Exception as e: messagebox.showerror("Reports Error",str(e))

    def open_manage_accounts(self):
        try:
            from ui.manage_accounts import ManageAccountsWindow
            if self.manage_window is not None and self.manage_window.winfo_exists():
                self.manage_window.deiconify(); self.manage_window.lift(); self.manage_window.focus_force(); return
            self.manage_window=ManageAccountsWindow(master=self,refresh_callback=self.refresh_dashboard)
            self.manage_window.transient(self); self.manage_window.lift(); self.manage_window.focus_force()
        except ImportError: messagebox.showinfo("Manage Apps","ui/manage_accounts.py এখনো তৈরি করা হয়নি।")
        except Exception as e: messagebox.showerror("Error",str(e))

    def close_application(self):
        if messagebox.askyesno("Exit","আপনি কি Software বন্ধ করতে চান?"): self.destroy()

if __name__=="__main__":
    from database import initialize_database
    initialize_database(); ctk.set_appearance_mode("dark"); ctk.set_default_color_theme("blue")
    app=Dashboard(); app.mainloop()
