import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
import json
import os


class TrainingPlanner:
    def __init__(self, root):
        self.root = root
        self.root.title("Training Planner (План тренировок)")
        self.root.geometry("900x700")

        # Данные тренировок
        self.workouts = []
        self.filtered_workouts = []

        self.setup_ui()
        self.load_data()
        self.refresh_table()

    def setup_ui(self):
        # Форма ввода
        input_frame = ttk.LabelFrame(self.root, text="Добавить тренировку", padding=10)
        input_frame.pack(fill="x", padx=10, pady=5)

        ttk.Label(input_frame, text="Дата (YYYY-MM-DD):").grid(row=0, column=0, sticky="w")
        self.date_entry = ttk.Entry(input_frame, width=15)
        self.date_entry.grid(row=0, column=1, padx=5)

        ttk.Label(input_frame, text="Тип:").grid(row=0, column=2, sticky="w")
        self.type_entry = ttk.Entry(input_frame, width=15)
        self.type_entry.grid(row=0, column=3, padx=5)

        ttk.Label(input_frame, text="Длительность (мин):").grid(row=0, column=4, sticky="w")
        self.duration_entry = ttk.Entry(input_frame, width=10)
        self.duration_entry.grid(row=0, column=5, padx=5)

        ttk.Button(input_frame, text="Добавить", command=self.add_workout).grid(row=0, column=6, padx=10)

        # Фильтры
        filter_frame = ttk.LabelFrame(self.root, text="Фильтры", padding=10)
        filter_frame.pack(fill="x", padx=10, pady=5)

        ttk.Label(filter_frame, text="Тип:").grid(row=0, column=0, sticky="w")
        self.type_filter = ttk.Combobox(filter_frame, width=15)
        self.type_filter.grid(row=0, column=1, padx=5)
        self.type_filter.bind('<<ComboboxSelected>>', self.apply_filters)

        ttk.Label(filter_frame, text="Дата:").grid(row=0, column=2, sticky="w")
        self.date_filter = ttk.Entry(filter_frame, width=15)
        self.date_filter.grid(row=0, column=3, padx=5)
        ttk.Button(filter_frame, text="Применить", command=self.apply_filters).grid(row=0, column=4, padx=5)
        ttk.Button(filter_frame, text="Сбросить", command=self.reset_filters).grid(row=0, column=5, padx=5)

        # Таблица
        table_frame = ttk.Frame(self.root)
        table_frame.pack(fill="both", expand=True, padx=10, pady=5)

        # Treeview
        columns = ("Дата", "Тип", "Длительность")
        self.tree = ttk.Treeview(table_frame, columns=columns, show="headings", height=20)

        self.tree.heading("Дата", text="Дата")
        self.tree.heading("Тип", text="Тип тренировки")
        self.tree.heading("Длительность", text="Длительность (мин)")

        self.tree.column("Дата", width=120)
        self.tree.column("Тип", width=200)
        self.tree.column("Длительность", width=120)

        # Скроллбары
        v_scrollbar = ttk.Scrollbar(table_frame, orient="vertical", command=self.tree.yview)
        h_scrollbar = ttk.Scrollbar(table_frame, orient="horizontal", command=self.tree.xview)
        self.tree.configure(yscrollcommand=v_scrollbar.set, xscrollcommand=h_scrollbar.set)

        self.tree.pack(side="left", fill="both", expand=True)
        v_scrollbar.pack(side="right", fill="y")
        h_scrollbar.pack(side="bottom", fill="x")

        # Кнопки управления
        btn_frame = ttk.Frame(self.root)
        btn_frame.pack(fill="x", padx=10, pady=5)

        ttk.Button(btn_frame, text="Сохранить", command=self.save_data).pack(side="left", padx=5)
        ttk.Button(btn_frame, text="Загрузить", command=self.load_data).pack(side="left", padx=5)
        ttk.Button(btn_frame, text="Очистить таблицу", command=self.clear_table).pack(side="right", padx=5)

    def validate_date(self, date_str):
        try:
            datetime.strptime(date_str, "%Y-%m-%d")
            return True
        except ValueError:
            return False

    def validate_duration(self, duration_str):
        try:
            duration = float(duration_str)
            return duration > 0
        except ValueError:
            return False

    def add_workout(self):
        date = self.date_entry.get().strip()
        workout_type = self.type_entry.get().strip()
        duration = self.duration_entry.get().strip()

        if not date or not workout_type or not duration:
            messagebox.showerror("Ошибка", "Заполните все поля!")
            return

        if not self.validate_date(date):
            messagebox.showerror("Ошибка", "Дата в формате YYYY-MM-DD (например, 2026-05-04)!")
            return

        if not self.validate_duration(duration):
            messagebox.showerror("Ошибка", "Длительность - положительное число!")
            return

        workout = {"date": date, "type": workout_type, "duration": duration}
        self.workouts.append(workout)
        self.apply_filters()
        self.clear_inputs()
        self.update_type_filter()

    def clear_inputs(self):
        self.date_entry.delete(0, tk.END)
        self.type_entry.delete(0, tk.END)
        self.duration_entry.delete(0, tk.END)

    def update_type_filter(self):
        types = ["Все"] + list(set(w["type"] for w in self.workouts))
        self.type_filter["values"] = types
        if types[0]:
            self.type_filter.set(types[0])

    def apply_filters(self, event=None):
        self.filtered_workouts = self.workouts.copy()

        type_filter = self.type_filter.get()
        if type_filter and type_filter != "Все":
            self.filtered_workouts = [w for w in self.filtered_workouts if w["type"] == type_filter]

        date_filter = self.date_filter.get().strip()
        if date_filter:
            if not self.validate_date(date_filter):
                messagebox.showerror("Ошибка", "Фильтр даты в формате YYYY-MM-DD!")
                return
            self.filtered_workouts = [w for w in self.filtered_workouts if w["date"] == date_filter]

        self.refresh_table()

    def reset_filters(self):
        self.type_filter.set("Все")
        self.date_filter.delete(0, tk.END)
        self.apply_filters()

    def refresh_table(self):
        # Очистка таблицы
        for item in self.tree.get_children():
            self.tree.delete(item)

        # Заполнение
        for workout in self.filtered_workouts:
            self.tree.insert("", "end", values=(workout["date"], workout["type"], workout["duration"]))

    def clear_table(self):
        if messagebox.askyesno("Подтверждение", "Очистить все тренировки?"):
            self.workouts.clear()
            self.apply_filters()

    def save_data(self):
        try:
            with open("workouts.json", "w", encoding="utf-8") as f:
                json.dump(self.workouts, f, ensure_ascii=False, indent=2)
            messagebox.showinfo("Успех", "Данные сохранены в workouts.json")
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось сохранить: {e}")

    def load_data(self):
        try:
            if os.path.exists("workouts.json"):
                with open("workouts.json", "r", encoding="utf-8") as f:
                    self.workouts = json.load(f)
                self.apply_filters()
                self.update_type_filter()
                messagebox.showinfo("Успех", "Данные загружены")
            else:
                messagebox.showinfo("Инфо", "Файл workouts.json не найден")
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось загрузить: {e}")


if __name__ == "__main__":
    root = tk.Tk()
    app = TrainingPlanner(root)
    root.mainloop()