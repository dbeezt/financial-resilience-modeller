import threading, tkinter.ttk
from functools import partial
from .Model import Model
from PIL import Image, ImageTk
from time import strftime
from tkinter import *

class GUI(Tk):
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
        self.output_plot_dirs = []
        self.output_stats_dirs = []

    def create_and_position_frames(self):
        self.prepare_input_fields()

        self.graph_frame = Frame(self, width=self.width, height=500, background="green")
        self.graph_frame.grid(row=0, column=0, columnspan=2, sticky="nsew")

        log_frame = Frame(
            self, width=int(self.width * 0.7), height=150, background="yellow"
        )
        log_frame.grid(row=1, column=0, columnspan=1, sticky="ns")
        self.compose_log_frame(log_frame)

        output_commands_frame = Frame(
            self, width=int(self.width * 0.3), height=150, background="red"
        )
        output_commands_frame.grid(
            row=1, rowspan=1, column=1, columnspan=1, sticky="ns"
        )
        self.compose_output_commands_frame(output_commands_frame)

        input_frame = Frame(
            self, width=int(self.width * 0.7), height=150, background="red"
        )
        input_frame.grid(row=2, column=0, columnspan=1, sticky="nsew")
        self.compose_input_frame(input_frame)

        model_commands_frame = Frame(
            self, width=int(self.width * 0.3), height=150, background="purple"
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
            default_general_values = [50, 2, "erdos_renyi", 5]
            default_pandemic_values = [0.05, 1, 0.1, 5]
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

    def compose_output_commands_frame(self, frame):
        frame.update()
        width, height = frame.winfo_width(), frame.winfo_height()
        button_label_font = ("TkDefaultFont", 12)

        create_separator(fr=frame, o="vertical", r=0, rs=10, c=0, cs=1, s="ns")
        create_separator(fr=frame, o="horizontal", r=0, rs=1, c=1, cs=10, s="ew")
        create_label(fr=frame, w=29, t="Outputs", a="n", r=1, rs=1, c=1, cs=3)
        create_separator(fr=frame, o="horizontal", r=2, rs=1, c=1, cs=10, s="ew")

        output_commands = [
            partial(print, "test"),
            partial(print, "test"),
            partial(print, "test"),
            partial(print, "test"),
        ]
        for command in range(0, len(output_commands)):
            create_label(
                fr=frame,
                w=10,
                t="t",
                a="center",
                fo=button_label_font,
                r=command + 3,
                rs=1,
                c=1,
                cs=1,
            )
            create_button(
                fr=frame,
                w=3,
                h=1,
                t="q",
                a="center",
                r=command + 3,
                rs=1,
                c=2,
                cs=1,
                cmd=output_commands[command],
                padx=(0, 0),
                pady=(0, 0),
            )

    def compose_model_commands_frame(self, frame):
        frame.update()
        width, height = frame.winfo_width(), frame.winfo_height()

        create_separator(fr=frame, o="vertical", r=0, rs=10, c=0, cs=1, s="ns")
        create_separator(fr=frame, o="horizontal", r=0, rs=1, c=1, cs=10, s="ew")
        create_label(fr=frame, w=29, t="Commands", a="n", r=1, rs=1, c=1, cs=3)
        create_separator(fr=frame, o="horizontal", r=2, rs=1, c=1, cs=10, s="ew")

        label_text = ["Run", "Reset"]
        button_text = ["Ctrl + ↩", "Ctrl + R"]
        keybindings = ["<Control-Return>", "<Control-r>"]

        model_commands = [
            partial(
                self.run_model_with_current_entries,
                self.field_entries,
                self.graph_frame,
            ),
            partial(
                self.reset_inputs,
                self.field_entries,
                self.field_defaults,
                self.activity_log_textbox,
            ),
        ]
        for command in range(0, len(model_commands)):
            create_label(
                fr=frame,
                w=10,
                t=label_text[command],
                a="center",
                r=command + 3,
                rs=1,
                c=1,
                cs=1,
            )
            create_button(
                fr=frame,
                w=3,
                h=1,
                t=button_text[command],
                a="center",
                r=command + 3,
                rs=1,
                c=2,
                cs=1,
                cmd=model_commands[command],
                padx=(0, 0),
                pady=(0, 0),
            )
            self.bind(keybindings[command], model_commands[command])

    def compose_log_frame(self, frame):
        frame.update()
        width, height = frame.winfo_width(), frame.winfo_height()
        create_separator(fr=frame, o="horizontal", r=0, rs=1, c=0, cs=10, s="ew")
        create_label(fr=frame, w=20, t="Activity Log", a="w", r=1, rs=1, c=0, cs=1)
        create_separator(fr=frame, o="horizontal", r=2, rs=1, c=0, cs=10, s="ew")
        self.activity_log_textbox = create_textbox(
            fr=frame, w=90, h=11, r=3, rs=6, c=0, cs=1, s="nesw"
        )
        create_separator(fr=frame, o="horizontal", r=2, rs=1, c=0, cs=10, s="ew")

    def compose_input_frame(self, frame):
        frame.update()
        width, height = frame.winfo_width(), frame.winfo_height()
        input_area_width = int(width / 2.99)

        general_input_area = Frame(
            frame, width=input_area_width, height=height, background=""
        )
        general_input_area.grid(row=0, column=0, sticky="nsew")
        pandemic_input_area = Frame(
            frame, width=input_area_width, height=height, background="pink"
        )
        pandemic_input_area.grid(row=0, column=1, sticky="nsew")
        financial_input_area = Frame(
            frame, width=input_area_width, height=height, background="brown"
        )
        financial_input_area.grid(row=0, column=2, sticky="nsew")

        area_title_font, field_title_font = ("TkDefaultFont", 12), ("TkDefaultFont", 11)
        create_separator(
            fr=general_input_area, o="horizontal", r=0, rs=1, c=0, cs=10, s="ew"
        )
        create_label(
            fr=general_input_area,
            w=20,
            t="General",
            a="center",
            fo=area_title_font,
            r=1,
            rs=1,
            c=0,
            cs=2,
        )
        create_separator(
            fr=general_input_area, o="horizontal", r=2, rs=1, c=0, cs=10, s="ew"
        )
        # create_label(f=general_input_area, w=5, t=self.field_titles[0][0], a='w', r=3, rs=1, c=0, cs=1)
        # print(general_input_area.winfo_width())
        input_title_width, input_entry_width = 6, 10
        for field in range(0, len(self.field_titles[0])):
            create_label(
                fr=general_input_area,
                w=input_title_width,
                t=self.field_titles[0][field],
                a="e",
                fo=field_title_font,
                r=field + 3,
                rs=1,
                c=0,
                cs=1,
            )
            entry = create_entry(
                fr=general_input_area,
                w=input_entry_width,
                s="normal",
                fo=field_title_font,
                d=self.field_defaults[0][field],
                r=field + 3,
                c=1,
            )
            # Record the entry object so we can access its value later using entry[0][x].get()
            self.field_entries[0].append(entry)
        self.field_entries[0][2].config(state="disabled")
        create_separator(
            fr=general_input_area, o="vertical", r=0, rs=10, c=3, cs=1, s="ns"
        )

        create_separator(
            fr=pandemic_input_area, o="horizontal", r=0, rs=1, c=0, cs=10, s="ew"
        )
        create_label(
            fr=pandemic_input_area,
            w=24,
            t="Pandemic",
            a="center",
            fo=area_title_font,
            r=1,
            rs=1,
            c=0,
            cs=2,
        )
        create_separator(
            fr=pandemic_input_area, o="horizontal", r=2, rs=1, c=0, cs=10, s="ew"
        )
        input_title_width, input_entry_width = 15, 5
        for field in range(0, len(self.field_titles[1])):
            create_label(
                fr=pandemic_input_area,
                w=input_title_width,
                t=self.field_titles[1][field],
                a="e",
                fo=field_title_font,
                r=field + 3,
                rs=1,
                c=0,
                cs=1,
            )
            entry = create_entry(
                fr=pandemic_input_area,
                w=input_entry_width,
                s="normal",
                fo=field_title_font,
                d=self.field_defaults[1][field],
                r=field + 3,
                c=1,
            )
            # Record the entry object so we can access its value later using entry[0][x].get()
            self.field_entries[1].append(entry)
        create_separator(
            fr=pandemic_input_area, o="vertical", r=0, rs=10, c=3, cs=1, s="ns"
        )

        create_separator(
            fr=financial_input_area, o="horizontal", r=0, rs=1, c=0, cs=10, s="ew"
        )
        create_label(
            fr=financial_input_area,
            w=24,
            t="Financial",
            a="center",
            fo=area_title_font,
            r=1,
            rs=1,
            c=0,
            cs=2,
        )
        create_separator(
            fr=financial_input_area, o="horizontal", r=2, rs=1, c=0, cs=10, s="ew"
        )
        input_title_width, input_entry_width = 15, 5
        for field in range(0, len(self.field_titles[2])):
            create_label(
                fr=financial_input_area,
                w=input_title_width,
                t=self.field_titles[2][field],
                a="e",
                fo=field_title_font,
                r=field + 3,
                rs=1,
                c=0,
                cs=1,
            )
            entry = create_entry(
                fr=financial_input_area,
                w=input_entry_width,
                s="normal",
                fo=field_title_font,
                d=self.field_defaults[2][field],
                r=field + 3,
                c=1,
            )
            # Record the entry object so we can access its value later using entry[0][x].get()
            self.field_entries[2].append(entry)
        create_separator(
            fr=financial_input_area, o="vertical", r=0, rs=10, c=3, cs=1, s="ns"
        )

    def run_model_with_current_entries(self, entries, graph_frame):
        # https://stackoverflow.com/questions/16626789/functools-partial-on-class-method
        # referencing these variables to get around partial/self should be possible when model class is created
        def get_current_datetime():
            return strftime("%d.%m.%y/%H:%M:%S")

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

        self.latest_datetime = get_current_datetime()
        output_dir = f"output/{self.latest_datetime}"

        #  if validate_entries(entries, defaults):
        model_inputs = get_current_entry_values(entries)
        compound_model = Model(output_dir=output_dir, options=model_inputs)
        compound_model.auto_run()
        print(compound_model.latest_run_time)
        self.latest_pandemic_model_gif = compound_model.latest_pandemic_gif
        self.latest_financial_model_gif = compound_model.latest_financial_gif

        self.load_gif_to_gui(self.graph_frame, self.latest_pandemic_model_gif)

    def load_gif_to_gui(self, gui_frame, gif_path):
        graph_image_label = ImageLabel(gui_frame)
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


def create_label(fr, w, t, a, r, rs, c, cs, fo=("TkDefaultFont", 12)):
    label = Label(fr, width=w, text=t, anchor=a, font=fo)
    label.grid(row=r, column=c, rowspan=rs, columnspan=cs)


def create_entry(fr, w, s, d, r, c, fo=("TkDefaultFont", 12)):
    entry = Entry(fr, width=w, state=s, font=fo)
    entry.insert(0, d)
    entry.grid(row=r, column=c)
    return entry


def create_button(fr, w, h, t, a, cmd, r, rs, c, cs, padx, pady, fo=("TkMenuFont", 12)):
    button = Button(fr, width=w, height=h, text=t, font=fo, anchor=a, command=cmd)
    button.grid(row=r, rowspan=rs, column=c, columnspan=cs, padx=padx, pady=pady)
    # return button


def create_textbox(fr, w, h, r, rs, c, cs, s):
    textbox = Text(fr, width=w, height=h, state="disabled")
    textbox.grid(row=r, rowspan=rs, column=c, sticky=s)
    textbox_scrollbar = Scrollbar(width=4, command=textbox.yview)
    textbox["yscrollcommand"] = textbox_scrollbar.set
    return textbox


def create_separator(fr, o, r, rs, c, cs, s):
    separator = tkinter.ttk.Separator(fr, orient=o)
    separator.grid(row=r, rowspan=rs, column=c, columnspan=cs, sticky=s)


def print_to_activity_log(activity_log, message):
    # https://stackoverflow.com/questions/14786507/how-to-change-the-color-of-certain-words-in-the-tkinter-text-widget
    # Fade existing text - TO DO
    activity_log.configure(fg="black")
    # Highlight new text - TO DO
    activity_log.insert(END, f"\n{message}")


# https://stackoverflow.com/questions/43770847/play-an-animated-gif-in-python-with-tkinter
from itertools import count


class ImageLabel(Label):
    def load(self, image):
        if isinstance(image, str):
            image = Image.open(image)
        self.loc = 0
        self.frames = []

        try:
            for i in count(1):
                self.frames.append(ImageTk.PhotoImage(image.copy()))
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
