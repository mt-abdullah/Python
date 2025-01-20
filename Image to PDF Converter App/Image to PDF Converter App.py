import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import Image

def select_image():
    file_path = filedialog.askopenfilename(
        title="Select an Image",
        filetypes=[("Image Files", "*.png;*.jpg;*.jpeg;*.bmp;*.tiff")]
    )
    if file_path:
        entry_file_path.delete(0, tk.END)
        entry_file_path.insert(0, file_path)

def convert_to_pdf():
    image_path = entry_file_path.get()
    if not image_path:
        messagebox.showerror("Error", "Please select an image file first.")
        return
    
    save_path = filedialog.asksaveasfilename(
        title="Save PDF As",
        defaultextension=".pdf",
        filetypes=[("PDF Files", "*.pdf")]
    )
    if not save_path:
        return
    
    try:
        image = Image.open(image_path)
        
        # Handle transparency for palette-based or RGBA images
        if image.mode == "P" or image.mode == "RGBA":
            image = image.convert("RGBA")
            new_image = Image.new("RGB", image.size, (255, 255, 255))  # White background
            new_image.paste(image, mask=image.split()[3])  # Use alpha channel as mask
            image = new_image
        else:
            image = image.convert("RGB")
        
        pdf_path = save_path
        image.save(pdf_path, "PDF")
        messagebox.showinfo("Success", f"Image successfully converted to PDF!\nSaved at: {pdf_path}")
    except Exception as e:
        messagebox.showerror("Error", f"An error occurred:\n{e}")

# Create the GUI
app = tk.Tk()
app.title("Image to PDF Converter")
app.geometry("400x200")
app.resizable(False, False)

# Widgets
label_title = tk.Label(app, text="Image to PDF Converter", font=("Arial", 16))
label_title.pack(pady=10)

frame_file_selection = tk.Frame(app)
frame_file_selection.pack(pady=10)

label_file_path = tk.Label(frame_file_selection, text="Image Path:")
label_file_path.grid(row=0, column=0, padx=5, pady=5)

entry_file_path = tk.Entry(frame_file_selection, width=30)
entry_file_path.grid(row=0, column=1, padx=5, pady=5)

button_browse = tk.Button(frame_file_selection, text="Browse", command=select_image)
button_browse.grid(row=0, column=2, padx=5, pady=5)

button_convert = tk.Button(app, text="Convert to PDF", command=convert_to_pdf, bg="green", fg="white")
button_convert.pack(pady=20)

# Start the main loop
app.mainloop()
