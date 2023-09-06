import tkinter as tk
import csv
import main as mk2


class Display:
    def __init__(self, root, generators):
        self._visible = None
        self._displays = [self.grid(root, generator) for generator in generators]

    def exclusive_show(self, index):
        if self._visible is not None:
            self._visible.pack_forget()
        self._visible = self._displays[index]
        self._visible.pack()

    @staticmethod
    def grid(root, grid):
        _grid = tk.Frame(root)
        for i, row in enumerate(grid):
            for j, col in enumerate(row):
                tk.Label(_grid, text=col).grid(row=i, column=j)
        return _grid


def read_csv(directory):
    with open(directory, newline='') as csvfile:
        data = []
        reader = csv.reader(csvfile)
        for row in reader:
            data.append(row)
        return data


def parse_hours(directory):
    data = read_csv(directory)
    return data


def parse_staff(directory):
    data = read_csv(directory)
    return data


def parse_jobs(directory):
    data = read_csv(directory)
    return data


def rota_generator():
    rota = mk2.Rota()
    rota.create_rota()
    return rota.display_rota()


if __name__ == "__main__":
    root = tk.Tk()
    root.configure(background="white")
    root.title("Rota")
    root.geometry("500x500")
    table_display = Display(root,
                            [parse_hours("hours.csv"), parse_staff("staff.csv"), parse_jobs("jobs.csv"),
                             rota_generator()])

    dirs = {"Staff": lambda: table_display.exclusive_show(0),
            "Jobs": lambda: table_display.exclusive_show(1),
            "Hours": lambda: table_display.exclusive_show(2)}
    call_to_action = {
        "Create Rota": lambda: table_display.exclusive_show(3),
    }

header = tk.Frame(root)
dir_frame = tk.Frame(header)
for i, _dir in enumerate(dirs):
    tk.Button(dir_frame, text=_dir, command=dirs[_dir]).grid(row=0, column=i)
dir_frame.pack(side=tk.RIGHT)

call_to_action_frame = tk.Frame(header)
for i, action in enumerate(call_to_action):
    tk.Button(call_to_action_frame, text=action, command=call_to_action[action]).grid(row=0, column=i)
call_to_action_frame.pack(side=tk.LEFT)
header.pack(fill=tk.X)
root.mainloop()
