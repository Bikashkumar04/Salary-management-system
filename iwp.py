# -- coding: utf-8 --
"""
==============================================================================
===          PRACTICAL PYTHON SALARY MANAGEMENT SYSTEM (GUI)             ===
==============================================================================
This is a graphical user interface (GUI) application for managing employee
salaries, built using Python's standard Tkinter library.

Features:
- A user-friendly window with forms and buttons.
- Add, View, Update, and Delete employee records.
- Data is saved to 'employees.csv' for persistence.
- Generates a formatted payslip in a separate pop-up window.
- Includes user feedback through message boxes.

How to Run:
1. Save this code as a Python file (e.g., salary_gui_app.py).
2. Run the file in Spyder (press F5).
3. The application window will appear on your screen.
==============================================================================
"""

import tkinter as tk
from tkinter import ttk, messagebox
import csv
import os
from datetime import datetime

# --- Configuration ---
DATA_FILE = 'employees.csv'
TAX_RATE = 0.20          # 20%
NATIONAL_INSURANCE_RATE = 0.12 # 12%
PENSION_RATE = 0.05      # 5%

# Color scheme
COLORS = {
    'bg': '#f9fafb',           # Very Light Grey (Almost White)
    'frame_bg': '#ffffff',     # Pure White
    'primary': '#06b6d4',      # Modern Teal/Cyan
    'primary_hover': '#0891b2', # Darker Teal
    'text': '#1f2937',         # Dark Slate Grey
    'text_light': '#6b7280',   # Medium Grey
    'border': '#e5e7eb',       # Very Light Grey Border
    'tree_selected': '#ccfbf1', # Very Light Mint/Cyan Selection
    'success': '#10b981',      # Green
    'error': '#dc2626',        # Bright Red
    'warning': '#f59e0b'       # Vibrant Amber/Orange
}

class SalaryApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Salary Management System")
        self.root.geometry("950x600")  # Slightly larger window
        self.root.configure(bg=COLORS['bg'])

        self.employees = self._load_employees()

        # --- Modern Style Configuration ---
        style = ttk.Style()
        
        # Configure main styles with proper background
        style.configure("Modern.TFrame",
                       background=COLORS['frame_bg'])
        
        style.configure("Card.TFrame",
                       background=COLORS['frame_bg'],
                       relief="solid",
                       borderwidth=1)
        
        # Fix label styles with proper background
        style.configure("Modern.TLabel",
                       font=("Segoe UI", 10),
                       background=COLORS['frame_bg'],
                       foreground=COLORS['text'])
        
        style.configure("Header.TLabel",
                       font=("Segoe UI", 12, "bold"),
                       background=COLORS['frame_bg'],
                       foreground=COLORS['text'])

        # Fix button style with proper colors
        style.configure("Modern.TButton",
                       font=("Segoe UI", 10, "bold"),
                       padding=(20, 10))
        
        style.map("Modern.TButton",
                 foreground=[('pressed', 'white'),
                            ('active', 'white')],
                 background=[('pressed', COLORS['primary_hover']),
                            ('active', COLORS['primary'])])

        # Modern entry style
        style.configure("Modern.TEntry",
                       fieldbackground=COLORS['frame_bg'],
                       borderwidth=1)

        # Configure Treeview for modern look
        style.configure("Modern.Treeview",
                       background=COLORS['frame_bg'],
                       fieldbackground=COLORS['frame_bg'],
                       foreground=COLORS['text'],
                       rowheight=30,
                       font=("Segoe UI", 10))
        
        style.configure("Modern.Treeview.Heading",
                       font=("Segoe UI", 10, "bold"),
                       background=COLORS['bg'],
                       foreground=COLORS['text'])
        
        style.map("Modern.Treeview",
                 background=[('selected', COLORS['tree_selected'])],
                 foreground=[('selected', COLORS['text'])])

        # --- Main Frames ---
        # Frame for input form and buttons
        self.controls_frame = ttk.Frame(root, padding="10")
        self.controls_frame.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")

        # Frame for the employee list (Treeview)
        self.list_frame = ttk.Frame(root, padding="10")
        self.list_frame.grid(row=0, column=1, padx=10, pady=10, sticky="nsew")
        
        root.grid_columnconfigure(1, weight=1) # Make the list frame expandable
        root.grid_rowconfigure(0, weight=1)

        # --- Create Widgets ---
        self._create_input_widgets()
        self._create_button_widgets()
        self._create_treeview_widget()
        
        self._populate_treeview()

        # Tax slabs and limits (configurable)
        self.NEW_REGIME_SLABS = [
            (300000, 0.0),
            (600000, 0.05),
            (900000, 0.10),
            (1200000, 0.15),
            (1500000, 0.20),
            (float('inf'), 0.30),
        ]
        self.OLD_REGIME_SLABS = [
            (250000, 0.0),
            (500000, 0.05),
            (1000000, 0.20),
            (float('inf'), 0.30),
        ]
        self.OLD_REBATE_LIMIT = 500000
        self.NEW_REBATE_LIMIT = 700000
        self.CESS_RATE = 0.04

    # --- Widget Creation Methods ---
    def _create_input_widgets(self):
        input_form = ttk.Frame(self.controls_frame, style="Card.TFrame", padding=20)
        input_form.grid(row=0, column=0, sticky="ew", padx=10, pady=10)

        # Header
        header = ttk.Label(input_form, text="Employee Details", style="Header.TLabel")
        header.grid(row=0, column=0, columnspan=2, pady=(0, 20), sticky="w")

        # Name field
        ttk.Label(input_form, text="Name", style="Modern.TLabel").grid(row=1, column=0, padx=5, pady=(0, 5), sticky="w")
        self.name_var = tk.StringVar()
        name_entry = ttk.Entry(input_form, textvariable=self.name_var, width=30, style="Modern.TEntry")
        name_entry.grid(row=2, column=0, columnspan=2, padx=5, pady=(0, 15), sticky="ew")
        self.name_entry = name_entry  # <-- fix: store as attribute (was causing errors)

        # Salary components
        ttk.Label(input_form, text="Basic Pay (monthly)", style="Modern.TLabel").grid(row=5, column=0, padx=5, pady=(0, 5), sticky="w")
        self.basic_var = tk.StringVar(value="0")
        self.basic_entry = ttk.Entry(input_form, textvariable=self.basic_var, width=20, style="Modern.TEntry")
        self.basic_entry.grid(row=6, column=0, padx=5, pady=(0, 10), sticky="w")

        ttk.Label(input_form, text="HRA (monthly)", style="Modern.TLabel").grid(row=5, column=1, padx=5, pady=(0, 5), sticky="w")
        self.hra_var = tk.StringVar(value="0")
        self.hra_entry = ttk.Entry(input_form, textvariable=self.hra_var, width=20, style="Modern.TEntry")
        self.hra_entry.grid(row=6, column=1, padx=5, pady=(0, 10), sticky="w")

        ttk.Label(input_form, text="Other Allowances (monthly)", style="Modern.TLabel").grid(row=7, column=0, padx=5, pady=(0, 5), sticky="w")
        self.other_allow_var = tk.StringVar(value="0")
        self.other_allow_entry = ttk.Entry(input_form, textvariable=self.other_allow_var, width=20, style="Modern.TEntry")
        self.other_allow_entry.grid(row=8, column=0, padx=5, pady=(0, 10), sticky="w")

        ttk.Label(input_form, text="Other Annual Income", style="Modern.TLabel").grid(row=7, column=1, padx=5, pady=(0, 5), sticky="w")
        self.other_income_var = tk.StringVar(value="0")
        self.other_income_entry = ttk.Entry(input_form, textvariable=self.other_income_var, width=20, style="Modern.TEntry")
        self.other_income_entry.grid(row=8, column=1, padx=5, pady=(0, 10), sticky="w")

        # Deductions
        ttk.Label(input_form, text="Section 80C (annual)", style="Modern.TLabel").grid(row=9, column=0, padx=5, pady=(0, 5), sticky="w")
        self.sec80c_var = tk.StringVar(value="0")
        self.sec80c_entry = ttk.Entry(input_form, textvariable=self.sec80c_var, width=20, style="Modern.TEntry")
        self.sec80c_entry.grid(row=10, column=0, padx=5, pady=(0, 10), sticky="w")

        ttk.Label(input_form, text="Section 80D (annual)", style="Modern.TLabel").grid(row=9, column=1, padx=5, pady=(0, 5), sticky="w")
        self.sec80d_var = tk.StringVar(value="0")
        self.sec80d_entry = ttk.Entry(input_form, textvariable=self.sec80d_var, width=20, style="Modern.TEntry")
        self.sec80d_entry.grid(row=10, column=1, padx=5, pady=(0, 10), sticky="w")

        ttk.Label(input_form, text="Standard Deduction (annual)", style="Modern.TLabel").grid(row=11, column=0, padx=5, pady=(0, 5), sticky="w")
        self.std_ded_var = tk.StringVar(value="50000")
        self.std_ded_entry = ttk.Entry(input_form, textvariable=self.std_ded_var, width=20, style="Modern.TEntry")
        self.std_ded_entry.grid(row=12, column=0, padx=5, pady=(0, 10), sticky="w")

        # Tax regime selection
        ttk.Label(input_form, text="Tax Regime", style="Modern.TLabel").grid(row=11, column=1, padx=5, pady=(0, 5), sticky="w")
        self.regime_var = tk.StringVar(value="new")
        rb_new = ttk.Radiobutton(input_form, text="New Regime", variable=self.regime_var, value="new")
        rb_old = ttk.Radiobutton(input_form, text="Old Regime", variable=self.regime_var, value="old")
        rb_new.grid(row=12, column=1, sticky="w")
        rb_old.grid(row=13, column=1, sticky="w")

    def _create_button_widgets(self):
        button_frame = ttk.Frame(self.controls_frame, style="Card.TFrame", padding=20)
        button_frame.grid(row=1, column=0, sticky="ew", padx=10, pady=10)

        buttons = [
            ("Add Employee", self._add_employee),
            ("Update Selected", self._update_employee),
            ("Delete Selected", self._delete_employee),
            ("Generate Payslip", self._generate_payslip),
            ("Calculate Tax", self._calculate_tax),  # <-- new button
            ("Clear Form", self._clear_form)
        ]

        for i, (text, command) in enumerate(buttons):
            btn = ttk.Button(button_frame, text=text, style="Modern.TButton", command=command)
            btn.pack(fill='x', pady=5)

    def _create_treeview_widget(self):
        self.tree = ttk.Treeview(self.list_frame, style="Modern.Treeview",
                                columns=("id", "name", "salary"), show="headings")
        
        # Configure columns
        self.tree.heading("id", text="ID")
        self.tree.heading("name", text="Name")
        self.tree.heading("salary", text="Gross Salary")
        
        self.tree.column("id", width=80, anchor="center")
        self.tree.column("name", width=300)
        self.tree.column("salary", width=200, anchor="e")

        # Add a scrollbar
        scrollbar = ttk.Scrollbar(self.list_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        
        self.tree.grid(row=0, column=0, sticky="nsew")
        scrollbar.grid(row=0, column=1, sticky="ns")
        
        self.list_frame.grid_rowconfigure(0, weight=1)
        self.list_frame.grid_columnconfigure(0, weight=1)
        
        # Bind the selection event to a handler function
        self.tree.bind("<<TreeviewSelect>>", self._on_item_select)

    # --- Data Handling & Business Logic ---
    def _load_employees(self):
        if not os.path.exists(DATA_FILE):
            return {}
        employees = {}
        try:
            with open(DATA_FILE, mode='r', newline='', encoding='utf-8') as file:
                reader = csv.DictReader(file)
                for row in reader:
                    employees[int(row['id'])] = {'name': row['name'], 'gross_salary': float(row['gross_salary'])}
        except Exception as e:
            messagebox.showerror("Load Error", f"Failed to load data from {DATA_FILE}:\n{e}")
        return employees

    def _save_employees(self):
        try:
            with open(DATA_FILE, mode='w', newline='', encoding='utf-8') as file:
                fieldnames = ['id', 'name', 'gross_salary']
                writer = csv.DictWriter(file, fieldnames=fieldnames)
                writer.writeheader()
                for emp_id, data in self.employees.items():
                    writer.writerow({'id': emp_id, **data})
        except Exception as e:
            messagebox.showerror("Save Error", f"Failed to save data to {DATA_FILE}:\n{e}")

    def _get_next_id(self):
        if not self.employees:
            return 1
        return max(self.employees.keys()) + 1
        
    def _populate_treeview(self):
        """Clears and re-populates the employee list from the data dictionary."""
        # Clear existing items
        for item in self.tree.get_children():
            self.tree.delete(item)
            
        # Add new items from the employees dictionary, sorted by ID
        for emp_id in sorted(self.employees.keys()):
            data = self.employees[emp_id]
            # Format salary to 2 decimal places for display
            formatted_salary = f"{data['gross_salary']:,.2f}"
            self.tree.insert("", "end", values=(emp_id, data['name'], formatted_salary))

    # --- Event Handlers and Button Commands ---
    def _on_item_select(self, event):
        """When an item in the tree is selected, populate the form fields."""
        selected_items = self.tree.selection()
        if not selected_items:
            return
            
        selected_item = selected_items[0]
        emp_id = int(self.tree.item(selected_item)["values"][0])
        
        employee_data = self.employees.get(emp_id)
        if employee_data:
            self.name_var.set(employee_data['name'])
            # Populate basic pay from stored gross_salary (approximate)
            try:
                basic_month = float(employee_data.get('gross_salary', 0.0)) / 12.0
            except Exception:
                basic_month = 0.0
            self.basic_var.set(f"{basic_month:.2f}")
            # HRA and other allowances are not stored separately; reset to 0
            self.hra_var.set("0")
            self.other_allow_var.set("0")
            # other annual income/deductions reset (user can edit)
            self.other_income_var.set("0")
            self.sec80c_var.set("0")
            self.sec80d_var.set("0")
            self.std_ded_var.set("50000")
            self.regime_var.set("new")

    def _clear_form(self):
        """Clears the input fields and deselects any item in the tree."""
        self.name_var.set("")
        # Clear component fields instead of non-existent salary_var
        self.basic_var.set("0")
        self.hra_var.set("0")
        self.other_allow_var.set("0")
        self.other_income_var.set("0")
        self.sec80c_var.set("0")
        self.sec80d_var.set("0")
        self.std_ded_var.set("50000")
        self.regime_var.set("new")
        if self.tree.selection():
            self.tree.selection_remove(self.tree.selection()[0])
        # focus basic field for convenience
        try:
            self.basic_entry.focus()
        except Exception:
            self.name_entry.focus()

    def _add_employee(self):
        """Adds a new employee with improved error handling."""
        try:
            name = self.name_var.get().strip()
            # compute gross salary from monthly components
            def to_float_val(var):
                try:
                    return float(var.get())
                except Exception:
                    return 0.0

            basic_month = to_float_val(self.basic_var)
            hra_month = to_float_val(self.hra_var)
            other_allow_month = to_float_val(self.other_allow_var)

            if not name:
                messagebox.showerror("Input Error", "Employee name is required.")
                try:
                    self.name_entry.focus()
                except Exception:
                    pass
                return

            # require at least some basic pay
            if basic_month <= 0 and hra_month <= 0 and other_allow_month <= 0:
                messagebox.showerror("Input Error", "Enter at least one salary component (Basic / HRA / Other).")
                try:
                    self.basic_entry.focus()
                except Exception:
                    pass
                return

            # compute annual gross salary
            gross_annual = (basic_month + hra_month + other_allow_month) * 12.0

            emp_id = self._get_next_id()
            self.employees[emp_id] = {'name': name, 'gross_salary': gross_annual}
            
            self._save_employees()
            self._populate_treeview()
            self._clear_form()
            messagebox.showinfo("Success", f"Employee '{name}' added successfully with ID {emp_id}.")
            
        except Exception as e:
            messagebox.showerror("Error", f"An unexpected error occurred:\n{str(e)}")

    def _update_employee(self):
        """Updates the selected employee with the data from the form."""
        selected_items = self.tree.selection()
        if not selected_items:
            messagebox.showerror("Selection Error", "Please select an employee from the list to update.")
            return

        emp_id = int(self.tree.item(selected_items[0])["values"][0])
        
        name = self.name_var.get().strip()
        # compute gross salary from monthly components
        def to_float_val(var):
            try:
                return float(var.get())
            except Exception:
                return 0.0

        basic_month = to_float_val(self.basic_var)
        hra_month = to_float_val(self.hra_var)
        other_allow_month = to_float_val(self.other_allow_var)

        if not name or (basic_month <= 0 and hra_month <= 0 and other_allow_month <= 0):
            messagebox.showerror("Input Error", "Both name and at least one salary component are required.")
            return

        gross_annual = (basic_month + hra_month + other_allow_month) * 12.0
        
        self.employees[emp_id] = {'name': name, 'gross_salary': gross_annual}
        self._save_employees()
        self._populate_treeview()
        self._clear_form()
        messagebox.showinfo("Success", f"Employee ID {emp_id} updated successfully.")

    def _delete_employee(self):
        """Deletes the selected employee."""
        selected_items = self.tree.selection()
        if not selected_items:
            messagebox.showerror("Selection Error", "Please select an employee to delete.")
            return

        emp_id = int(self.tree.item(selected_items[0])["values"][0])
        name = self.employees[emp_id]['name']

        if messagebox.askyesno("Confirm Deletion", f"Are you sure you want to delete {name} (ID: {emp_id})?"):
            del self.employees[emp_id]
            self._save_employees()
            self._populate_treeview()
            self._clear_form()
            messagebox.showinfo("Success", f"Employee {name} has been deleted.")

    def _generate_payslip(self):
        """Generates payslip with improved error handling."""
        try:
            selected_items = self.tree.selection()
            if not selected_items:
                messagebox.showerror("Selection Error", "Please select an employee to generate a payslip.")
                return

            emp_id = int(self.tree.item(selected_items[0])["values"][0])
            employee = self.employees[emp_id]

            # Create payslip window with error handling
            try:
                payslip_window = tk.Toplevel(self.root)
                payslip_window.title(f"Payslip for {employee['name']}")
                payslip_window.geometry("500x600")
                payslip_window.configure(bg=COLORS['bg'])
                
                # Ensure window is created as modal
                payslip_window.transient(self.root)
                payslip_window.grab_set()
                
                # Add error handling for calculations
                gross_salary = float(employee['gross_salary'])
                tax = gross_salary * TAX_RATE
                ni = gross_salary * NATIONAL_INSURANCE_RATE
                pension = gross_salary * PENSION_RATE
                total_deductions = tax + ni + pension
                net_salary = gross_salary - total_deductions

                payslip_frame = ttk.Frame(payslip_window, style="Card.TFrame", padding=30)
                payslip_frame.pack(expand=True, fill="both", padx=20, pady=20)

                # Modern payslip header
                ttk.Label(payslip_frame, text="PAYSLIP", style="Header.TLabel",
                         font=("Segoe UI", 16, "bold")).grid(row=0, column=0, columnspan=2, pady=(0, 20))

                content = [
                    ("Date", datetime.now().strftime('%Y-%m-%d')),
                    ("Employee ID", emp_id),
                    ("Employee Name", employee['name']),
                    ("Gross Salary", f"{gross_salary:,.2f}"),
                    ("--- DEDUCTIONS ---", ""),
                    (f"Tax ({TAX_RATE*100:.0f}%)", f"({tax:,.2f})"),
                    (f"National Insurance ({NATIONAL_INSURANCE_RATE*100:.0f}%)", f"({ni:,.2f})"),
                    (f"Pension ({PENSION_RATE*100:.0f}%)", f"({pension:,.2f})"),
                    ("Total Deductions", f"({total_deductions:,.2f})"),
                    ("NET SALARY", f"{net_salary:,.2f}")
                ]

                for i, (label, value) in enumerate(content):
                    ttk.Label(payslip_frame, text=label, style="Modern.TLabel").grid(row=i+1, column=0, sticky="w", pady=4)
                    ttk.Label(payslip_frame, text=value, style="Modern.TLabel").grid(row=i+1, column=1, sticky="e", pady=4)
                
                # Make the window modal (disables interaction with the main window)
                payslip_window.transient(self.root)
                payslip_window.grab_set()
                self.root.wait_window(payslip_window)

            except Exception as e:
                messagebox.showerror("Payslip Error", f"Error generating payslip:\n{str(e)}")
                if payslip_window:
                    payslip_window.destroy()
                    
        except Exception as e:
            messagebox.showerror("Error", f"An unexpected error occurred:\n{str(e)}")

    # --- New methods for tax computation ---
    def _compute_tax_from_slabs(self, taxable_income, slabs):
        tax = 0.0
        lower = 0.0
        remaining = taxable_income
        for upper, rate in slabs:
            slab_amount = max(0.0, min(upper - lower, remaining))
            if slab_amount <= 0:
                lower = upper
                continue
            tax += slab_amount * rate
            remaining -= slab_amount
            lower = upper
            if remaining <= 0:
                break
        return tax

    def _calculate_tax(self):
        """Calculate annual tax estimate and show a breakdown to the user."""
        try:
            # Read and validate numeric inputs (monthly inputs converted to annual)
            def to_float(var):
                try:
                    return float(var.get())
                except Exception:
                    return 0.0

            basic_month = to_float(self.basic_var)
            hra_month = to_float(self.hra_var)
            other_allow_month = to_float(self.other_allow_var)
            other_income = to_float(self.other_income_var)

            basic_annual = basic_month * 12
            hra_annual = hra_month * 12
            other_allow_annual = other_allow_month * 12

            gross_salary = basic_annual + hra_annual + other_allow_annual
            gross_total_income = gross_salary + other_income

            # deductions
            std_ded = to_float(self.std_ded_var)
            sec80c = to_float(self.sec80c_var)
            sec80d = to_float(self.sec80d_var)

            total_deductions = std_ded + sec80c + sec80d
            taxable_income = max(0.0, gross_total_income - total_deductions)

            # choose regime slabs
            regime = self.regime_var.get()
            if regime == "new":
                slabs = self.NEW_REGIME_SLABS
                rebate_limit = self.NEW_REBATE_LIMIT
            else:
                slabs = self.OLD_REGIME_SLABS
                rebate_limit = self.OLD_REBATE_LIMIT

            tax_before_cess = self._compute_tax_from_slabs(taxable_income, slabs)

            # rebate u/s87A (basic handling)
            rebate = 0.0
            if taxable_income <= rebate_limit:
                rebate = min(tax_before_cess, tax_before_cess)  # full rebate up to limit -> tax zero
                tax_before_cess = 0.0

            cess = tax_before_cess * self.CESS_RATE
            total_tax = tax_before_cess + cess

            # monthly TDS estimate
            monthly_tds = total_tax / 12.0

            # Show results in a modal window
            result_win = tk.Toplevel(self.root)
            result_win.title("Tax Estimate")
            result_win.geometry("420x360")
            result_win.transient(self.root)
            result_win.grab_set()

            frame = ttk.Frame(result_win, style="Card.TFrame", padding=15)
            frame.pack(expand=True, fill="both", padx=10, pady=10)

            rows = [
                ("Gross Salary (annual):", f"₹{gross_salary:,.2f}"),
                ("Other Income (annual):", f"₹{other_income:,.2f}"),
                ("Gross Total Income:", f"₹{gross_total_income:,.2f}"),
                ("Total Deductions:", f"₹{total_deductions:,.2f}"),
                ("Taxable Income:", f"₹{taxable_income:,.2f}"),
                ("Tax before Cess:", f"₹{tax_before_cess:,.2f}"),
                ("Cess (4%):", f"₹{cess:,.2f}"),
                ("Total Annual Tax:", f"₹{total_tax:,.2f}"),
                ("Estimated Monthly TDS:", f"₹{monthly_tds:,.2f}")
            ]

            for i, (label, val) in enumerate(rows):
                ttk.Label(frame, text=label, style="Modern.TLabel").grid(row=i, column=0, sticky="w", pady=4)
                ttk.Label(frame, text=val, style="Modern.TLabel").grid(row=i, column=1, sticky="e", pady=4)

            ttk.Button(frame, text="Close", style="Modern.TButton", command=result_win.destroy).grid(row=len(rows), column=0, columnspan=2, pady=(10,0))

            self.root.wait_window(result_win)

        except Exception as e:
            messagebox.showerror("Calculation Error", f"Error while calculating tax:\n{e}")

if __name__ == "__main__":
    root = tk.Tk()
    app = SalaryApp(root)
    root.mainloop()