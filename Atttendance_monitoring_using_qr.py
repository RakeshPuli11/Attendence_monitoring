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

    def check_authorised_students(self, x1, x2):
        val = None
        try:
            my_cursor.execute(
                "SELECT roll_no FROM authorised_students where roll_no=(%s) AND user_name=(%s)", (x1, x2))
            val = my_cursor.fetchone()
        except mysql.connector.Error as err:
            print("Error while querying the database:", err)
        return val

    def submit_attendance(self):
        self.roll_no = self.entry1.get()
        self.user_name = self.entry2.get()
        text = self.combobox.get()
        x = datetime.now()
        if text == "Morning" and self.roll_no != "" and self.user_name != "":
            var = self.check_authorised_students(self.roll_no, self.user_name)
            if var:
                my_cursor.execute("INSERT INTO mor(roll_no,user_name,today) values('%s','%s','%s')" % (
                    self.roll_no, self.user_name, x))
                self.valid_input = True
            else:
                messagebox.showerror(
                    "Error", "Please enter valid credentials.")
        elif text == "Evening" and self.roll_no != "" and self.user_name != "":
            var = self.check_authorised_students(self.roll_no, self.user_name)
            if var:
                my_cursor.execute("INSERT INTO eve(roll_no,user_name,today) VALUES ('%s','%s','%s')" % (
                    self.roll_no, self.user_name, x))
                self.valid_input = True
            else:
                messagebox.showerror(
                    "Error", "Please enter valid credentials.")
        else:
            messagebox.showerror("Error", "Please select a valid time.")
            self.valid_input = False
        if self.valid_input:
            decoded_text = self.detect_qr_code()
            if decoded_text == self.roll_no:
                print("QR code matches Roll No.")
                my_cursor.execute(
                    "INSERT INTO xzyfinal(roll_no,time_,attendance_status) VALUES((%s),(%s),'PRESENT')", (self.roll_no, x,))
                messagebox.showinfo(
                    "Success", "Attendance marked successfully.")
                my_cursor.execute("SELECT * FROM xzyfinal")
                rows = my_cursor.fetchall()
                for i in rows:
                    print(i)
            else:
                print("QR code does not match Roll No.")
                messagebox.showerror(
                    "Error", "QR code does not match Roll No.")
        con.commit()
        con.close()

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
    my_cursor.execute(
        "CREATE TABLE IF NOT EXISTS xzyfinal (roll_no varchar(21),time_ datetime, attendance_status char(20))")
    my_cursor.execute("truncate mor")
    my_cursor.execute("truncate eve")
    # my_cursor.execute("ALTER TABLE final_sheet ADD COLUMN roll_no varchar(21)")
    obj = AttendanceMonitor()
    obj.run()
