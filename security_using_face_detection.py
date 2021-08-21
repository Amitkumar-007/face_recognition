import cv2
import numpy as np
import face_recognition
import os
import tkinter as tk
from datetime import datetime
import argparse
import pickle
from PIL import Image, ImageTk
import tkinter.messagebox as tmsg


##################################################################################################################
class MainWindow:
    def __init__(self, output_path="./"):
        self.vs = cv2.VideoCapture(0)
        self.output_path = output_path
        self.frame = None
        self.current_frame = None
        self.all_face_encodings = {}
        self.facenames = []
        self.faceIds = []
        self.name_for_face = None
        self.facess = []

        '''Root Window'''
        self.root = tk.Tk()
        self.root.geometry("700x500")
        self.root.title("Security using face detection")
        self.root.configure(background="#d9d9d9")
        self.root.configure(highlightbackground="#d9d9d9")
        self.root.configure(highlightcolor="black")
        self.root.wm_protocol("WM_DELETE_WINDOW", self.destructor)

        '''frame_1, frame_2'''
        self.root.columnconfigure(0, weight=2)
        self.root.columnconfigure(1, weight=8)
        self.frame_1 = tk.Frame(self.root)
        self.frame_1.grid(column=0, sticky="nsew")
        self.frame_1.place(relheight=1, relwidth=1, relx=0, rely=0)
        self.frame_2 = tk.Frame(self.root)
        self.frame_2.grid(column=1, sticky="nsew")
        self.frame_2.place(relheight=1, relwidth=1, relx=0.2, rely=0)

        self.panel = tk.Label(self.frame_2)
        self.panel.pack(padx=10, pady=10, fill=tk.BOTH)

        self.load_encoding()

        ''' new_face register, authenticate and remove buttons'''
        new_face_btn = tk.Button(self.frame_1, text="Ragister New Face", command=lambda: self.registering())
        new_face_btn.grid(sticky='nsew', pady=20)
        authenticate_btn = tk.Button(self.frame_1, text="Authenticate Face", command=self.authentication)
        authenticate_btn.grid(sticky='nsew', pady=20)
        remove_btn = tk.Button(self.frame_1, text="Remove Face", command=lambda: self.remove_face())
        remove_btn.grid(sticky='nsew', pady=20)

        ''' start a self.video_loop that constantly read video frame'''
        self.video_loop()


    def findEncodings(self, imag):
        try:
            imag = cv2.cvtColor(imag, cv2.COLOR_BGR2RGB)
            faces = face_recognition.face_locations(imag)
            encode = face_recognition.face_encodings(imag, faces)[0]
            return encode
        except:
            return []

    def load_encoding(self):
        try:  # reading face encode(dictionary) key:name of person ,value: face encoding file
            with open('dataset_faces.dat', 'rb') as f:
                self.all_face_encodings = pickle.load(f)
                f.close()
        except:
            self.all_face_encodings = {}
        if len(self.all_face_encodings) == 0:
            # all_face_encodings = {}
            self.facenames = []
            self.faceIds = []
        else:
            self.facenames = list(self.all_face_encodings.keys())
            self.faceIds = list(self.all_face_encodings.values())

    def video_loop(self):
        """ Get frame from the video stream and show it in Tkinter """
        ok, self.frame = self.vs.read()  # read frame from video stream
        if ok:  # frame captured without any errors
            self.facess = face_recognition.face_locations(self.frame)
            for i in range(len(self.facess)):
                self.img = cv2.rectangle(self.frame, (self.facess[i][3], self.facess[i][0]),
                                         (self.facess[i][1], self.facess[i][2]), (0, 255, 0), 2)

            cv2image = cv2.cvtColor(self.frame, cv2.COLOR_BGR2RGB)
            self.current_frame = Image.fromarray(cv2image)
            imgtk = ImageTk.PhotoImage(image=self.current_frame)
            self.panel.imgtk = imgtk
            self.panel.config(image=imgtk)
        self.root.after(30, self.video_loop)

    def registering(self):
        def validate_name():
            if self.name_for_face.get() in self.facenames:
                tmsg.showinfo("Error", self.name_for_face.get() + " already in use try different name!!!")
            else:
                name_window.destroy()
                enc = self.findEncodings(self.frame)
                if len(enc) == 0:
                    tmsg.showinfo("Message", "No face found....failed...")
                    return
                self.all_face_encodings[self.name_for_face.get()] = enc
                with open('dataset_faces.dat', 'wb') as f:
                    pickle.dump(self.all_face_encodings, f)
                    tmsg.showinfo("Message", self.name_for_face.get() + " Registered")
                self.load_encoding()

        def cancel_face_name_input():
            name_window.destroy()

        faces = self.facess
        if len(faces) != 1:
            tmsg.showinfo("message", "Face not Detected Try again!!!")
            return False
        else:
            # name input window
            name_window = tk.Toplevel()
            name_window.geometry('300x150')
            name_window.title('Face Label')

            face_label = tk.Label(name_window, text="Name", relief=tk.GROOVE).grid(row=0, column=0, padx=15, pady=15)
            self.name_for_face = tk.StringVar()
            face_label_entry = tk.Entry(name_window, textvariable=self.name_for_face).grid(row=0, column=1, pady=15)

            ok_btn = tk.Button(name_window, text="Continue", command=validate_name).grid(row=1, column=0)
            cancel_btn = tk.Button(name_window, text="Cancel", command=cancel_face_name_input).grid(row=1, column=1)

    def marktime(self, name):
        with open('logindetails.csv', 'a+') as f:
            myDataList = f.readlines()
            nameList = []
            for line in myDataList:
                entry = line.split(',')
                nameList.append(entry[0])
            if name not in nameList:
                now = datetime.now()
                dtString = now.strftime('%H:%M:%S')
                f.writelines(f'\n{name},{dtString}')

    def authentication(self):
        if len(self.facess) != 1:
            tmsg.showinfo("message", " Face Not Detected Try Again!!!")
        self.current_frame  = cv2.cvtColor(self.frame, cv2.COLOR_BGR2RGB)
        facesCurFrame = face_recognition.face_locations(self.current_frame)
        if len(facesCurFrame) != 0:
            encodesCurFrame = face_recognition.face_encodings(self.current_frame, facesCurFrame)
            for encodeFace, faceLoc in zip(encodesCurFrame, facesCurFrame):
                matches = face_recognition.compare_faces(self.faceIds, encodeFace)
                self.faceDis = face_recognition.face_distance(self.faceIds, encodeFace)
                if len(self.faceDis) != 0:
                    matchIndex = np.argmin(self.faceDis)
                    if matches[matchIndex]:
                        name = self.facenames[matchIndex]
                        self.marktime(name)
                        tmsg.showinfo("message", name + " Authenticated")
                        return
                else:
                    print("hello")
                    tmsg.showinfo("message", "Unregistered Face")
                    name = "unauthorized"
                    self.marktime(name)

    def remove_face(self):

        def remove():
            if self.name_for_face.get() not in self.facenames:
                tmsg.showinfo("Error", "Not In database Try different name!!!")

            else:
                remove_window.destroy()
                try:
                    self.all_face_encodings.pop(self.name_for_face.get())
                    with open('dataset_faces.dat', 'wb') as f:
                        pickle.dump(self.all_face_encodings, f)
                        tmsg.showinfo("message", "Face deleted")
                    self.load_encoding()

                except FileExistsError:
                    tmsg.showinfo("Error", "some error occured Try again!!!")

        def cancel_face_name_input():
            remove_window.destroy()

        def set_face_name(event):
            widget = event.widget
            selection = widget.curselection()
            value = widget.get(selection[0])
            self.name_for_face.set(value)

        remove_window = tk.Toplevel()
        remove_window.geometry('300x400')
        remove_window.title('Delete Face')

        remove_window.rowconfigure(0, weight=3)
        remove_window.rowconfigure(1, weight=7)
        remove_window_frame1 = tk.Frame(remove_window)
        remove_window_frame2 = tk.Frame(remove_window)

        face_label = tk.Label(remove_window_frame1, text="Name", relief=tk.GROOVE)
        face_label.grid(sticky='ew', row=0, column=0, padx=30, pady=20)
        self.name_for_face = tk.StringVar()
        face_label_entry = tk.Entry(remove_window_frame1, textvariable=self.name_for_face, width=15)
        face_label_entry.grid(sticky='ew', row=0, column=2)

        ok_btn = tk.Button(remove_window_frame1, text="Continue", command=remove)
        ok_btn.grid(sticky='ew', padx=30, row=1, column=0)
        cancel_btn = tk.Button(remove_window_frame1, text="Cancel", command=cancel_face_name_input)
        cancel_btn.grid(sticky='ew', row=1, column=2, columnspan=2)
        remove_window_frame1.grid(row=0, sticky="nsew")
        remove_window_frame1.place(relheight=0.30, relwidth=1, relx=0, rely=0)

        tk.Label(remove_window_frame2, text="Registered Faces").pack()
        sb = tk.Scrollbar(remove_window_frame2)
        lb = tk.Listbox(remove_window_frame2, font=('calibre', 10), yscrollcommand=sb.set, height=15, width=10)
        for i in self.facenames:
            lb.insert(tk.END, i)
        lb.bind("<<ListboxSelect>>", set_face_name)
        sb.configure(command=lb.yview, orient=tk.VERTICAL)
        sb.pack(side=tk.RIGHT, fill=tk.Y)
        lb.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        remove_window_frame2.grid(row=1, sticky="nsew")
        remove_window_frame2.place(relheight=0.70, relwidth=1, relx=0, rely=0.30)

    def destructor(self):
        """ Destroy the root object and release all resources """
        print("[INFO] closing...")
        self.root.destroy()
        self.vs.release()  # release web camera
        cv2.destroyAllWindows()  # it is not mandatory in this application


# construct the argument parse and parse the arguments
ap = argparse.ArgumentParser()
ap.add_argument("-o", "--output", default="./",
                help="path to output directory to store snapshots (default: current folder")
args = vars(ap.parse_args())

# start the app
print("[INFO] starting...")
pba = MainWindow(args["output"])
pba.root.mainloop()

######################################################################################################################
