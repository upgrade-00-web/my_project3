import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime

from finance_classes import FinanceManager, Transaction, TransactionType


class FinanceApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Учет личных финансов")
        self.root.geometry("850x600")
        self.manager = FinanceManager()
        self.setup_ui()
        self.update_table()
        self.update_balance()

    def setup_ui(self):
        form = ttk.LabelFrame(self.root, text="Добавить операцию", padding=10)
        form.pack(fill=tk.X, padx=10, pady=8)

        ttk.Label(form, text="Сумма:").grid(row=0, column=0, sticky="w", padx=4, pady=4)
        self.amount_entry = ttk.Entry(form, width=18)
        self.amount_entry.grid(row=0, column=1, padx=4, pady=4)

        ttk.Label(form, text="Категория:").grid(row=0, column=2, sticky="w", padx=4, pady=4)
        self.category_var = tk.StringVar()
        self.category_combo = ttk.Combobox(
            form, textvariable=self.category_var, state="readonly", width=20
        )
        self.category_combo["values"] = [c.name for c in self.manager.categories]
        self.category_combo.grid(row=0, column=3, padx=4, pady=4)
        self.category_combo.current(0)

        ttk.Label(form, text="Дата (ГГГГ-ММ-ДД):").grid(
            row=1, column=0, sticky="w", padx=4, pady=4
        )
        self.date_entry = ttk.Entry(form, width=18)
        self.date_entry.insert(0, datetime.now().strftime("%Y-%m-%d"))
        self.date_entry.grid(row=1, column=1, padx=4, pady=4)

        ttk.Label(form, text="Описание:").grid(row=1, column=2, sticky="w", padx=4, pady=4)
        self.desc_entry = ttk.Entry(form, width=23)
        self.desc_entry.grid(row=1, column=3, padx=4, pady=4)

        buttons = ttk.Frame(form)
        buttons.grid(row=2, column=0, columnspan=4, pady=8)
        ttk.Button(buttons, text="Добавить", command=self.add_transaction).pack(side=tk.LEFT, padx=5)
        ttk.Button(buttons, text="Удалить выбранную", command=self.delete_transaction).pack(side=tk.LEFT, padx=5)
        ttk.Button(buttons, text="Аналитика", command=self.show_analytics).pack(side=tk.LEFT, padx=5)

        info = ttk.LabelFrame(self.root, text="Финансовая информация", padding=10)
        info.pack(fill=tk.X, padx=10, pady=4)
        self.balance_label = ttk.Label(info, text="Баланс: 0.00", font=("Arial", 12, "bold"))
        self.balance_label.pack()

        table_frame = ttk.LabelFrame(self.root, text="История операций", padding=8)
        table_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=8)
        columns = ("date", "category", "type", "amount", "description")
        self.tree = ttk.Treeview(table_frame, columns=columns, show="headings")
        headings = {
            "date": "Дата",
            "category": "Категория",
            "type": "Тип",
            "amount": "Сумма",
            "description": "Описание",
        }
        widths = {"date": 105, "category": 130, "type": 85, "amount": 100, "description": 250}
        for column in columns:
            self.tree.heading(column, text=headings[column])
            self.tree.column(column, width=widths[column], anchor="w")

        scrollbar = ttk.Scrollbar(table_frame, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.tree.pack(fill=tk.BOTH, expand=True)

    def add_transaction(self):
        try:
            amount = float(self.amount_entry.get().replace(",", "."))
            if amount <= 0:
                raise ValueError
            date = self.date_entry.get().strip()
            datetime.strptime(date, "%Y-%m-%d")
            category_name = self.category_var.get()
            category = next((c for c in self.manager.categories if c.name == category_name), None)
            if category is None:
                messagebox.showwarning("Ошибка", "Выберите категорию.")
                return

            transaction = Transaction(amount, category, date, self.desc_entry.get().strip())
            self.manager.add_transaction(transaction)
            self.update_table()
            self.update_balance()
            self.amount_entry.delete(0, tk.END)
            self.desc_entry.delete(0, tk.END)
            messagebox.showinfo("Готово", "Операция добавлена.")
        except ValueError:
            messagebox.showerror("Ошибка", "Введите положительную сумму и дату в формате ГГГГ-ММ-ДД.")

    def delete_transaction(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Внимание", "Сначала выберите операцию в таблице.")
            return
        index = self.tree.index(selected[0])
        self.manager.delete_transaction(index)
        self.update_table()
        self.update_balance()

    def show_analytics(self):
        summary = self.manager.get_category_summary()
        window = tk.Toplevel(self.root)
        window.title("Аналитика по категориям")
        window.geometry("320x350")
        if not summary:
            ttk.Label(window, text="Операций пока нет.").pack(padx=12, pady=12)
            return
        for category, amount in summary.items():
            ttk.Label(window, text=f"{category}: {amount:.2f}").pack(
                padx=12, pady=4, anchor="w"
            )

    def update_table(self):
        for item in self.tree.get_children():
            self.tree.delete(item)
        for transaction in self.manager.transactions:
            self.tree.insert(
                "", tk.END,
                values=(
                    transaction.date,
                    transaction.category.name,
                    transaction.category.type.value,
                    f"{transaction.amount:.2f}",
                    transaction.description,
                ),
            )

    def update_balance(self):
        balance = self.manager.get_balance()
        self.balance_label.config(text=f"Текущий баланс: {balance:.2f}")


if __name__ == "__main__":
    root = tk.Tk()
    app = FinanceApp(root)
    root.mainloop()
