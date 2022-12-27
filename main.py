import os
import sys
from datetime import datetime
from Utils import utils
from Utils import vad

import tkinter as tk

import threading
from threading import Event
from collections import Counter

#For disabling terminal logs
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'


class App(tk.Tk):
    def __init__(self):
        super().__init__()

        #Configure the root window
        self.title('Data Annotator')
        #self.attributes('-fullscreen',True)
        self.geometry('1500x1000')
        self.configure(bg='black')


        self.columnconfigure(0, weight=1)
        self.columnconfigure(1, weight=1)
        self.columnconfigure(2, weight=1)

        self.rowconfigure(0, weight=1)
        self.rowconfigure(1, weight=1)
        self.rowconfigure(2, weight=1)

        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        screen_height = (screen_height/2)

        self.text_label = tk.Text(wrap="word", highlightbackground="black", highlightthickness=5, bg = "black", fg = "white", font=("Ariel", 24), height=10, width=50)
        self.text_label.tag_configure('center', justify='center')

        self.error_label = tk.Label(highlightbackground="black", highlightthickness=5, bg = "black", fg = "white", font=("Ariel", 12))

        self.text_label.grid(row=0,column=1)

        self.repeat_button = tk.Button(text="Repeat", command = self.repeat)
        self.invalid_button = tk.Button(text="Invalid", command = self.invalid)
        self.next_button = tk.Button(text="Next", command = self.next)
        self.repeat_button.grid(row=1,column=0)
        self.invalid_button.grid(row=1,column=1)
        self.next_button.grid(row=1,column=2)

        self.repeat_event = Event()
        self.invalid_event = Event()
        self.next_event = Event()

        self.start_proc()

    def repeat(self):
        self.repeat_event.set()

    def invalid(self):
        self.invalid_event.set()

    def next(self):
        self.next_event.set()


    def check_speech(self, event):
        while True:
            if event.is_set():
                self.text_label["highlightbackground"] = "red"
            else:
                self.text_label["highlightbackground"] = "black"


    def start_read(self, event):
        main_dir = os.getcwd()

        #Start the course
        #Make data collection path for language
        output_folder = os.path.join(main_dir, "Collection", datetime.now().strftime("%Y-%m-%d_%H-%M-%S"))
        text_file = os.path.join(main_dir, "Data", "input.txt")
        os.makedirs(output_folder, exist_ok=True)

        self.vad_audio = vad.listen_audio(event, output_folder)

        input_data = open(text_file, "r")
        file_data = input_data.readlines()
        input_data.close()

        items_counter = Counter({'all': 0, 'failed': 0, 'invalid_label': 0, 'too_short': 0, 'too_long': 0, 'imported_time': 0, 'total_time': 0})

        j = 0

        #for line in file_data:
        while j < len(file_data):
            #Remove spaces from both side(begining and end) of string and return
            line = file_data[j].strip()
            #Load user speech
            file_name = str()
            self.text_label.delete("1.0", tk.END)
            self.text_label.insert(tk.END, line, 'center')

            self.next_event.clear()
            self.next_button["state"] = "disabled"

            self.invalid_event.clear()
            self.invalid_button["state"] = "disabled"

            self.repeat_event.clear()
            self.repeat_button["state"] = "disabled"

            file_name = next(self.vad_audio)

            self.next_event.clear()
            self.next_button["state"] = "normal"

            self.invalid_event.clear()
            self.invalid_button["state"] = "normal"

            self.repeat_event.clear()
            self.repeat_button["state"] = "normal"

            #Check for audio length and update csv
            while True:
                if self.next_event.is_set():
                    self.next_event.clear()

                    is_valid, file_size = utils.check_audio(line, file_name, items_counter)
                    if is_valid:
                        #Update collected data in csv
                        utils.write_to_csv(file_name, file_size, line, output_folder)
                    else:
                        #print("--->|File is not valid.|<---")
                        os.remove(file_name)

                    j+=1
                    break

                if self.invalid_event.is_set():
                    self.invalid_event.clear()
                    #print("--->|File is not valid.|<---")
                    os.remove(file_name)
                    j+=1
                    break

                if self.repeat_event.is_set():
                    self.repeat_event.clear()
                    os.remove(file_name)
                    break

        csv_file_path = os.path.join(output_folder, "validated.csv")
        utils.generate_alphabet(csv_file_path, output_folder)

        self.text_label.delete("1.0", tk.END)
        self.text_label.insert(tk.END, utils.print_import_report(items_counter, 15), 'center')

    def start_proc(self):

        self.anim_event = Event()
        self.language_event = Event()

        self.anim_proc = threading.Thread(target=self.start_read, args = (self.anim_event, ))
        #Daemon threads are those threads which are killed when the main program exits
        self.anim_proc.daemon = True
        self.anim_proc.start()

        self.vad_proc = threading.Thread(target=self.check_speech, args = (self.anim_event, ))
        #Daemon threads are those threads which are killed when the main program exits
        self.vad_proc.daemon = True
        self.vad_proc.start()

if __name__ == "__main__":
    app = App()
    app.mainloop()
