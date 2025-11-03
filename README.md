# Salary Management System (Tkinter)

A practical Python GUI application for managing employee salaries and producing payslips. Built with Tkinter and simple CSV persistence for learning and small-scale use.

## Features
- Add / Update / Delete employee records
- Store data in `employees.csv`
- Generate a formatted payslip
- Basic tax estimate (Old / New Indian tax regimes)
- Modernized UI with configurable colors and styles

## Requirements
- Python 3.8+
- Standard library only (tkinter, csv, datetime, os)

## Installation
1. Clone or download this repository into a folder, e.g.:
   - `c:\Users\91899\Desktop\iwp`
2. Ensure Python is installed and tkinter is available.

## Running
From the project folder run:
```
python iwp.py
```
(If using an IDE, open `iwp.py` and run.)

## Files
- `iwp.py` — main application (GUI, data handling, tax estimate)
- `employees.csv` — data file created automatically
- `README.md` — this file

## Quick Usage
1. Open the app.
2. Enter employee details (Basic / HRA / Other monthly components) and click "Add Employee".
3. Select an employee in the list to edit or delete.
4. Use "Generate Payslip" for a printable payslip.
5. Use "Calculate Tax" to see an estimated annual tax and monthly TDS (New/Old regimes).

## Configuration
- Tax slabs, rebate limits and cess are configurable inside `SalaryApp`:
  - `NEW_REGIME_SLABS`, `OLD_REGIME_SLABS`
  - `NEW_REBATE_LIMIT`, `OLD_REBATE_LIMIT`
  - `CESS_RATE`
- UI colors are stored in the `COLORS` dictionary near the top of `iwp.py`. Change hex codes to customize the appearance.

## Notes & Limitations
- This app is an estimate/demo tool. It does NOT handle:
  - Exact HRA exemption calculations, surcharge rules, payroll statutory remittances, PF/ESI employer shares, or comprehensive tax exemptions.
  - Production-grade security or concurrency for multi-user access.
- For accurate tax filings or payroll compliance, consult a qualified accountant or use certified payroll software.

## Contribution
Contributions and improvements are welcome:
- Open an issue to discuss features/bugs.
- Fork, implement changes, and submit a pull request.

## License
Include a suitable license (e.g., MIT) if you plan to open-source this project.

## Contact
For questions or suggestions, update the repository issues or contact the maintainer listed in the project.

