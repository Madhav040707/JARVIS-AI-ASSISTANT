import threading
import queue
import time
import datetime
import webbrowser
import sys
import speech_recognition as sr
import pyttsx3
import pywhatkit
import wikipedia
import pyjokes
import os
import psutil

APP_PATHS = {
    "chrome": r"C:\Users\user\Desktop\Madhav - Chrome.lnk",
    "notepad": r"C:\Users\user\Desktop\Notepad.lnk",
    "vs code": r"C:\Users\user\Desktop\Visual Studio Code.lnk",
    "calculator": r"C:\Users\user\Desktop\Calculator.lnk",
    "chatgpt": r"C:\Users\user\Desktop\ChatGPT.lnk",
    "codetantra": r"C:\Users\user\Desktop\CodeTantra SEA.lnk",
    "instagram": r"C:\Users\user\Desktop\Instagram.lnk",
    "whatsapp": r"C:\Users\user\Desktop\WhatsApp.lnk",
    "powerpoint" : r"C:\ProgramData\Microsoft\Windows\Start Menu\Programs\PowerPoint.lnk"
}

try:
    import tkinter as tk
    from tkinter import ttk, scrolledtext, messagebox
except Exception:
    raise RuntimeError("Tkinter is required to run the GUI")

# tts
recognizer = sr.Recognizer()
engine = pyttsx3.init()
voices = engine.getProperty('voices')
engine.setProperty('rate', 110)
engine.setProperty('volume', 1)

if len(voices) > 1:
    engine.setProperty('voice', voices[0].id)
    
# noise filters
recognizer.dynamic_energy_threshold = True
recognizer.energy_threshold = 300  
recognizer.pause_threshold = 3   

# Thread-safe queue to send recognized commands to GUI
command_queue = queue.Queue()
listening_flag = threading.Event()

def talk(text):
    """Speak and print to the GUI via the queue."""
    try:
        engine.say(text)
        engine.runAndWait()
    except Exception as e:
        print("TTS Error", e)

def listen_in_background(log_func, timeout = 3, phrase_time_limit = 6):
    with sr.Microphone() as source:
        # small noise adjustment to reduce initial lag
        recognizer.adjust_for_ambient_noise(source , duration=2)
        log_func("Microphone ready. Say 'jarvis' followed by your command.")
        talk("Microphone ready. Say 'jarvis' followed by your command.")
        
        while listening_flag.is_set():
            try:
                audio = recognizer.listen(source, timeout, phrase_time_limit)
            except sr.WaitTimeoutError:
                continue  
            try:
                text = recognizer.recognize_google(audio).lower()
            except sr.UnknownValueError:
                continue
            except sr.RequestError:
                log_func("Network error: speech recognition unavailable.")
                continue

            if 'jarvis' in text:
                cmd = text.replace('jarvis', '').strip()
                log_func(f"Heard: {cmd}")
                talk(f"okay: {cmd} ")
                command_queue.put(cmd)

#  Command handling 

def handle_command(cmd, log_func):
    if not cmd:
        return

    if cmd.startswith('play'):
        song = cmd.replace('play', '').strip()
        log_func(f"Playing: {song}")
        talk(f"Playing {song}")
        threading.Thread(target=pywhatkit.playonyt, args=(song,), daemon=True).start()
        

    elif 'time' in cmd and 'date' in cmd:
        now = datetime.datetime.now().strftime('%I:%M %p, %B %d %Y')
        log_func(f"Time & date: {now}")
        talk(f"The current time and date is {now}")

    elif cmd.startswith('who is') or cmd.startswith('who the heck is'):
        person = cmd.replace('who the heck is', '').replace('who is', '').strip()
        if person:
            try:
                info = wikipedia.summary(person, sentences=1)
                log_func(info)
                talk(info)
            except Exception as e:
                log_func(f"Wiki error: {e}")
                talk("I couldn't fetch that information.")

    elif 'joke' in cmd:
        joke = pyjokes.get_joke()
        # log_func(joke)
        talk(joke)

    elif cmd.startswith('send whatsapp') or cmd.startswith('send message'):
        log_func("For reliable WhatsApp sending, please use the GUI form (phone + message).")
        talk("I opened the WhatsApp panel. Please type the phone number and message and press Send.")
    
    elif "favourite tracks of jarvis" in cmd:
        log_func("ohh that Dil tho baccha hai ji is his favourite song")
        talk("Dil tho baccha hai ji is jarvis's favourite track")
    
    elif "open youtube"in cmd:
        talk("Opening youtube.................")
        time.sleep(1)
        webbrowser.open("https://www.youtube.com")
    
    elif "open university site"  in cmd:
        talk("Welcome to page of your University")
        webbrowser.open("https://www.bennett.edu.in/")
       
    elif "open portal" in  cmd:
        talk("opening LMS Portal For Bennett University")
        webbrowser.open('https://lms.bennett.edu.in/login/index.php')
    
    elif ("shutdown laptop" in cmd) or ("shut down" in cmd) or ("turn off" in cmd) or ("power off" in cmd):
        talk("Shutting down your computer. Goodbye.")
        log_func("System shutdown command received.")
        os.system("shutdown /s /t 1")     # Window shutdown
    
    elif ("restart the laptop" in cmd) or ("reboot" in cmd) :
        talk("restarting your computer. see you soon.")
        log_func("System received command received.")
        os.system("shutdown /r /t 1")     # Window restart
   
    elif cmd.startswith("close"):
        app = cmd.replace("close", "").strip()
        if not app:
            talk("Which app should I close?")
            return
        
        talk(f"Closing {app}.")
        log_func(f"Closing application: {app}")

        closed = False
        for proc in psutil.process_iter(['name']):
            try:
                if app.lower() in proc.info['name'].lower():
                    proc.kill()
                    closed = True
            except:
                pass
        
        if closed:
            talk(f"{app} has been closed.")
        else:
            talk(f"I could not find {app} running.")

    elif "lock screen" in cmd or "lock the screen" in cmd or "lock my pc" in cmd:
        talk("Locking your computer.")
        log_func("Lock screen command executed.")
        os.system("rundll32.exe user32.dll,LockWorkStation")
    
    # command for app opening as i am using dict fetch method
    elif cmd.startswith("on"):
        app = cmd.replace("on", "").strip()

        if not app:
            talk("Which application should I open?")
            return

        log_func(f"opening: {app}")
        talk(f"opening: {app}")
        
        # Check if we know the app
        if app in APP_PATHS:
            try:
                os.startfile(APP_PATHS[app])
                talk(f"Opening {app}.")
            except Exception as e:
                talk(f"Failed to open {app}.")
                log_func(f"Error: {e}")
            
        # elif 'aqi' in cmd:
        
        else:
            talk(f"I don't know where {app} is installed.")
            log_func(f"Unknown app: {app}")
    
    elif "your name" in cmd:
        talk("my name is jarvis i am your Virtual Assistant")
        log_func("my name is jarvis i am your Virtual Assistant")
    
    elif "who made you" in cmd or "who created you" in cmd:
        talk("Algoamigos is my creater creater.") 

    elif "how are you" in cmd:
        talk("i am just code, but i feel fantastic to help you, tell me what can i do for you")

    else:
        log_func("Command not recognized. Try 'play', 'time and date', 'joke', or use the WhatsApp form.")
        talk("Please say the command again.")

#  WhatsApp helper 
def send_whatsapp_number(number: str, message: str, log_func):
    if not number.startswith('+'):
        log_func('Phone number must include country code, e.g. +91XXXXXXXXXX')
        return

    try:
        # Try the instant API if available (pywhatkit >= some versions)
        send_fn = getattr(pywhatkit, 'sendwhatmsg_instantly', None)
        if send_fn:
            log_func('Sending instantly via WhatsApp Web...')
            send_fn(number, message, wait_time=30, tab_close=True, close_time=5)
            talk('Message send attempted (instant).')
        else:
            # Fallback: schedule one minute from now
            now = datetime.datetime.now() + datetime.timedelta(minutes=1)
            h = now.hour
            m = now.minute
            log_func(f'Scheduling WhatsApp message at {h:02d}:{m:02d}. Make sure WhatsApp Web is logged in.')
            pywhatkit.sendwhatmsg(number, message, h, m, wait_time=1, tab_close=True)
            log_func('Scheduled message sent (fallback).')
    except Exception as e:
        log_func(f'WhatsApp send error: {e}')

# ----------------- GUI -----------------
class AssistantGUI:
    def __init__(self, root):
        self.root = root
        root.title('jarvis')
        root.geometry('700x520')

        mainframe = ttk.Frame(root, padding=10)
        mainframe.pack(fill='both', expand=True)

        # Log area
        self.log = scrolledtext.ScrolledText(mainframe, wrap='word', height=18)
        self.log.pack(fill='both', expand=True, pady=(0, 10))
        self.log.configure(state='normal')

        # Controls
        controls = ttk.Frame(mainframe)
        controls.pack(fill='x')

        self.listen_btn = ttk.Button(controls, text='Start Listening', command=self.toggle_listening)
        self.listen_btn.pack(side='left')

        ttk.Label(controls, text='Manual command:').pack(side='left', padx=(10, 2))
        self.cmd_entry = ttk.Entry(controls, width=40)
        self.cmd_entry.pack(side='left', padx=(0, 6))
        ttk.Button(controls, text='Run', command=self.run_manual_command).pack(side='left')

        # WhatsApp frame
        wa_frame = ttk.LabelFrame(mainframe, text='WhatsApp Sender')
        wa_frame.pack(fill='x', pady=(10, 0))

        ttk.Label(wa_frame, text='Phone (with +countrycode):').grid(column=0, row=0, sticky='w', padx=6, pady=6)
        self.phone_entry = ttk.Entry(wa_frame, width=20)
        self.phone_entry.grid(column=1, row=0, sticky='w', padx=6, pady=6)

        ttk.Label(wa_frame, text='Message:').grid(column=0, row=1, sticky='nw', padx=6)
        self.msg_text = tk.Text(wa_frame, height=4, width=50)
        self.msg_text.grid(column=1, row=1, sticky='w', padx=6, pady=6)

        self.send_btn = ttk.Button(wa_frame, text='Send WhatsApp', command=self.send_whatsapp_thread)
        self.send_btn.grid(column=1, row=2, sticky='e', padx=6, pady=6)

        # Periodic check for commands from recognizer thread
        self.root.after(300, self.check_command_queue)

    # GUI helpers
    def log_msg(self, text):
        timestamp = datetime.datetime.now().strftime('%H:%M:%S')
        self.log.insert('end', f'[{timestamp}] {text}\n')
        self.log.see('end')

    def toggle_listening(self):
        if not listening_flag.is_set():
            listening_flag.set()
            self.listen_btn.config(text='Stop Listening')
            t = threading.Thread(target=listen_in_background, args=(self.log_msg,), daemon=True)
            t.start()
            self.log_msg('Listening started.')
            talk("...Hello This is jarvis, i am here for your help .... ")
        else:
            listening_flag.clear()
            self.listen_btn.config(text='Start Listening')
            self.log_msg('Listening stopped.')

    def run_manual_command(self):
        cmd = self.cmd_entry.get().strip().lower()
        if cmd:
            self.log_msg(f'Manual: {cmd}')
            threading.Thread(target=handle_command, args=(cmd, self.log_msg), daemon=True).start()

    def send_whatsapp_thread(self):
        number = self.phone_entry.get().strip()
        message = self.msg_text.get('1.0', 'end').strip()
        if not number or not message:
            messagebox.showwarning('Missing', 'Provide both phone number and message.')
            return
        # Run sending in background
        threading.Thread(target=send_whatsapp_number, args=(number, message, self.log_msg), daemon=True).start()

    def check_command_queue(self):
        try:
            while not command_queue.empty():
                cmd = command_queue.get_nowait()
                threading.Thread(target=handle_command, args=(cmd, self.log_msg), daemon=True).start()
        except queue.Empty:
            pass
        finally:
            self.root.after(300, self.check_command_queue)

# ----------------- Run the GUI -----------------
def main():
    root = tk.Tk()
    gui = AssistantGUI(root)
    root.protocol('WM_DELETE_WINDOW', lambda: on_close(root))
    root.mainloop()


def on_close(root):
    listening_flag.clear()
    try:
        root.destroy()
    except Exception:
        sys.exit(0)


if __name__ == '__main__':
    main()