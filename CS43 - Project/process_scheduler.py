import tkinter as tk
from tkinter import ttk, messagebox


class ProcessSchedulerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Process Scheduler")
        self.root.geometry("1400x700")  # Increased width for better output chart display
        
        self.processes = []  # Store processes as a list of dictionaries
        self.selected_algorithm = tk.StringVar(value="FCFS")
        self.time_quantum = tk.IntVar(value=4)  # Default time quantum for Round Robin
        
        self.build_gui()

    def build_gui(self):
        # Input Frame
        input_frame = tk.Frame(self.root)
        input_frame.pack(pady=10)
        
        tk.Label(input_frame, text="Process Name").grid(row=0, column=0)
        tk.Label(input_frame, text="Arrival Time").grid(row=0, column=1)
        tk.Label(input_frame, text="CPU Cycle").grid(row=0, column=2)
        
        self.process_name = tk.Entry(input_frame, width=15)
        self.arrival_time = tk.Entry(input_frame, width=10)
        self.cpu_cycle = tk.Entry(input_frame, width=10)
        
        self.process_name.grid(row=1, column=0, padx=5)
        self.arrival_time.grid(row=1, column=1, padx=5)
        self.cpu_cycle.grid(row=1, column=2, padx=5)
        
        tk.Button(input_frame, text="Add Process", command=self.add_process).grid(row=1, column=3, padx=10)
        tk.Button(input_frame, text="Clear All", command=self.clear_all).grid(row=1, column=4, padx=10)
        
        # Algorithm Selection
        algo_frame = tk.Frame(self.root)
        algo_frame.pack(pady=10)
        
        tk.Label(algo_frame, text="Select Algorithm:").pack(side=tk.LEFT)
        algo_dropdown = ttk.Combobox(algo_frame, textvariable=self.selected_algorithm, state="readonly", 
                                     values=["FCFS", "SJN", "SRT", "Round Robin"])
        algo_dropdown.bind("<<ComboboxSelected>>", self.toggle_input_fields)
        algo_dropdown.pack(side=tk.LEFT, padx=5)
        
        tk.Label(algo_frame, text="Time Quantum (RR):").pack(side=tk.LEFT, padx=10)
        self.time_quantum_entry = tk.Entry(algo_frame, textvariable=self.time_quantum, width=5, state="disabled")
        self.time_quantum_entry.pack(side=tk.LEFT)
        
        tk.Button(algo_frame, text="Run Scheduler", command=self.run_scheduler).pack(side=tk.LEFT, padx=10)
        
        # Process List Section
        process_list_frame = tk.Frame(self.root)
        process_list_frame.pack(pady=10)
        
        tk.Label(process_list_frame, text="Inputted Processes:").pack(anchor=tk.W)
        self.process_listbox = tk.Listbox(process_list_frame, width=80, height=5)
        self.process_listbox.pack(pady=5)

        # Output Section (for the timeline)
        self.output_canvas = tk.Canvas(self.root, width=1300, height=200, bg="white")  # Increased width
        self.output_canvas.pack(pady=10)

    def add_process(self):
        if len(self.processes) >= 5:
            messagebox.showerror("Error", "Maximum of 5 processes allowed!")
            return
        try:
            name = self.process_name.get()
            arrival = int(self.arrival_time.get()) if self.arrival_time["state"] != "disabled" else 0
            cpu = int(self.cpu_cycle.get())
            if name == "" or cpu <= 0 or (self.arrival_time["state"] != "disabled" and arrival < 0):
                raise ValueError("Invalid input")
            process = {"name": name, "arrival": arrival, "cpu": cpu, "remaining": cpu}
            self.processes.append(process)
            self.process_listbox.insert(tk.END, f"{name} (Arrival: {arrival}, CPU: {cpu})")
            messagebox.showinfo("Success", f"Process {name} added successfully!")
        except ValueError:
            messagebox.showerror("Error", "Invalid input. Please try again.")
        self.process_name.delete(0, tk.END)
        self.arrival_time.delete(0, tk.END)
        self.cpu_cycle.delete(0, tk.END)

    def clear_all(self):
        # Clear all stored data
        self.processes.clear()
        self.process_listbox.delete(0, tk.END)
        self.output_canvas.delete("all")
        messagebox.showinfo("Cleared", "All processes and outputs have been cleared.")

    def toggle_input_fields(self, event):
        algorithm = self.selected_algorithm.get()
        if algorithm in ["FCFS", "SJN", "SRT"]:
            self.arrival_time.config(state="normal")
            self.cpu_cycle.config(state="normal")
            self.time_quantum_entry.config(state="disabled")
        elif algorithm == "Round Robin":
            self.arrival_time.config(state="normal")
            self.cpu_cycle.config(state="normal")
            self.time_quantum_entry.config(state="normal")

    def run_scheduler(self):
        if not self.processes:
            messagebox.showerror("Error", "No processes to schedule!")
            return
        
        algorithm = self.selected_algorithm.get()
        if algorithm == "FCFS":
            self.fcfs()
        elif algorithm == "SJN":
            self.sjn()
        elif algorithm == "SRT":
            self.srt()
        elif algorithm == "Round Robin":
            self.round_robin()

    def fcfs(self):
        self.processes.sort(key=lambda p: p["arrival"])
        timeline = []
        current_time = 0
        for process in self.processes:
            start_time = max(current_time, process["arrival"])
            end_time = start_time + process["cpu"]
            timeline.append((process["name"], start_time, end_time))
            current_time = end_time
        self.display_timeline(timeline)

    def sjn(self):
        processes = sorted(self.processes, key=lambda p: (p["arrival"], p["cpu"]))
        timeline = []
        current_time = 0
        while processes:
            available = [p for p in processes if p["arrival"] <= current_time]
            if not available:
                current_time += 1
                continue
            process = min(available, key=lambda p: p["cpu"])
            start_time = max(current_time, process["arrival"])
            end_time = start_time + process["cpu"]
            timeline.append((process["name"], start_time, end_time))
            current_time = end_time
            processes.remove(process)
        self.display_timeline(timeline)

    def srt(self):
        processes = self.processes[:]
        timeline = []
        current_time = 0
        while any(p["remaining"] > 0 for p in processes):
            available = [p for p in processes if p["arrival"] <= current_time and p["remaining"] > 0]
            if not available:
                current_time += 1
                continue
            process = min(available, key=lambda p: p["remaining"])
            process["remaining"] -= 1
            if not timeline or timeline[-1][0] != process["name"]:
                timeline.append((process["name"], current_time, current_time + 1))
            else:
                timeline[-1] = (timeline[-1][0], timeline[-1][1], current_time + 1)
            current_time += 1
        self.display_timeline(timeline)

    def round_robin(self):
        time_quantum = self.time_quantum.get()
        queue = sorted(self.processes, key=lambda p: p["arrival"])
        current_time = 0
        timeline = []
        while queue:
            process = queue.pop(0)
            if process["arrival"] > current_time:
                current_time = process["arrival"]
            execution_time = min(time_quantum, process["remaining"])
            start_time = current_time
            end_time = start_time + execution_time
            timeline.append((process["name"], start_time, end_time))
            process["remaining"] -= execution_time
            current_time = end_time
            if process["remaining"] > 0:
                queue.append(process)
        self.display_timeline(timeline)

    def display_timeline(self, timeline):
        self.output_canvas.delete("all")
        x_offset = 50
        y_offset = 50
        bar_height = 40
        bar_spacing = 20

        # Draw the timeline
        for process, start, end in timeline:
            bar_width = (end - start) * 15  # Increased scale factor for wider bars
            self.output_canvas.create_rectangle(
                x_offset + start * 15, y_offset,
                x_offset + end * 15, y_offset + bar_height,
                fill="skyblue", outline="black"
            )
            self.output_canvas.create_text(
                x_offset + (start + end) * 7.5, y_offset + bar_height / 2,
                text=process, fill="black"
            )
            # Add start and end times
            self.output_canvas.create_text(x_offset + start * 15, y_offset + bar_height + 15, text=str(start))
            self.output_canvas.create_text(x_offset + end * 15, y_offset + bar_height + 15, text=str(end))


# Run the application
if __name__ == "__main__":
    root = tk.Tk()
    app = ProcessSchedulerApp(root)
    root.mainloop()
