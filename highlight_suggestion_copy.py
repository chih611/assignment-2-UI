import tkinter as tk
from tkinter import messagebox
import keyboard_design as kd
import recognizer
from template import Point, WordTemplates


class Application(tk.Frame):
    def __init__(self, window_width, window_height, master=None):
        super().__init__(master)  # Call tk.Frame.__init__(master)
        # Update the master object after tk.Frame() makes necessary changes to it
        self.master = master
        frame_bottom_height = 200
        frame_middle_height = 50
        frame_top_height = window_height - frame_bottom_height - frame_middle_height

        # the top frame is used to show input words in the text
        frame_top = tk.Frame(self.master)
        frame_top.place(x=0, y=0, width=window_width, height=frame_top_height)

        self.text = tk.Text(frame_top, bg='white', borderwidth=2,
                            relief='groove', font=('Arial', 20))
        self.text.bind('<ButtonRelease-1>', self.highlight)
        self.text.place(x=0, y=0, width=window_width, height=frame_top_height)

        # the middle frame is used to list word candidates (four labels)
        frame_middle = tk.Frame(self.master)
        frame_middle.place(x=0, y=frame_top_height,
                           width=window_width, height=frame_middle_height)

        word_candidate_num = 4
        self.label_word_candidates = []  # labels used to show word candidates
        for i in range(word_candidate_num):  # the values 0 to (word_candidate_num - 1)
            label_word = tk.Label(
                frame_middle, bg='white', borderwidth=2, relief='groove', font=15)  # anchor='w',
            label_word.place(relx=i/word_candidate_num, relwidth=1 /
                             word_candidate_num, height=frame_middle_height)
            label_word.bind("<ButtonRelease-1>", self.select_word_candidate)
            self.label_word_candidates.append(label_word)
            temp = self.label_word_candidates[0].cget("text")
            print(temp)

        # the bottom frame is used to show the keyboard
        frame_bottom = tk.Frame(self.master)
        frame_bottom.place(x=0, y=(frame_top_height + frame_middle_height), width=window_width,
                           height=frame_bottom_height)

        self.canvas_keyboard = tk.Canvas(
            frame_bottom, bg='light gray', borderwidth=2, relief='groove')
        self.canvas_keyboard.place(
            x=0, y=0, width=window_width, height=frame_bottom_height)

        self.keyboard = kd.Keyboard(self.canvas_keyboard)
        self.keyboard.keyboard_layout()

        # generate word templates
        templates = WordTemplates(self.keyboard.get_keys())

        # generate the function button

        keyboard_bottom_y = window_height - 280  # Adjust this value as needed
        self.microphone_button = tk.Button(
            master, text="Function", command=self.open_microphone_window)
        self.microphone_button.place(
            x=0, y=keyboard_bottom_y, width=80, height=30)
        # generate a recognizer
        self.word_recognizer = recognizer.Recognizer(templates.set_templates())
        self.gesture_points = []

        # mouse events on the canvas keyboard
        self.canvas_keyboard.bind(
            "<ButtonPress-1>", self.mouse_left_button_press)
        self.canvas_keyboard.bind(
            "<ButtonRelease-1>", self.mouse_left_button_release)
        self.canvas_keyboard.bind(
            "<B1-Motion>", self.mouse_move_left_button_down)

        # store x, y, segment tag
        self.cursor_move_position_list = []

        # store the tag for each segment of the drawn gesture
        self.line_tag = []

    # when users highlight and copy
    def highlight(self, event):
        try:
            global content
            content = self.master.selection_get()
            command_highligh = ['Copy', 'Cut']
            if len(content) != 0:
                for i, value in enumerate(command_highligh):
                    self.label_word_candidates[i].config(
                        text=value)
        except tk.TclError:
            content = None

    # when users select a word candidate from the four labels in the middle frame
    def select_word_candidate(self, event):
        btn = event.widget  # event.widget is the widget that called the event
        # if the button is command
        if btn.cget('text') == 'Copy':
            tk.messagebox.showinfo(title="Message box",
                                   message="Copy function executed")
        else:
            # self.label_show_text.config(text=btn.cget('text'))
            # show it to the text widget
            self.text.insert(tk.END, btn.cget('text'))
        # clear the content of all word labels
        for i in range(len(self.label_word_candidates)):
            self.label_word_candidates[i].config(text='')

    # press mouse left button
    def mouse_left_button_press(self, event):
        self.cursor_move_position_list.append(
            [event.x, event.y, 0])  # store x, y, segment tag
        self.keyboard.key_press(event.x, event.y)
        self.gesture_points.clear()

        # self.gesture_points.append(Point(event.x, event.y))

    # release mouse left button

    def mouse_left_button_release(self, event):
        previous_x = self.cursor_move_position_list[-1][0]
        previous_y = self.cursor_move_position_list[-1][1]
        line_tag = self.canvas_keyboard.create_line(
            previous_x, previous_y, event.x, event.y)
        self.cursor_move_position_list.append([event.x, event.y, line_tag])

        self.keyboard.key_release(event.x, event.y)
        result = self.word_recognizer.recognize(self.gesture_points)
        print(result)
        if len(result) > 0:
            for i in range(len(result)):
                if i < len(self.label_word_candidates):
                    self.label_word_candidates[i].config(text=result[i][1])
                else:
                    break
        else:
            key = self.keyboard.get_key_pressed()
            if key == '<--':  # remove the final character from the text
                length = len(self.text.get("1.0", 'end-1c'))
                # print(length)
                if length > 0:
                    self.text.delete("end-2c")  # remover the last character
            '''
            else:  # not the delete key ("<--")
                characters = self.label_word_candidates[0].cget("text")
                characters += self.keyboard.get_key_pressed().lower()  # convert to lowercase
                self.label_word_candidates[0].config(
                    text=characters)  # only one key was pressed
            '''

        if len(self.cursor_move_position_list) > 1:  # delete cursor trajectory
            for x in self.cursor_move_position_list[1:]:
                self.canvas_keyboard.delete(x[2])

    # users drag the mouse cursor on the keyboard while pressing the left button: drawing gestures on the keyboard

    def mouse_move_left_button_down(self, event):
        previous_x = self.cursor_move_position_list[-1][0]
        previous_y = self.cursor_move_position_list[-1][1]

        line_tag = self.canvas_keyboard.create_line(
            previous_x, previous_y, event.x, event.y)  # draw a line
        self.cursor_move_position_list.append([event.x, event.y, line_tag])

        self.keyboard.mouse_move_left_button_down(event.x, event.y)
        # store all cursor movement points
        self.gesture_points.append(Point(event.x, event.y))

#  define functions in the function button
    def open_microphone_window(self):
        self.function_window = tk.Toplevel(self.master)
        self.function_window.title("Microphone Functions")
        self.function_window.geometry("200x120")

        function_messages = {
            "cut": "Cut function executed",
            "copy": "Copy function executed",
            "save": "Save function executed",
            "highlight": "Copy function executed"
        }

        for function in function_messages:
            function_button = tk.Button(self.function_window, text=function.capitalize(),
                                        command=lambda func=function: self.execute_function(func, function_messages[func]))
            function_button.pack()

    def execute_function(self, function, message):
        # Add the code to execute the function here, e.g., cut, copy, or save.
        print(message)
        messagebox.showinfo("Function Executed", message)


if __name__ == '__main__':
    master = tk.Tk()
    window_width = 500
    window_height = 600
    # master.geometry('500x600')
    master.geometry(str(window_width) + 'x' + str(window_height))
    master.resizable(0, 0)  # can not change the size of the window
    app = Application(window_width, window_height, master=master)
    app.mainloop()  # mainloop() tells Python to run the Tkinter event loop. This method listens for events, such as button clicks or keypresses, and blocks any code that comes after it from running until the window it's called on is closed.
