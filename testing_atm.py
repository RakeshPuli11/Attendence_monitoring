import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
from datetime import datetime
import mysql.connector
import cv2


class QRCodeScanner:
    def __init__(self, camera_id=0, delay=1, window_name='OpenCV QR Code'):
        self.camera_id = camera_id
        self.delay = delay
        self.window_name = window_name
        self.qcd = cv2.QRCodeDetector()
        self.qr_code_found = False

    def detect_qr_code(self):
        cap = cv2.VideoCapture(self.camera_id)
        while True:
            ret, frame = cap.read()

            if ret and not self.qr_code_found:
                ret_qr, decoded_info, points, _ = self.qcd.detectAndDecodeMulti(
                    frame)
                if ret_qr:
                    for s, p in zip(decoded_info, points):
                        if s:
                            print(s)
                            color = (0, 255, 0)
                            self.qr_code_found = True
                        else:
                            color = (0, 0, 255)
                        frame = cv2.polylines(
                            frame, [p.astype(int)], True, color, 8)

                cv2.imshow(self.window_name, frame)

            if self.qr_code_found:
                break

            if cv2.waitKey(self.delay) & 0xFF == ord('q'):
                break

        cap.release()
        cv2.destroyAllWindows()
        return decoded_info[0] if decoded_info else None


class AttendanceMonitor(QRCodeScanner):
    def __init__(self):
        super().__init__(camera_id=0, delay=1, window_name='OpenCV QR Code')
        self.root = tk.Tk()
        self.root.title("Attendance Monitoring")
        self.root.geometry("400x300")
        self.root.config(bg="grey")
        f = ("poppins", 16, "bold")

        label1 = tk.Label(self.root, text="Roll No.      :",
                          font=f, fg="white", bg="grey")
        label1.place(x=20, y=50, anchor=tk.W)

        # Entry widget for Roll No.
        self.entry1 = tk.Entry(self.root, font=f)
        self.entry1.place(x=150, y=50, anchor=tk.W)

        label2 = tk.Label(self.root, text="User Name :",
                          font=f, fg="white", bg="grey")
        label2.place(x=20, y=100, anchor=tk.W)

        # Entry widget for User Name
        self.entry2 = tk.Entry(self.root, font=f)
        self.entry2.place(x=150, y=100, anchor=tk.W)

        self.options = ["Select", "Morning", "Evening"]
        self.combobox = ttk.Combobox(self.root, values=self.options, font=f)
        self.combobox.set("Select")
        self.combobox.place(x=150, y=150, anchor=tk.W, width=100)

        # Submit button
        submit_button = tk.Button(self.root, text="Submit", font=f,
                                  command=self.submit_attendance)
        submit_button.place(x=200, y=200, anchor=tk.CENTER)
        self.valid_input = False

    def submit_attendance(self):
        roll_no = self.entry1.get()
        user_name = self.entry2.get()
        text = self.combobox.get()
        x = datetime.now()
        if text == "Morning" and roll_no != "" and user_name != "":
            # Your MySQL code to insert attendance data goes here
            my_cursor.execute("INSERT INTO mor(roll_no,user_name,today) values('%s','%s','%s')" % (
                roll_no, user_name, x))
            self.valid_input = True
        elif text == "Evening" and roll_no != "" and user_name != "":
            # Your MySQL code to insert attendance data goes here
            my_cursor.execute("INSERT INTO eve(roll_no,user_name,today) VALUES ('%s','%s','%s')" % (
                roll_no, user_name, x))
            self.valid_input = True
        else:
            messagebox.showerror("Error", "Please select a valid time.")
            self.valid_input = False
        if self.valid_input:
            decoded_text = self.detect_qr_code()
            if decoded_text and decoded_text == roll_no:
                print("QR code matches Roll No.")
                messagebox.showinfo(
                    "Success", "Attendance marked successfully.")
            else:
                print("QR code does not match Roll No.")
                messagebox.showerror(
                    "Error", "QR code does not match Roll No.")

    def run(self):
        self.root.mainloop()


if __name__ == "__main__":
    con = mysql.connector.connect(
        host="localhost", user="root", password="MySql@2157", database="attendance"
    )
    if con.is_connected():
        print("Connect ayyindhi bhaiyyah.")

    my_cursor = con.cursor()
    my_cursor.execute(
        "CREATE TABLE IF NOT EXISTS mor (roll_no VARCHAR(20) PRIMARY KEY,user_name VARCHAR(121),today DATETIME)")
    my_cursor.execute(
        "CREATE TABLE IF NOT EXISTS eve (roll_no VARCHAR(20) PRIMARY KEY,user_name VARCHAR(121),today DATETIME)")

    obj = AttendanceMonitor()
    obj.run()
