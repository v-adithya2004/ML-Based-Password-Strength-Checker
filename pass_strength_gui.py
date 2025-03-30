import tkinter as tk
from tkinter import messagebox
from pass_strength_check import create_database, check_password_strength, store_password_data, train_model, improve_password_ml, improve_password_basic

create_database()

def analyze_password():
    password = entry_password.get()
    if not password:
        messagebox.showerror("Error", "Please enter a password")
        return

    classification, strength, rules_failed = check_password_strength(password)
    result_text.set(f"\nPassword Strength: {classification}\nScore: {strength:.2f}")
    store_password_data(password, strength)

    if rules_failed:
        failed_rules.set("\n".join(rules_failed))
    else:
        failed_rules.set("All requirements met!")

    if classification in ["Very Weak", "Weak", "Medium"]:
        model, patterns = train_model()
        if model:
            suggestions = improve_password_ml(password, model, patterns)
        else:
            suggestions = improve_password_basic(password)
        
        suggestion_list.set("\n".join(suggestions))
    else:
        suggestion_list.set("No suggestions needed. Password is strong!")

def reset_fields():
    entry_password.delete(0, tk.END)
    result_text.set("")
    failed_rules.set("")
    suggestion_list.set("")

root = tk.Tk()
root.title("Password Strength Checker")
root.geometry("500x450")
root.configure(bg="#f0f0f0")

frame = tk.Frame(root, padx=10, pady=10, bg="#f0f0f0")
frame.pack(expand=True, fill="both")

entry_label = tk.Label(frame, text="Enter Password:", bg="#f0f0f0", font=("Arial", 12))
entry_label.pack(pady=5)
entry_password = tk.Entry(frame, width=40, show="*", font=("Arial", 12))
entry_password.pack(pady=5)

btn_frame = tk.Frame(frame, bg="#f0f0f0")
btn_frame.pack(pady=5)

btn_analyze = tk.Button(btn_frame, text="Check Strength", command=analyze_password, bg="#4caf50", fg="white", font=("Arial", 10, "bold"))
btn_analyze.grid(row=0, column=0, padx=5)

btn_reset = tk.Button(btn_frame, text="Reset", command=reset_fields, bg="#f44336", fg="white", font=("Arial", 10, "bold"))
btn_reset.grid(row=0, column=1, padx=5)

result_text = tk.StringVar()
result_label = tk.Label(frame, textvariable=result_text, fg="#1e88e5", font=("Arial", 12, "bold"), bg="#f0f0f0")
result_label.pack(pady=5)

failed_rules = tk.StringVar()
failed_label = tk.Label(frame, textvariable=failed_rules, fg="#e53935", font=("Arial", 10), bg="#f0f0f0")
failed_label.pack(pady=5)

suggestion_label = tk.Label(frame, text="Improvement Suggestions:", bg="#f0f0f0", font=("Arial", 12))
suggestion_label.pack(pady=5)

suggestion_list = tk.StringVar()
suggestion_box = tk.Label(frame, textvariable=suggestion_list, fg="#43a047", font=("Arial", 10), bg="#f0f0f0")
suggestion_box.pack(pady=5)

root.mainloop()
