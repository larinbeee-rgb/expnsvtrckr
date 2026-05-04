import tkinter as tk
from expense_tracker import ExpenseTracker

if __name__ == "__main__":
    root = tk.Tk()
    app = ExpenseTracker(root)
    root.mainloop()