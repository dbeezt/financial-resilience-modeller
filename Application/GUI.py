import functools
import itertools
import glob
import pathlib
import PIL.Image
import PIL.ImageTk
import tkinter as tk
import tkinter.ttk
import threading
import time
from Model import Model


class GUI(tk.Tk):
    def __init__(self):
        super().__init__()
        self.create_window()
        self.create_and_position_frames()
        self.output_path = "output"

    def create_window(self):
        self.title("Financial Resilience Modeller")
        self.width, self.height = 800, 800
        self.geometry(f"{self.width}x{self.height}")
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)
        self.resizable(False, False)
        self.output_dir = "output"
        self.latest_datetime = time.strftime("%d.%m.%y/%H:%M:%S")
        self.latest_pandemic_model_gif = ""
        self.latest_financial_model_gif = ""
        self.output_plot_dirs = []
        self.output_stats_dirs = []

    def create_and_position_frames(self):
        self.prepare_input_fields()

        self.graph_frame = tk.Frame(
            self, width=self.width, height=500, background="#F0F0F0"
        )
        self.graph_frame.grid(row=0, column=0, columnspan=2, sticky="nsew")

        log_frame = tk.Frame(
            self, width=int(self.width * 0.7), height=150, background="#F0F0F0"
        )
        log_frame.grid(row=1, column=0, columnspan=1, sticky="ns")
        self.compose_log_frame(log_frame)

        output_commands_frame = tk.Frame(
            self, width=int(self.width * 0.3), height=150, background="#F0F0F0"
        )
        output_commands_frame.grid(
            row=1, rowspan=1, column=1, columnspan=1, sticky="ns"
        )
        self.compose_output_commands_frame(output_commands_frame)

        input_frame = tk.Frame(
            self, width=int(self.width * 0.7), height=150, background="#F0F0F0"
        )
        input_frame.grid(row=2, column=0, columnspan=1, sticky="nsew")
        self.compose_input_frame(input_frame)

        model_commands_frame = tk.Frame(
            self, width=int(self.width * 0.3), height=150, background="#F0F0F0"
        )
        model_commands_frame.grid(row=2, rowspan=1, column=1, columnspan=1, sticky="ns")
        self.compose_model_commands_frame(model_commands_frame)

    def prepare_input_fields(self):
        def compose_entries():
            self.field_entries = [[], [], []]
            self.entry_state = "normal"
            self.invalid_entry_foreground, self.invalid_entry_background = (
                "red",
                "yellow",
            )

        def compose_fields():
            general_fields = ["Agents:", "Cycles:", "Graph:", "Seed:"]
            pandemic_fields = [
                "Geographic Cohesion:",
                "Iterations per Cycle:",
                "Ease of Transmisson:",
                "Time to Recover:",
            ]
            financial_fields = [
                "Financial Cohesion:",
                "Iterations per Cycle:",
                "Lockdown Severity:",
                "Loan Threshold:",
            ]
            self.field_titles = [general_fields, pandemic_fields, financial_fields]

        def compose_defaults():
            default_general_values = [50, 5, "erdos_renyi", 5]
            default_pandemic_values = [0.05, 1, 0.5, 5]
            default_financial_values = [0.05, 1, 0.1, 5.0]
            self.field_defaults = [
                default_general_values,
                default_pandemic_values,
                default_financial_values,
            ]

        def compose_expected_input_value_types():
            self.field_data_types = [[], [], []]
            for set_of_defaults in range(0, len(self.field_defaults)):
                for default_value in range(
                    0, len(self.field_defaults[set_of_defaults])
                ):
                    self.field_data_types[set_of_defaults].append(
                        type(self.field_defaults[set_of_defaults][default_value])
                    )

        compose_entries()
        compose_fields()
        compose_defaults()
        compose_expected_input_value_types()

    def find_latest_gif(self, model):
        output_dir = f"{self.output_dir}/{self.latest_datetime}"
        gif_file = f"{model}.gif"
        latest_gif = pathlib.Path(output_dir).rglob(gif_file)

    def choose_output_directory(self):
        self.output_dir = tk.filedialog.askdirectory()

    def print_dir(self):
        print(self.output_dir)

    def compose_output_commands_frame(self, frame):
        create_separator(
            frame=frame,
            orientation="vertical",
            row=0,
            rowspan=10,
            column=0,
            columnspan=1,
            sticky="ns",
        )
        create_separator(
            frame=frame,
            orientation="horizontal",
            row=0,
            rowspan=1,
            column=1,
            columnspan=10,
            sticky="ew",
        )
        create_label(
            frame=frame,
            width=29,
            text="Outputs",
            anchor="n",
            row=1,
            rowspan=1,
            column=1,
            columnspan=3,
        )
        create_separator(
            frame=frame,
            orientation="horizontal",
            row=2,
            rowspan=1,
            column=1,
            columnspan=10,
            sticky="ew",
        )

        output_button_text = ["Switch Shown Graph", "Set Output Location"]
        output_button_commands = [
            functools.partial(self.load_gif_to_gui, self.graph_frame),
            functools.partial(self.choose_output_directory),
        ]
        for button in range(0, len(output_button_text)):
            create_button(
                frame=frame,
                width=22,
                height=1,
                text=output_button_text[button],
                anchor="center",
                row=button + 3,
                rowspan=1,
                column=1,
                columnspan=4,
                command=output_button_commands[button],
                padx=(10, 0),
                pady=(4, 0),
            )

        # output_settings_button_text

        # def compose_pandemic_output_frame(self, frame, button_text):
        #     pandemic_outputs = Frame(
        #         frame, width=int(width/2), height=150, background="green"
        #     )
        #     pandemic_outputs.grid(
        #         row=2, rowspan=1, column=1, columnspan=1, sticky="ns"
        #     )
        #     pandemic_outputs.pack_propagate(0)
        #     create_separator(frame=pandemic_outputs, orientation="horizontal", row=0, rowspan=1, column=1, columnspan=10, sticky="ew")
        #     create_label(frame=pandemic_outputs, width=14, text="Pandemic", anchor="n", row=1, rowspan=1, column=1, columnspan=3)
        #     create_separator(frame=pandemic_outputs, orientation="horizontal", row=2, rowspan=1, column=1, columnspan=10, sticky="ew")

        #     # current_model_output_dir = f"output/{self.latest_datetime}"
        #     commands = [
        #         functools.partial(self.load_gif_to_gui, self.graph_frame),
        #         functools.partial(self.choose_output_directory),
        #         functools.partial(self.print_dir),
        #         functools.partial(print, 'test')
        #     ]

        #     for button in range(0, len(button_text)):
        #         create_button(frame=pandemic_outputs, width=8, height=1, text=button_text[button], anchor='center', row=button+3, rowspan=1, column=1, columnspan=1, command=commands[button], padx=(10,0), pady=(4,0))

        # def compose_financial_output_frame(self, frame):
        #     financial_outputs = Frame(
        #         frame, width=int(width/2), height=150, background="red"
        #     )
        #     financial_outputs.grid(
        #         row=2, rowspan=1, column=2, columnspan=1, sticky="ns"
        #     )
        #     create_separator(frame=financial_outputs, orientation="vertical", row=0, rowspan=10, column=0, columnspan=1, sticky="ns")
        #     create_separator(frame=financial_outputs, orientation="horizontal", row=0, rowspan=1, column=1, columnspan=10, sticky="ew")
        #     create_label(frame=financial_outputs, width=14, text="Financial", anchor="n", row=1, rowspan=1, column=1, columnspan=3)
        #     create_separator(frame=financial_outputs, orientation="horizontal", row=2, rowspan=1, column=1, columnspan=10, sticky="ew")

        # compose_pandemic_output_frame(self, frame, button_text)
        # compose_financial_output_frame(self, frame)

    def compose_model_commands_frame(self, frame):
        create_separator(
            frame=frame,
            orientation="vertical",
            row=0,
            rowspan=10,
            column=0,
            columnspan=1,
            sticky="ns",
        )
        create_separator(
            frame=frame,
            orientation="horizontal",
            row=0,
            rowspan=1,
            column=1,
            columnspan=10,
            sticky="ew",
        )
        create_label(
            frame=frame,
            width=29,
            text="Commands",
            anchor="n",
            row=1,
            rowspan=1,
            column=1,
            columnspan=3,
        )
        create_separator(
            frame=frame,
            orientation="horizontal",
            row=2,
            rowspan=1,
            column=1,
            columnspan=10,
            sticky="ew",
        )

        label_text = ["Run", "Reset"]
        button_text = ["Ctrl + ↩", "Ctrl + R"]
        keybindings = ["<Control-Return>", "<Control-r>"]

        model_commands = [
            functools.partial(
                self.run_model_with_current_entries,
                self.field_entries,
                self.graph_frame,
            ),
            functools.partial(
                self.reset_inputs,
                self.field_entries,
                self.field_defaults,
                self.activity_log_textbox,
            ),
        ]
        for command in range(0, len(model_commands)):
            create_label(
                frame=frame,
                width=10,
                text=label_text[command],
                anchor="w",
                font=("TkDefaultFont", 12),
                row=command + 3,
                rowspan=1,
                column=1,
                columnspan=1,
            )
            create_button(
                frame=frame,
                width=10,
                height=1,
                text=button_text[command],
                anchor="center",
                row=command + 3,
                rowspan=1,
                column=2,
                columnspan=1,
                command=model_commands[command],
                padx=(0, 0),
                pady=(0, 0),
            )
            self.bind(keybindings[command], model_commands[command])

    def compose_log_frame(self, frame):
        frame.update()
        width, height = frame.winfo_width(), frame.winfo_height()
        create_separator(
            frame=frame,
            orientation="horizontal",
            row=0,
            rowspan=1,
            column=0,
            columnspan=10,
            sticky="ew",
        )
        create_label(
            frame=frame,
            width=20,
            text="Activity Log",
            anchor="w",
            row=1,
            rowspan=1,
            column=0,
            columnspan=1,
        )
        create_separator(
            frame=frame,
            orientation="horizontal",
            row=2,
            rowspan=1,
            column=0,
            columnspan=10,
            sticky="ew",
        )
        self.activity_log_textbox = create_textbox(
            frame=frame,
            width=79,
            height=11,
            row=3,
            rowspan=6,
            column=0,
            columnspan=1,
            sticky="nesw",
        )
        create_separator(
            frame=frame,
            orientation="vertical",
            row=0,
            rowspan=10,
            column=10,
            columnspan=1,
            sticky="ns",
        )
        create_separator(
            frame=frame,
            orientation="horizontal",
            row=2,
            rowspan=1,
            column=0,
            columnspan=10,
            sticky="ew",
        )

    def compose_input_frame(self, frame):
        frame.update()
        width, height = frame.winfo_width(), frame.winfo_height()
        input_area_width = int(width / 2.99)

        general_input_area = tk.Frame(
            frame, width=input_area_width, height=height, background="#F0F0F0"
        )
        general_input_area.grid(row=0, column=0, sticky="nsew")
        pandemic_input_area = tk.Frame(
            frame, width=input_area_width, height=height, background="#F0F0F0"
        )
        pandemic_input_area.grid(row=0, column=1, sticky="nsew")
        financial_input_area = tk.Frame(
            frame, width=input_area_width, height=height, background="#F0F0F0"
        )
        financial_input_area.grid(row=0, column=2, sticky="nsew")

        area_title_font, field_title_font = ("TkDefaultFont", 12), ("TkDefaultFont", 11)
        create_separator(
            frame=general_input_area,
            orientation="horizontal",
            row=0,
            rowspan=1,
            column=0,
            columnspan=10,
            sticky="ew",
        )
        create_label(
            frame=general_input_area,
            width=20,
            text="General",
            anchor="center",
            font=area_title_font,
            row=1,
            rowspan=1,
            column=0,
            columnspan=2,
        )
        create_separator(
            frame=general_input_area,
            orientation="horizontal",
            row=2,
            rowspan=1,
            column=0,
            columnspan=10,
            sticky="ew",
        )
        input_title_width, input_entry_width = 6, 10
        for field in range(0, len(self.field_titles[0])):
            create_label(
                frame=general_input_area,
                width=input_title_width,
                text=self.field_titles[0][field],
                anchor="e",
                font=field_title_font,
                row=field + 3,
                rowspan=1,
                column=0,
                columnspan=1,
            )
            entry = create_entry(
                frame=general_input_area,
                width=input_entry_width,
                state="normal",
                font=field_title_font,
                default=self.field_defaults[0][field],
                row=field + 3,
                column=1,
            )
            # Record the entry object so we can access its value later using entry[0][x].get()
            self.field_entries[0].append(entry)
        self.field_entries[0][2].config(state="disabled")
        create_separator(
            frame=general_input_area,
            orientation="vertical",
            row=0,
            rowspan=10,
            column=3,
            columnspan=1,
            sticky="ns",
        )

        create_separator(
            frame=pandemic_input_area,
            orientation="horizontal",
            row=0,
            rowspan=1,
            column=0,
            columnspan=10,
            sticky="ew",
        )
        create_label(
            frame=pandemic_input_area,
            width=24,
            text="Pandemic",
            anchor="center",
            font=area_title_font,
            row=1,
            rowspan=1,
            column=0,
            columnspan=2,
        )
        create_separator(
            frame=pandemic_input_area,
            orientation="horizontal",
            row=2,
            rowspan=1,
            column=0,
            columnspan=10,
            sticky="ew",
        )
        input_title_width, input_entry_width = 16, 5
        for field in range(0, len(self.field_titles[1])):
            create_label(
                frame=pandemic_input_area,
                width=input_title_width,
                text=self.field_titles[1][field],
                anchor="e",
                font=field_title_font,
                row=field + 3,
                rowspan=1,
                column=0,
                columnspan=1,
            )
            entry = create_entry(
                frame=pandemic_input_area,
                width=input_entry_width,
                state="normal",
                font=field_title_font,
                default=self.field_defaults[1][field],
                row=field + 3,
                column=1,
            )
            # Record the entry object so we can access its value later using entry[0][x].get()
            self.field_entries[1].append(entry)
        create_separator(
            frame=pandemic_input_area,
            orientation="vertical",
            row=0,
            rowspan=10,
            column=3,
            columnspan=1,
            sticky="ns",
        )

        create_separator(
            frame=financial_input_area,
            orientation="horizontal",
            row=0,
            rowspan=1,
            column=0,
            columnspan=10,
            sticky="ew",
        )
        create_label(
            frame=financial_input_area,
            width=24,
            text="Financial",
            anchor="center",
            font=area_title_font,
            row=1,
            rowspan=1,
            column=0,
            columnspan=2,
        )
        create_separator(
            frame=financial_input_area,
            orientation="horizontal",
            row=2,
            rowspan=1,
            column=0,
            columnspan=10,
            sticky="ew",
        )
        input_title_width, input_entry_width = 14, 5
        for field in range(0, len(self.field_titles[2])):
            create_label(
                frame=financial_input_area,
                width=input_title_width,
                text=self.field_titles[2][field],
                anchor="e",
                font=field_title_font,
                row=field + 3,
                rowspan=1,
                column=0,
                columnspan=1,
            )
            entry = create_entry(
                frame=financial_input_area,
                width=input_entry_width,
                state="normal",
                font=field_title_font,
                default=self.field_defaults[2][field],
                row=field + 3,
                column=1,
            )
            # Record the entry object so we can access its value later using entry[0][x].get()
            self.field_entries[2].append(entry)
        create_separator(
            frame=financial_input_area,
            orientation="vertical",
            row=0,
            rowspan=10,
            column=3,
            columnspan=1,
            sticky="ns",
        )

    def run_model_with_current_entries(self, entries, graph_frame):
        # https://stackoverflow.com/questions/16626789/functools-partial-on-class-method
        # referencing these variables to get around partial/self should be possible when model class is created

        def get_current_entry_values(entries):
            model_inputs = [[], [], []]
            for list_of_entries in range(0, len(entries)):
                for entry in range(0, len(entries[list_of_entries])):
                    model_inputs[list_of_entries].append(
                        entries[list_of_entries][entry].get()
                    )
            return model_inputs

        def validate_input_values():
            pass

        self.latest_datetime = time.strftime("%d.%m.%y/%H:%M:%S")
        output_dir = f"{self.output_dir}/{self.latest_datetime}"

        #  if validate_entries(entries, defaults):
        model_inputs = get_current_entry_values(entries)
        compound_model = Model(
            output_dir=output_dir, options=model_inputs, log=self.activity_log_textbox
        )
        self.activity_log_textbox.insert("end", "Processing\n")
        thread = threading.Thread(target=compound_model.auto_run())
        while thread.is_alive():
            print("test")
            self.activity_log_textbox.insert("end", ".")
            self.update()
        self.latest_pandemic_model_gif = compound_model.latest_pandemic_gif
        self.latest_financial_model_gif = compound_model.latest_financial_gif
        self.gif_to_load = "pandemic"
        self.load_gif_to_gui(gui_frame=self.graph_frame)

    def load_gif_to_gui(self, gui_frame):
        # def find_latest_gif(self, model):
        #     latest_gif = glob.glob(f"{self.output_dir}/{self.latest_datetime}/*{model}.gif", recursive=True)[0]
        #     return latest_gif
        if self.gif_to_load == "pandemic":
            gif_path = self.latest_pandemic_model_gif
            self.gif_to_load = "financial"
        elif self.gif_to_load == "financial":
            gif_path = self.latest_financial_model_gif
            self.gif_to_load = "pandemic"

        graph_image_label = GIF(gui_frame)
        graph_image_label.load(gif_path)
        graph_image_label.grid(row=0, column=0, sticky="nesw")
        return graph_image_label

    def reset_inputs(self, entries, defaults, activity_log):
        def reset_entries_to_defaults(entries, defaults):
            for list_of_entries in range(0, len(entries)):
                for entry in range(0, len(entries[list_of_entries])):
                    entries[list_of_entries][entry].delete(0, "end")
                    entries[list_of_entries][entry].insert(
                        0, defaults[list_of_entries][entry]
                    )

        def reset_activity_log_to_empty(activity_log):
            activity_log.delete(1.0, "end")

        reset_entries_to_defaults(entries, defaults)
        reset_activity_log_to_empty(activity_log)


def create_label(
    frame,
    width,
    text,
    anchor,
    row,
    rowspan,
    column,
    columnspan,
    font=("TkDefaultFont", 12),
):
    label = tk.Label(
        frame, width=width, text=text, anchor=anchor, background="#F0F0F0", font=font
    )
    label.grid(row=row, column=column, rowspan=rowspan, columnspan=columnspan)


def create_entry(frame, width, state, default, row, column, font=("TkDefaultFont", 12)):
    entry = tk.Entry(frame, width=width, state=state, font=font)
    entry.insert(0, default)
    entry.grid(row=row, column=column)
    return entry


def create_button(
    frame,
    width,
    height,
    text,
    anchor,
    command,
    row,
    rowspan,
    column,
    columnspan,
    padx,
    pady,
    font=("TkMenuFont", 12),
):
    button = tk.Button(
        frame,
        width=width,
        height=height,
        text=text,
        font=font,
        anchor=anchor,
        background="#F0F0F0",
        command=command,
    )
    button.grid(
        row=row,
        rowspan=rowspan,
        column=column,
        columnspan=columnspan,
        padx=padx,
        pady=pady,
    )
    # return button


def create_textbox(frame, width, height, row, rowspan, column, columnspan, sticky):
    textbox = tk.Text(frame, width=width, height=height, state="disabled")
    textbox.grid(
        row=row, rowspan=rowspan, column=column, columnspan=columnspan, sticky=sticky
    )
    textbox_scrollbar = tk.Scrollbar(width=4, command=textbox.yview)
    textbox["yscrollcommand"] = textbox_scrollbar.set

    return textbox


def create_listbox(frame, width, height, row, rowspan, column, sticky):
    listbox = tk.Listbox(frame, width=width, height=height, state="disabled")
    listbox.grid(row=row, rowspan=rowspan, column=column, sticky=sticky)
    listbox_scrollbar = tk.Scrollbar(width=4, command=listbox.yview)
    listbox["yscrollcommand"] = listbox_scrollbar.set
    return listbox


def create_separator(frame, orientation, row, rowspan, column, columnspan, sticky):
    separator = tk.ttk.Separator(frame, orient=orientation)
    separator.grid(
        row=row, rowspan=rowspan, column=column, columnspan=columnspan, sticky=sticky
    )


def print_to_activity_log(activity_log, message):
    # https://stackoverflow.com/questions/14786507/how-to-change-the-color-of-certain-words-in-the-tkinter-text-widget
    # Fade existing text - TO DO
    activity_log.configure(fg="black")
    # Highlight new text - TO DO
    activity_log.insert("end", f"{message}\n")


# Source: https://stackoverflow.com/questions/43770847/play-an-animated-gif-in-python-with-tkinter
class GIF(tk.Label):
    def load(self, image):
        # image =
        print(image)
        if isinstance(image, str):
            image = PIL.Image.open(image)
        self.loc = 0
        self.frames = []

        try:
            for i in itertools.count(1):
                self.frames.append(PIL.ImageTk.PhotoImage(image.copy()))
                image.seek(i)
        except EOFError:
            pass

        try:
            self.delay = image.info["duration"]
        except:
            self.delay = 400

        if len(self.frames) == 1:
            self.config(image=self.frames[0])
        else:
            self.next_frame()

    def unload(self):
        self.config(image="")
        self.frames = None

    def next_frame(self):
        if self.frames:
            self.loc += 1
            self.loc %= len(self.frames)
            self.config(image=self.frames[self.loc])
            self.after(self.delay, self.next_frame)


if __name__ == "__main__":
    GUI().mainloop()
