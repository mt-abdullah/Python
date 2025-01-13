from tkinter import *

# Initialize the main window
root = Tk()
root.geometry("1000x550")
root.title("Bill Management")
root.resizable(False, False)

# Functions
def Reset():
    dosa.set("")
    cookies.set("")
    tea.set("")
    coffee.set("")
    juice.set("")
    pancakes.set("")
    eggs.set("")
    total_bill.set("")  # Reset total bill as well

def Total():
    try:
        a1 = int(dosa.get()) if dosa.get().isdigit() else 0
        a2 = int(cookies.get()) if cookies.get().isdigit() else 0
        a3 = int(tea.get()) if tea.get().isdigit() else 0
        a4 = int(coffee.get()) if coffee.get().isdigit() else 0
        a5 = int(juice.get()) if juice.get().isdigit() else 0
        a6 = int(pancakes.get()) if pancakes.get().isdigit() else 0
        a7 = int(eggs.get()) if eggs.get().isdigit() else 0

        # Prices
        c1 = 60 * a1
        c2 = 30 * a2
        c3 = 7 * a3
        c4 = 100 * a4
        c5 = 20 * a5
        c6 = 15 * a6
        c7 = 7 * a7

        # Calculate the total cost
        totalcost = c1 + c2 + c3 + c4 + c5 + c6 + c7
        
        # Format the total cost as a string with 2 decimal places
        string_bill = "Rs. " + str('%.2f' % totalcost)

        # Set the formatted string to the total_bill variable
        total_bill.set(string_bill)
    except Exception as e:
        total_bill.set("Invalid input")

# Variables for user inputs
dosa = StringVar()
cookies = StringVar()
tea = StringVar()
coffee = StringVar()
juice = StringVar()
pancakes = StringVar()
eggs = StringVar()
total_bill = StringVar()

# Title Label
Label(root, text="BILL MANAGEMENT", bg="black", fg="white", font=("calibri", 30), width=300, height=2).pack()

# Menu Card Frame
menu_frame = Frame(root, bg="lightgreen", highlightbackground="black", highlightthickness=1, width=300, height=400)
menu_frame.place(x=10, y=100)

# Menu Card Title
Label(menu_frame, text="Menu", font=("Gabriola", 35, "bold"), fg="black", bg="lightgreen").place(x=100, y=10)

# Menu Items
menu_items = [
    ("Dosa.......Rs.60/plate", 80),
    ("Cookies....Rs.30/plate", 120),
    ("Tea........Rs.7/cup", 160),
    ("Coffee.....Rs.100/cup", 200),
    ("Juice......Rs.20/glass", 240),
    ("Pancakes...Rs.15/pack", 280),
    ("Eggs.......Rs.7/egg", 320),
]
for item, y_pos in menu_items:
    Label(menu_frame, font=("Lucida Calligraphy", 15, 'bold'), text=item, fg="black", bg="lightgreen").place(x=10, y=y_pos)

# Input Frame
input_frame = Frame(root, bd=5, height=400, width=330, relief=RAISED)
input_frame.place(x=330, y=100)

# Labels and Entry Boxes
items = ["Dosa", "Cookies", "Tea", "Coffee", "Juice", "Pancakes", "Eggs"]
variables = [dosa, cookies, tea, coffee, juice, pancakes, eggs]

for i, item in enumerate(items):
    Label(input_frame, font=("aria", 15, 'bold'), text=item, width=10, fg="blue4", anchor="w").grid(row=i, column=0, pady=10)
    Entry(input_frame, font=("aria", 15, 'bold'), textvariable=variables[i], bd=5, width=10, bg="lightpink").grid(row=i, column=1, pady=10)

# Buttons
Button(input_frame, bd=5, fg="black", bg="lightblue", font=("ariel", 14, 'bold'), width=8, text="Reset", command=Reset).grid(row=7, column=0, pady=20)
Button(input_frame, bd=5, fg="black", bg="lightblue", font=("ariel", 14, 'bold'), width=8, text="Total", command=Total).grid(row=7, column=1, pady=20)

# Total Frame
total_frame = Frame(root, bd=5, height=400, width=300, relief=RAISED)
total_frame.place(x=670, y=100)

# Updated Total Label
lbl_total = Label(total_frame, font=('aria', 20, 'bold'), text="Total Bill", width=16, fg="lightyellow", bg="black")
lbl_total.place(x=0, y=50)

# Total Entry
entry_total = Entry(total_frame, font=('aria', 20, 'bold'), textvariable=total_bill, bd=6, width=15, bg="lightgreen")
entry_total.place(x=20, y=100)

root.mainloop()
