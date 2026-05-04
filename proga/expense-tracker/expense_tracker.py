import tkinter as tk
from tkinter import ttk, messagebox
import json
import os
from datetime import datetime

DATA_FILE = "data/expenses.json"

class ExpenseTracker:
    def __init__(self, root):
        self.root = root
        self.root.title("Менеджер расходов")
        self.root.geometry("700x500")
        self.root.resizable(False, False)

        self.expenses = []
        self.load_data()

        self.category_var = tk.StringVar()
        self.amount_var = tk.StringVar()
        self.date_var = tk.StringVar(value=datetime.now().strftime("%Y-%m-%d"))
        self.filter_var = tk.StringVar()

        self.setup_ui()
        self.refresh_table()

    def setup_ui(self):
        input_frame = ttk.LabelFrame(self.root, text="Добавить расход", padding=10)
        input_frame.pack(fill="x", padx=10, pady=5)

        ttk.Label(input_frame, text="Категория:").grid(row=0, column=0, padx=5, pady=5)
        self.category_entry = ttk.Entry(input_frame, textvariable=self.category_var, width=20)
        self.category_entry.grid(row=0, column=1, padx=5, pady=5)

        ttk.Label(input_frame, text="Сумма (₽):").grid(row=0, column=2, padx=5, pady=5)
        self.amount_entry = ttk.Entry(input_frame, textvariable=self.amount_var, width=15)
        self.amount_entry.grid(row=0, column=3, padx=5, pady=5)

        ttk.Label(input_frame, text="Дата (ГГГГ-ММ-ДД):").grid(row=0, column=4, padx=5, pady=5)
        self.date_entry = ttk.Entry(input_frame, textvariable=self.date_var, width=12)
        self.date_entry.grid(row=0, column=5, padx=5, pady=5)

        add_btn = ttk.Button(input_frame, text="Добавить", command=self.add_expense)
        add_btn.grid(row=0, column=6, padx=10, pady=5)

        filter_frame = ttk.LabelFrame(self.root, text="Фильтровать по категории", padding=10)
        filter_frame.pack(fill="x", padx=10, pady=5)

        ttk.Label(filter_frame, text="Категория:").pack(side="left", padx=5)
        self.filter_entry = ttk.Entry(filter_frame, textvariable=self.filter_var, width=20)
        self.filter_entry.pack(side="left", padx=5)
        filter_btn = ttk.Button(filter_frame, text="Применить фильтр", command=self.apply_filter)
        filter_btn.pack(side="left", padx=5)
        reset_btn = ttk.Button(filter_frame, text="Сбросить", command=self.reset_filter)
        reset_btn.pack(side="left", padx=5)

        columns = ("id", "category", "amount", "date")
        self.tree = ttk.Treeview(self.root, columns=columns, show="headings", height=18)
        self.tree.heading("id", text="ID")
        self.tree.heading("category", text="Категория")
        self.tree.heading("amount", text="Сумма (₽)")
        self.tree.heading("date", text="Дата")
        self.tree.column("id", width=50)
        self.tree.column("category", width=200)
        self.tree.column("amount", width=100)
        self.tree.column("date", width=120)
        self.tree.pack(fill="both", expand=True, padx=10, pady=5)

        btn_frame = ttk.Frame(self.root)
        btn_frame.pack(fill="x", padx=10, pady=5)

        delete_btn = ttk.Button(btn_frame, text="Удалить выбранное", command=self.delete_expense)
        delete_btn.pack(side="left", padx=5)

        total_btn = ttk.Button(btn_frame, text="Общая сумма", command=self.show_total)
        total_btn.pack(side="left", padx=5)

    def validate_amount(self, amount_str):
        try:
            amount = float(amount_str)
            if amount <= 0:
                raise ValueError("Сумма должна быть > 0")
            if amount > 1e9:
                raise ValueError("Сумма слишком большая")
            return amount
        except ValueError as e:
            messagebox.showerror("Ошибка ввода", f"Некорректная сумма: {e}")
            return None

    def validate_date(self, date_str):
        try:
            datetime.strptime(date_str, "%Y-%m-%d")
            return True
        except ValueError:
            messagebox.showerror("Ошибка ввода", "Дата должна быть в формате ГГГГ-ММ-ДД")
            return False

    def add_expense(self):
        category = self.category_var.get().strip()
        amount_str = self.amount_var.get().strip()
        date_str = self.date_var.get().strip()

        if not category:
            messagebox.showerror("Ошибка", "Введите категорию")
            return

        amount = self.validate_amount(amount_str)
        if amount is None:
            return

        if not self.validate_date(date_str):
            return

        new_id = max([e["id"] for e in self.expenses], default=0) + 1
        expense = {
            "id": new_id,
            "category": category,
            "amount": amount,
            "date": date_str
        }
        self.expenses.append(expense)
        self.save_data()
        self.refresh_table()
        self.category_var.set("")
        self.amount_var.set("")
        self.date_var.set(datetime.now().strftime("%Y-%m-%d"))
        messagebox.showinfo("Успех", "Расход добавлен")

    def delete_expense(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Предупреждение", "Выберите расход для удаления")
            return

        item = self.tree.item(selected[0])
        expense_id = item["values"][0]

        self.expenses = [e for e in self.expenses if e["id"] != expense_id]
        self.save_data()
        self.refresh_table()
        messagebox.showinfo("Успех", "Расход удалён")

    def apply_filter(self):
        filter_category = self.filter_var.get().strip().lower()
        if not filter_category:
            self.refresh_table()
            return

        filtered = [e for e in self.expenses if filter_category in e["category"].lower()]
        self.refresh_table(filtered)

    def reset_filter(self):
        self.filter_var.set("")
        self.refresh_table()

    def refresh_table(self, data=None):
        for row in self.tree.get_children():
            self.tree.delete(row)

        if data is None:
            data = self.expenses

        for expense in data:
            self.tree.insert("", "end", values=(
                expense["id"],
                expense["category"],
                f"{expense['amount']:.2f}",
                expense["date"]
            ))

    def show_total(self):
        total = sum(e["amount"] for e in self.expenses)
        messagebox.showinfo("Общая сумма", f"Всего расходов: {total:.2f} ₽")

    def load_data(self):
        if not os.path.exists(DATA_FILE):
            self.expenses = []
            return
        try:
            with open(DATA_FILE, "r", encoding="utf-8") as f:
                self.expenses = json.load(f)
        except (json.JSONDecodeError, FileNotFoundError):
            self.expenses = []

    def save_data(self):
        os.makedirs(os.path.dirname(DATA_FILE), exist_ok=True)
        with open(DATA_FILE, "w", encoding="utf-8") as f:
            json.dump(self.expenses, f, indent=4, ensure_ascii=False)