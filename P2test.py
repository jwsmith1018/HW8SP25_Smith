import tkinter as tk
from tkinter import ttk
from abc import ABC, abstractmethod

class Rankine(ABC):
    def __init__(self, T1, T2, T3, T4):
        self.T1 = T1
        self.T2 = T2
        self.T3 = T3
        self.T4 = T4

    @abstractmethod
    def thermal_efficiency(self):
        pass

class IdealRankine(Rankine):
    def thermal_efficiency(self):
        efficiency = 1 - ((self.T1 - self.T4) / (self.T3 - self.T2))
        return efficiency

class ReheatRankine(Rankine):
    def __init__(self, T1, T2, T3, T4, T5):
        super().__init__(T1, T2, T3, T4)
        self.T5 = T5

    def thermal_efficiency(self):
        efficiency = 1 - ((self.T1 - self.T4) + (self.T2 - self.T5)) / (self.T3 - self.T2)
        return efficiency

class RankineCycle:
    def __init__(self):
        self.cycle = None
        self.efficiency = None

    def set_cycle(self, cycle):
        self.cycle = cycle

    def compute_efficiency(self):
        if self.cycle:
            self.efficiency = self.cycle.thermal_efficiency()
            return self.efficiency
        else:
            return None

    def get_efficiency(self):
        return self.efficiency

class View:
    def __init__(self, controller, root, rankineCycle):
        self.controller = controller
        self.root = root
        self.rankineCycle = rankineCycle

        self.root.title("Rankine Cycle Calculator")

        self.frame = ttk.Frame(root, padding="10")
        self.frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        self.temp_labels = ["T1", "T2", "T3", "T4", "T5"]
        self.temp_entries = {}
        for i, label in enumerate(self.temp_labels):
            ttk.Label(self.frame, text=label).grid(row=i, column=0)
            entry = ttk.Entry(self.frame)
            entry.grid(row=i, column=1)
            self.temp_entries[label] = entry

        self.cycle_var = tk.StringVar()
        self.cycle_var.set("Ideal")
        ttk.Label(self.frame, text="Cycle Type:").grid(row=6, column=0)
        ttk.OptionMenu(self.frame, self.cycle_var, "Ideal", "Ideal", "Reheat").grid(row=6, column=1)

        ttk.Button(self.frame, text="Compute Efficiency", command=self.compute_efficiency).grid(row=7, column=0, columnspan=2)

        self.result_label = ttk.Label(self.frame, text="Efficiency:")
        self.result_label.grid(row=8, column=0, columnspan=2)

    def compute_efficiency(self):
        temps = {}
        for key, entry in self.temp_entries.items():
            val = entry.get()
            if val:
                temps[key] = float(val)

        cycle_type = self.cycle_var.get()

        if cycle_type == "Ideal":
            cycle = IdealRankine(temps["T1"], temps["T2"], temps["T3"], temps["T4"])
        elif cycle_type == "Reheat":
            cycle = ReheatRankine(temps["T1"], temps["T2"], temps["T3"], temps["T4"], temps["T5"])
        else:
            self.result_label.config(text="Invalid cycle type")
            return

        self.rankineCycle.set_cycle(cycle)
        eff = self.rankineCycle.compute_efficiency()
        if eff is not None:
            self.result_label.config(text=f"Efficiency: {eff:.2%}")
        else:
            self.result_label.config(text="Error computing efficiency")

class Controller:
    def __init__(self, root):
        self.model = RankineCycle()
        self.view = View(self, root, self.model)

if __name__ == "__main__":
    root = tk.Tk()
    app = Controller(root)
    root.mainloop()
