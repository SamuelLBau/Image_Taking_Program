import Tkinter as tk

from GUI import main_app

def main():
    root = tk.Tk()
    root.minsize(10,10)
    root.maxsize(500,500)
    app = main_app(master=root)
    app.mainloop()
    root.destroy()

if __name__ == "__main__":
    main()