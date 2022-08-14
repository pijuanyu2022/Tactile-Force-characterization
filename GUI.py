from multiprocessing import Process, Queue
import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from ttkbootstrap.dialogs import Messagebox
import time
import numpy as np

class GUI(ttk.Frame):
    def __init__(self, master, conn, in_conn=None):
        super().__init__(master)

        self.running = ttk.BooleanVar(value=False)
        self.running_1 = ttk.BooleanVar(value=False)
        self.running_2 = ttk.BooleanVar(value=False)
        self.is_trial3_auto = False
        self.is_trial3_low = False
        self.is_trial3_medium = False
        self.is_trial3_high = False
        self.is_label = False

        self.is_trial3_status = False
        self.trial3_break = False
        self.trial1_break = False

        self.is_trial4_status = False
        self.trial4_break = False

        self.is_trial5_auto = False
        self.is_trial5_up = False
        self.is_trial5_in = False
        self.is_trial5_upin = False

        self.is_trial6_set1 = False
        self.is_trial6_set2 = False
        self.is_trial6_set3 = False
        self.is_trial6_set4 = False
        self.trial6_break = False

        self.pause_bar = False
        self.stop_bar = False
        self.has_started_bar = False
        self.trial_finish = False

        self.is_trial1_status = False
        self.is_trial3_status = False

        # queues for multiprocessing
        self.data_queue = conn
        self.in_queue = in_conn

        self.master = master
        
        self.style = ttk.Style()
        self.style.configure('lefttab.TNotebook',tabposition='wn',
                tabmargins=[5, 5, 2, 5],padding= [0, 0],justify= "left",font=("Calibri", 15, "bold"),foreground='green')
                # tabposition='wn',
                # justify= "left",
                # padding= [20, 10],
                # font=("Calibri", "bold"))

        self.style.element_create('Plain.Notebook.tab', "from", 'default')
        self.style.layout("TNotebook.Tab",
            [('Plain.Notebook.tab', {'children':
                [('Notebook.padding', {'side': 'top', 'children':
                    [('Notebook.focus', {'side': 'top', 'children':
                        [('Notebook.label', {'side': 'top', 'sticky': ''})],
                    'sticky': 'nswe'})],
                'sticky': 'nswe'})],
            'sticky': 'nswe'})])

        self.style.configure('TNotebook.Tab', background='green', foreground='green')
        self.style.configure("TNotebook", background='#666666', foreground='green' )
        # self.style.map("TNotebook", background=[("selected", 'green')])
        self.notebk = ttk.Notebook(self.master, style='lefttab.TNotebook')

        # Tabs for each section
        self.frame0 = ttk.Frame(self.notebk, width = 400, height = 400, relief = ttk.SUNKEN)
        self.frame1 = ttk.Frame(self.notebk, width = 400, height = 400, relief = ttk.SUNKEN)
        self.frame2 = ttk.Frame(self.notebk, width = 400, height = 400, relief = ttk.SUNKEN)
        self.frame3 = ttk.Frame(self.notebk, width = 400, height = 400, relief = ttk.SUNKEN)


        self.notebk.add(self.frame0, text = 'Constant                                ')
        self.notebk.add(self.frame1, text = 'Anatomical Localiation Scan')
        self.notebk.add(self.frame2, text = 'Pre Experiment                      ')
        self.notebk.add(self.frame3, text = 'Stimulation Task                    ')
        self.notebk.pack(expand = 1, fill="both")

        self.set_frame0()
        self.set_frame1()
        self.set_frame2()
        self.set_frame3()

        # self.trial_iteration()
 
    # frame functions
    def set_frame0(self):
        # --------------------------- Frame 0 ----------------------------------------------
        self.title = ttk.Label(self.frame0, text="                                                      0. Constant Value", bootstyle=DARK, font=("Calibri", 15, "bold"), background="")
        self.title.grid(row=0, column=0, columnspan=4, padx=10, pady=10)
        self.trial0_row = 0

        ######################### Input Constant Information #######################
        self.sub_lf = ttk.Labelframe(self.frame0,text="Constant Information", bootstyle=INFO)
        self.sub_lf.place(x=40,y=50,width=400,height=450)

        self.subjectInfo = ['Subject Number', 'Age', 'Gender', 'Subject Type', 'Diabetes', 'Years since Stroke', 
                             'Dominant Arm', 'Testing Arm']

        self.subject_result = []

        # Text entry fields
        for i in range(len(self.subjectInfo)):
            ttk.Label(self.sub_lf, text=self.subjectInfo[i],font=("Calibri", 10)).grid(row=i+1, column=0, padx=5, pady=5)
            if self.subjectInfo[i] not in ['Gender', 'Diabetes', 'Dominant Arm', 'Testing Arm']:
                e1 = ttk.Entry(self.sub_lf,show=None)
                e1.grid(row=i+1, column=1, padx=5, pady=5)
                self.subject_result.append(e1)


        # Option Menus
        self.subStringVars = ['Gender', 'Diabetes', 'Dominant Arm', 'Testing Arm']
        # Gender
        self.genders_StinngVar = ttk.StringVar(self.master)
        self.genders_First = 'Select a gender'
        self.genders_StinngVar.set(self.genders_First)
        self.genders_Type = ["Male", "Female", "Other"]
        self.genders_Menu = ttk.OptionMenu(self.sub_lf, self.genders_StinngVar, self.genders_Type[0], *self.genders_Type,)
        self.genders_Menu.grid(row=3, column=1, padx=5, pady=5)
    
        # Diabetes
        self.diabetes_StinngVar = ttk.StringVar(self.master)
        self.diabetes_First = 'YES/NO'
        self.diabetes_StinngVar.set(self.diabetes_First)
        self.diabetes_Type = ['YES','NO']
        self.diabetes_Menu = ttk.OptionMenu(self.sub_lf, self.diabetes_StinngVar, self.diabetes_Type[0], *self.diabetes_Type)
        self.diabetes_Menu.grid(row=5, column=1, padx=5, pady=5)

        # Dominant Arm
        self.domArm_StinngVar = ttk.StringVar(self.master)
        self.domArm_First = 'Left/Right'
        self.domArm_StinngVar.set(self.domArm_First)
        self.domArm_Type = ['Left','Right']
        self.domArm_Menu = ttk.OptionMenu(self.sub_lf, self.domArm_StinngVar, self.domArm_Type[0], *self.domArm_Type)
        self.domArm_Menu.grid(row=7, column=1, padx=5, pady=5)

        # Test Arm
        self.TestArm_StinngVar = ttk.StringVar(self.master)
        self.TestArm_First = 'Left/Right'
        self.TestArm_StinngVar.set(self.TestArm_First)
        self.TestArm_Type = ['Left','Right']
        self.TestArm_Menu = ttk.OptionMenu(self.sub_lf, self.TestArm_StinngVar, self.TestArm_Type[0], *self.TestArm_Type)
        self.TestArm_Menu.grid(row=8, column=1, padx=5, pady=5)

        # Submit constant information
        self.Constant_Sub = ttk.Button(self.sub_lf, text="Save", bootstyle=(INFO, OUTLINE), command=self.trial0_save)
        self.Constant_Sub.grid(row=9,column=1, padx=5, pady=5)

        ######################### Manual Control #######################
        self.trial0_exp_lf = ttk.Labelframe(self.frame0,text="Manual Control", bootstyle=INFO)
        self.trial0_exp_lf.place(x=470,y=50,width=370,height=450)


        self.trial0_info = ['This section will be used to control the solenoid', 'manually. If you do not want to control the ', 'device manualy, please ignore this part',' ','      Set the pressure value in range 1500 - 3100', 'Choose to open the solenoid']

        self.trial0_result = []

        for i in range(4):
            self.trial0_label = ttk.Label(self.trial0_exp_lf, text=self.trial0_info[i],font=("Calibri", 10)).grid(row=i, column=0, columnspan=2, padx=5, pady=5)

        self.trial0_label = ttk.Label(self.trial0_exp_lf, text=self.trial0_info[4],font=("Calibri", 10)).grid(row=5, column=0, columnspan=2, padx=5, pady=5)
        self.trial0_label = ttk.Label(self.trial0_exp_lf, text=self.trial0_info[5],font=("Calibri", 10)).grid(row=7, column=0, columnspan=2, padx=5, pady=5)

        e2 = ttk.Entry(self.trial0_exp_lf,show=None)
        e2.grid(row=6, column=0, columnspan=2, padx=5, pady=5)
        self.trial0_result.append(e2)


        self.trial0_start_StinngVar = ttk.StringVar(self.master)
        self.trial0_start_First = 'Select a task'
        self.trial0_start_StinngVar.set(self.trial0_start_First)
        self.trial0_start_Type = ["Pop out", "retract"]
        self.trial0_start_Menu = ttk.OptionMenu(self.trial0_exp_lf, self.trial0_start_StinngVar, self.trial0_start_Type[0], *self.trial0_start_Type,)
        self.trial0_start_Menu.grid(row=8,column=0, columnspan=2, padx=5, pady=5)

        self.trial0_button = ttk.Button(self.trial0_exp_lf, text="Start", command=self.trial0_start, bootstyle=DANGER)
        self.trial0_button.grid(row=9,column=0, columnspan=2, padx=5, pady=5)

        self.trial0_button = ttk.Button(self.trial0_exp_lf, text="Save", command=self.trial0_save_data, bootstyle=DANGER)
        self.trial0_button.grid(row=10,column=0, columnspan=2, padx=5, pady=5)

        # End 
        self.End_lf = ttk.Frame(self.frame0)
        self.End_lf.place(x=700,y=700,width=100,height=50)

        self.quit = ttk.Button(self.End_lf, text='Exit', command=self.close, bootstyle=DANGER)
        self.quit.grid(row=0,column=0,padx=5, pady=5)

    def set_frame1(self):

        # Bool number
        self.is_trial1_EMG = False
        self.is_trial1_in = False
        self.is_trial1_out = False
        self.is_trial1_up = False

        self.is_start_trial1 = True

        self.title = ttk.Label(self.frame1, text="                                          1, Anatomical Localiation Scan", bootstyle=DARK, font=("Calibri", 15, "bold"), background="")
        self.title.grid(row=0, column=0, columnspan=4, padx=10, pady=10)
        self.trial1_row = 0

        ### Description
        # add EF label frame
        self.trial1_lf = ttk.Labelframe(self.frame1,text="Preparation", bootstyle=INFO)
        self.trial1_lf.place(x=10,y=50,width=830,height=230)

        # description
        self.description_2 = ttk.Label(self.trial1_lf, text="This trial type will be used to do an anatomical localization scan. It will have two sets (Right and Left).",font=("Calibri", 11))
        self.description_2.grid(row=self.trial1_row+1, column=0, columnspan=4, padx=5, pady=5)

        self.description_2 = ttk.Label(self.trial1_lf, text="Each set has ten trials. Each trial will pop out the piston ten times. And then there will be 30 second to relax.",font=("Calibri", 11))
        self.description_2.grid(row=self.trial1_row+2, column=0,columnspan=4, padx=5, pady=5)

        # # INPUT MVT
        self.input_subj = ttk.Label(self.trial1_lf, text="Subject Number:  ",font=("Calibri", 10))
        self.input_subj.grid(row=self.trial1_row+3, column=0, padx=5, pady=5)

        self.input_subj = ttk.Label(self.trial1_lf, text="Subject Age:  ",font=("Calibri", 10))
        self.input_subj.grid(row=self.trial1_row+3, column=2, padx=5, pady=5)

        self.input_subj = ttk.Label(self.trial1_lf, text="Subject Gender:  ",font=("Calibri", 10))
        self.input_subj.grid(row=self.trial1_row+4, column=0, padx=5, pady=5)

        self.input_subj = ttk.Label(self.trial1_lf, text="Subject Type:  ",font=("Calibri", 10))
        self.input_subj.grid(row=self.trial1_row+4, column=2, padx=5, pady=5)

        self.input_subj = ttk.Label(self.trial1_lf, text="Years since Stroke:  ",font=("Calibri", 10))
        self.input_subj.grid(row=self.trial1_row+5, column=0, padx=5, pady=5)

        self.input_subj = ttk.Label(self.trial1_lf, text="Testing arm:  ",font=("Calibri", 10))
        self.input_subj.grid(row=self.trial1_row+5, column=2, padx=5, pady=5)

        ### Experimental 
        # add trial1 experimental label frame
        self.trial1_exp_lf = ttk.Labelframe(self.frame1,text="Experimental", bootstyle=INFO)
        self.trial1_exp_lf.place(x=10,y=300,width=830,height=365)

        # # UP IN UP&IN
        self.title_1 = ttk.Label(self.trial1_exp_lf, text="Choose Tasks",font=("Calibri", 12, "bold"), bootstyle=PRIMARY)
        self.title_1.grid(row=self.trial1_row+0, column=0, padx=5, pady=5)


        self.trial1_start_StinngVar_1 = ttk.StringVar(self.master)
        self.trial1_start_First = 'Select a task'
        self.trial1_start_StinngVar_1.set(self.trial1_start_First)
        self.trial1_start_Type = ["Automatic", "Right", "Left"]
        self.trial1_start_Menu = ttk.OptionMenu(self.trial1_exp_lf, self.trial1_start_StinngVar_1, self.trial1_start_Type[0], *self.trial1_start_Type,)
        self.trial1_start_Menu.grid(row=self.trial1_row+0,column=1, padx=5, pady=5)

        self.trial1_start_StinngVar_2 = ttk.StringVar(self.master)
        self.trial1_start_First = 'Select a task'
        self.trial1_start_StinngVar_2.set(self.trial1_start_First)
        self.trial1_start_Type = ["Auto", "Trial 1","Trial 2","Trial 3","Trial 4","Trial 5","Trial 6","Trial 7","Trial 8","Trial 9","Trial 10"]
        self.trial1_start_Menu = ttk.OptionMenu(self.trial1_exp_lf, self.trial1_start_StinngVar_2, self.trial1_start_Type[0], *self.trial1_start_Type,)
        self.trial1_start_Menu.grid(row=self.trial1_row+0,column=2, padx=5, pady=5)


        self.trial1_button = ttk.Button(self.trial1_exp_lf, text="Start", command=self.trial1_Start, bootstyle=DANGER)
        self.trial1_button.grid(row=self.trial1_row+0,column=3, padx=5, pady=5)

        self.trial1_button_2 = ttk.Button(self.trial1_exp_lf, text="Stop", command=self.trial1_stop, bootstyle=DANGER)
        self.trial1_button_2.grid(row=self.trial1_row+0,column=4, padx=5, pady=5)

        # Trial and Status
        self.title_1 = ttk.Label(self.trial1_exp_lf, text="Current Trial: ",font=("Calibri", 12, "bold"))
        self.title_1.grid(row=self.trial1_row+2, column=0, padx=5, pady=5)

        self.title_1 = ttk.Label(self.trial1_exp_lf, text="Current Status: ",font=("Calibri", 12, "bold"))
        self.title_1.grid(row=self.trial1_row+2, column=2, padx=5, pady=5)

        self.title_1 = ttk.Label(self.trial1_exp_lf, text="       ",font=("Calibri", 12, "bold"))
        self.title_1.grid(row=self.trial1_row+3, column=2, padx=5, pady=5) 


        # Starting 
        self.title_1 = ttk.Label(self.trial1_exp_lf, text="The Experimental Progress Bar",font=("Calibri", 12, "bold"), bootstyle=INFO)
        self.title_1.grid(row=self.trial1_row+5, column=0, columnspan=5, padx=5, pady=5)   

        self.title_1 = ttk.Label(self.trial1_exp_lf, text="       ",font=("Calibri", 12, "bold"))
        self.title_1.grid(row=self.trial1_row+6, column=0, padx=5, pady=5)   

        self.trial1_bar_max = 1000
        self.title_1_fg = ttk.Floodgauge(self.trial1_exp_lf, bootstyle=INFO, length=750, maximum=self.trial1_bar_max, font=("Calibri", 12, 'bold'),)
        self.title_1_fg.grid(row=self.trial1_row+7, column=0, columnspan=5, padx=5, pady=3)  

        self.add_trial1()
        # End 
        self.End_lf = ttk.Frame(self.frame1)
        self.End_lf.place(x=700,y=740,width=100,height=50)

        self.quit = ttk.Button(self.End_lf, text='Exit', command=self.close, bootstyle=DANGER)
        self.quit.grid(row=0,column=0,padx=5, pady=5)

    def set_frame2(self): 
        # --------------------------- Frame 2 ----------------------------------------------
        self.trial2_row = 1
        self.is_start_trial2 = True
        # Title
        self.title = ttk.Label(self.frame2, text="                                          2. Pre experiment", bootstyle=DARK, font=("Calibri", 15, "bold"), background="")
        self.title.grid(row=0, column=0, columnspan=4, padx=10, pady=10)

        ### Description
        # add EF label frame
        self.trial2_lf = ttk.Labelframe(self.frame2,text="Preparation", bootstyle=INFO)
        self.trial2_lf.place(x=10,y=50,width=830,height=230)

        # description
        self.description_2 = ttk.Label(self.trial2_lf, text="This trial type will be used to get the weak, medium and high pressure threshold.",font=("Calibri", 11))
        self.description_2.grid(row=self.trial2_row+1, column=0, columnspan=4, padx=5, pady=5)

        self.description_2 = ttk.Label(self.trial2_lf, text="                                                                                ",font=("Calibri", 11))
        self.description_2.grid(row=self.trial2_row+2, column=0,columnspan=4, padx=5, pady=5)

        # # INPUT MVT
        self.input_subj = ttk.Label(self.trial2_lf, text="Subject Number:  ",font=("Calibri", 10))
        self.input_subj.grid(row=self.trial2_row+3, column=0, padx=5, pady=5)

        self.input_subj = ttk.Label(self.trial2_lf, text="Subject Age:  ",font=("Calibri", 10))
        self.input_subj.grid(row=self.trial2_row+3, column=2, padx=5, pady=5)

        self.input_subj = ttk.Label(self.trial2_lf, text="Subject Gender:  ",font=("Calibri", 10))
        self.input_subj.grid(row=self.trial2_row+4, column=0, padx=5, pady=5)

        self.input_subj = ttk.Label(self.trial2_lf, text="Subject Type:  ",font=("Calibri", 10))
        self.input_subj.grid(row=self.trial2_row+4, column=2, padx=5, pady=5)

        self.input_subj = ttk.Label(self.trial2_lf, text="Years since Stroke:  ",font=("Calibri", 10))
        self.input_subj.grid(row=self.trial2_row+5, column=0, padx=5, pady=5)

        self.input_subj = ttk.Label(self.trial2_lf, text="Testing arm:  ",font=("Calibri", 10))
        self.input_subj.grid(row=self.trial2_row+5, column=2, padx=5, pady=5)

        ### Experimental 
        # add trial2 experimental label frame
        self.trial2_exp_lf = ttk.Labelframe(self.frame2,text="Experimental", bootstyle=INFO)
        self.trial2_exp_lf.place(x=10,y=310,width=830,height=300)

        # enter value
        self.title_2 = ttk.Label(self.trial2_exp_lf, text="Enter initial value in range 0-3150: ",font=("Calibri", 10))
        self.title_2.grid(row=self.trial2_row+0, column=0, padx=5, pady=5)

        self.trial2_input = ttk.Entry(self.trial2_exp_lf,show=None)
        self.trial2_input.grid(row=self.trial2_row+0, column=1, padx=5, pady=5)


        self.trial2_button = ttk.Button(self.trial2_exp_lf, text="Start", command=self.trial2_Start, bootstyle=DANGER)
        self.trial2_button.grid(row=self.trial2_row+0,column=2, padx=5, pady=5)

        # time and force
        self.trial2_button_3 = ttk.Button(self.trial2_exp_lf, text="Record", command=self.trial2_stop, bootstyle=SUCCESS)
        self.trial2_button_3.grid(row=self.trial2_row+0,column=3, padx=5, pady=5)


        self.title_2 = ttk.Label(self.trial2_exp_lf, text="       ",font=("Calibri", 12, "bold"))
        self.title_2.grid(row=self.trial2_row+2, column=0, padx=5, pady=5) 


        # End 
        self.End_lf = ttk.Frame(self.frame2)
        self.End_lf.place(x=700,y=750,width=100,height=50)

        self.quit = ttk.Button(self.End_lf, text='Exit', command=self.close, bootstyle=DANGER)
        self.quit.grid(row=0,column=0,padx=5, pady=5)

    def set_frame3(self): 
        # --------------------------- Frame 3 ----------------------------------------------
        self.trial3_row = 1
        self.is_start_trial3 = True
        # Title
        self.title = ttk.Label(self.frame3, text="                                          3. Stimulation Task", bootstyle=DARK, font=("Calibri", 15, "bold"), background="")
        self.title.grid(row=0, column=0, columnspan=4, padx=10, pady=10)

         ### Description
        # add EF label frame
        self.trial3_lf = ttk.Labelframe(self.frame3,text="Preparation", bootstyle=INFO)
        self.trial3_lf.place(x=10,y=50,width=830,height=330)

        # description
        self.description_3 = ttk.Label(self.trial3_lf, text="    This section are used to do the stimulation task. It will have two set (Right and Left). Each set has nine trials. ",font=("Calibri", 11))
        self.description_3.grid(row=self.trial3_row+0, column=0, columnspan=4, padx=5, pady=5)

        self.description_3 = ttk.Label(self.trial3_lf, text="The duration of each test will increase from 6.0 second to 10.0 second. The order of force will be a latin square.",font=("Calibri", 11))
        self.description_3.grid(row=self.trial3_row+1, column=0, columnspan=4, padx=5, pady=5)

        self.description_3 = ttk.Label(self.trial3_lf, text="Example: Trial1: Low + 6.0(relax) + medium + 6.5 + high + 7.0 ",font=("Calibri", 11))
        self.description_3.grid(row=self.trial3_row+2, column=0, columnspan=4, padx=5, pady=5)

        self.description_3 = ttk.Label(self.trial3_lf, text="                 Trial2: medium + 6.5(relax) + high + 7.0 + Low + 7.5 ",font=("Calibri", 11))
        self.description_3.grid(row=self.trial3_row+3, column=0, columnspan=4, padx=5, pady=5)
        
        self.description_3 = ttk.Label(self.trial3_lf, text="Latin Square: low medium high         [6.0, 6.5, 7.0] [7.5, 8.0, 8.5] [9.0, 9.5, 10.0]",font=("Calibri", 11))
        self.description_3.grid(row=self.trial3_row+4, column=0, columnspan=4, padx=5, pady=5)

        self.description_3 = ttk.Label(self.trial3_lf, text="                        medium high low         [6.5, 7.0, 7.5] [8.0, 8.5, 9.0] [9.5, 10.0, 6.0]",font=("Calibri", 11))
        self.description_3.grid(row=self.trial3_row+5, column=0, columnspan=4, padx=5, pady=5)

        self.description_3 = ttk.Label(self.trial3_lf, text="                        high low medium         [7.0, 7.5, 8.0] [8.5, 9.0, 9.5] [10.0, 6.0, 6.5]",font=("Calibri", 11))
        self.description_3.grid(row=self.trial3_row+6, column=0, columnspan=4, padx=5, pady=5)

        ### Experimental 
        # add trial3 experimental label frame
        self.trial3_exp_lf = ttk.Labelframe(self.frame3,text="Experimental", bootstyle=INFO)
        self.trial3_exp_lf.place(x=10,y=410,width=830,height=300)

        # select trail and task
        self.title_3 = ttk.Label(self.trial3_exp_lf, text="Choose to Start the Task",font=("Calibri", 12, "bold"), bootstyle=PRIMARY)
        self.title_3.grid(row=self.trial3_row+0, column=0, padx=5, pady=5)


        self.trial3_start_StinngVar_1 = ttk.StringVar(self.master)
        self.trial3_start_First = 'Select a task'
        self.trial3_start_StinngVar_1.set(self.trial3_start_First)
        self.trial3_start_Type = ["Automatic", "Left", "Right"]
        self.trial3_start_Menu = ttk.OptionMenu(self.trial3_exp_lf, self.trial3_start_StinngVar_1, self.trial3_start_Type[0], *self.trial3_start_Type,)
        self.trial3_start_Menu.grid(row=self.trial3_row+0,column=1, padx=5, pady=5)

        self.trial3_start_StinngVar_2 = ttk.StringVar(self.master)
        self.trial3_start_First = 'Select a task'
        self.trial3_start_StinngVar_2.set(self.trial3_start_First)
        self.trial3_start_Type = ["Auto", "Trial 1", "Trial 2", "Trial 3", "Trial 4", "Trial 5", "Trial 6", "Trial 7", "Trial 8", "Trial 9"]
        self.trial3_start_Menu = ttk.OptionMenu(self.trial3_exp_lf, self.trial3_start_StinngVar_2, self.trial3_start_Type[0], *self.trial3_start_Type,)
        self.trial3_start_Menu.grid(row=self.trial3_row+0,column=2, padx=5, pady=5)

        # add start and stop button
        self.trial3_button = ttk.Button(self.trial3_exp_lf, text="Start", command=self.trial3_Start, bootstyle=DANGER)
        self.trial3_button.grid(row=self.trial3_row+0,column=3, padx=5, pady=5)

        self.trial3_button_2 = ttk.Button(self.trial3_exp_lf, text="Stop", command=self.trial3_stop, bootstyle=DANGER)
        self.trial3_button_2.grid(row=self.trial3_row+0,column=4, padx=5, pady=5)

        # time and force
        self.title_3 = ttk.Label(self.trial3_exp_lf, text="Current Trial: ",font=("Calibri", 12, "bold"))
        self.title_3.grid(row=self.trial3_row+1, column=0, padx=5, pady=5)

        self.title_3 = ttk.Label(self.trial3_exp_lf, text="Current Status: ",font=("Calibri", 12, "bold"))
        self.title_3.grid(row=self.trial3_row+1, column=2, padx=5, pady=5)

        self.title_3 = ttk.Label(self.trial3_exp_lf, text="       ",font=("Calibri", 12, "bold"))
        self.title_3.grid(row=self.trial3_row+2, column=0, padx=5, pady=5) 


        # Progress bar
        self.title_3 = ttk.Label(self.trial3_exp_lf, text="The Experimental Progress Bar",font=("Calibri", 12, "bold"), bootstyle=INFO)
        self.title_3.grid(row=self.trial3_row+4, column=0, columnspan=4, padx=5, pady=5)   

        self.title_3 = ttk.Label(self.trial3_exp_lf, text="       ",font=("Calibri", 12, "bold"))
        self.title_3.grid(row=self.trial3_row+5, column=0, padx=5, pady=5)   

        self.title_3_fg = ttk.Floodgauge(self.trial3_exp_lf, bootstyle=INFO, length=750, maximum=1000, font=("Calibri", 12, 'bold'),)
        self.title_3_fg.grid(row=self.trial3_row+6, column=0, columnspan=5, padx=5, pady=3)  


        # End 
        self.End_lf = ttk.Frame(self.frame3)
        self.End_lf.place(x=700,y=750,width=100,height=50)

        self.quit = ttk.Button(self.End_lf, text='Exit', command=self.close, bootstyle=DANGER)
        self.quit.grid(row=0,column=0,padx=5, pady=5)


    # Helper functions
    def transmit(self, header, information):
        self.data_queue.put((header, information))

    def showError(self):
        print("retrycancel: ",Messagebox.show_error(title='Oh no', message="All fields should be filled"))

    # close the window
    def close(self):
        self.transmit("Close", "close")

    def pause(self):
        self.transmit("Pause", "pause")
        self.pause_bar = True
        print("Pause")

    def calculate_bar(self, mode):

        # Trial 1
        if mode == "trial1":
            # bar time
            bar_matrix = []
            bar_matrix.append(12)
            for i in range(11):
                bar_matrix.append(int(((i*2)/21.2)*718+12))
                bar_matrix.append(int(((i*2+2)/21.2)*718+12))
        
        elif mode == "trial3_low":
            self.latin_square = [[6.0, 6.5, 7.0],
                                 [6.5, 7.0, 7.5],
                                 [7.0, 7.5, 8.0],
                                 [7.5, 8.0, 8.5],
                                 [8.0, 8.5, 9.0],
                                 [8.5, 9.0, 9.5],
                                 [9.0, 9.5, 10.0],
                                 [9.5, 10.0, 6.0],
                                 [10.0, 6.0, 6.5],]

            # bar time
            start = 2.0            
            out_1 = start+2.0             
            relax_1 = out_1+self.latin_square[0][0]     
            out_2 = relax_1+2.0
            relax_2 = out_2+self.latin_square[0][1] 
            out_3 = relax_2+2.0 
            relax_3 = out_3+self.latin_square[0][2]
              
            
            # insert bar time into the matrix
            
            bar_matrix = []
            bar_matrix.append(12)
            bar_matrix.append(int((start/relax_3)*718+12))
            bar_matrix.append(int((out_1/relax_3)*718+12))
            bar_matrix.append(int((relax_1/relax_3)*718+12))
            bar_matrix.append(int((out_2/relax_3)*718+12))
            bar_matrix.append(int((relax_2/relax_3)*718+12))
            bar_matrix.append(int((out_3/relax_3)*718+12))

        elif mode == "trial3_medium":

            # bar time
            start = 2.0            
            out_1 = start+2.0             
            relax_1 = out_1+self.latin_square[1][0]     
            out_2 = relax_1+2.0
            relax_2 = out_2+self.latin_square[1][1] 
            out_3 = relax_2+2.0 
            relax_3 = out_3+self.latin_square[1][2]
              
            
            # insert bar time into the matrix
            
            bar_matrix = []
            bar_matrix.append(12)
            bar_matrix.append(int((start/relax_3)*718+12))
            bar_matrix.append(int((out_1/relax_3)*718+12))
            bar_matrix.append(int((relax_1/relax_3)*718+12))
            bar_matrix.append(int((out_2/relax_3)*718+12))
            bar_matrix.append(int((relax_2/relax_3)*718+12))
            bar_matrix.append(int((out_3/relax_3)*718+12))
        
        elif mode == "trial3_high":
    
            # bar time
            start = 2.0            
            out_1 = start+2.0             
            relax_1 = out_1+self.latin_square[2][0]     
            out_2 = relax_1+2.0
            relax_2 = out_2+self.latin_square[2][1] 
            out_3 = relax_2+2.0 
            relax_3 = out_3+self.latin_square[2][2]
              
            
            # insert bar time into the matrix
            
            bar_matrix = []
            bar_matrix.append(12)
            bar_matrix.append(int((start/relax_3)*718+12))
            bar_matrix.append(int((out_1/relax_3)*718+12))
            bar_matrix.append(int((relax_1/relax_3)*718+12))
            bar_matrix.append(int((out_2/relax_3)*718+12))
            bar_matrix.append(int((relax_2/relax_3)*718+12))
            bar_matrix.append(int((out_3/relax_3)*718+12))


        return bar_matrix    

    # ---------------------------------------functions in frame 0---------------------------------------

    # check if all the data has been submitted in the frame 0
    def checkFields_frame0(self):
        result = []
        for i in range(4):
            result.append(self.subject_result[i].get())
        for i in result:
            if i == '':
                self.showError()
                break      
    
    def trial0_save_data(self):
        self.transmit("Save_data", 'save_data')

    def trial0_start(self):
        # save the data
        trial0_exp_saved = []
        trial0_exp_header = []
        trial0_exp_header.append('Pressure regulator value')
        trial0_exp_header.append('Solenoid value')

        # save the subject information data
        trial0_exp_saved.append(self.trial0_result[0].get())
        trial0_exp_saved.append(self.trial0_start_StinngVar.get())

        is_correct = True
        if self.checkFields_frame0():
            is_correct = False

        if is_correct:
            trial0_control_Final = dict(zip(trial0_exp_header, trial0_exp_saved))
            self.transmit("Task0_control", trial0_control_Final)
            print(trial0_control_Final)

    def trial0_save(self):
        # save the data
        trial0_saved = []
        trial0_header = []
        for i in range(8):
            trial0_header.append(self.subjectInfo[i])

        # save the subject information data
        for i in range(4):
            trial0_saved.append(self.subject_result[i].get())

        trial0_saved.append(self.genders_StinngVar.get())
        trial0_saved.append(self.diabetes_StinngVar.get())
        trial0_saved.append(self.domArm_StinngVar.get())
        trial0_saved.append(self.TestArm_StinngVar.get())
        
        # reset the subject saved list
        disabtes = trial0_saved.pop(2)
        subject_type = trial0_saved.pop(2)
        trial0_saved.insert(3, disabtes)
        trial0_saved.insert(5, subject_type)

        # make sure all data has been input
        is_correct = True
        if self.checkFields_frame0():
            is_correct = False
        
        # if all data has been submitted correctly
        if is_correct:
            self.label1 = ttk.Label(self.sub_lf, text='Successfully Input !', bootstyle=SUCCESS)
            self.label1.grid(row=10, column=1)

            trial0_Final = dict(zip(trial0_header, trial0_saved))
            self.transmit("Task0_save", trial0_Final)

            print(trial0_Final)

            for i in [self.trial1_lf]:
    
                self.input_subj = ttk.Label(i, text=trial0_saved[0],font=("Calibri", 10), bootstyle=SUCCESS)
                self.input_subj.grid(row=self.trial2_row+2, column=1, padx=5, pady=5)              

                self.input_subj = ttk.Label(i, text=trial0_saved[1],font=("Calibri", 10), bootstyle=SUCCESS)
                self.input_subj.grid(row=self.trial2_row+2, column=3, padx=5, pady=5)   

                self.input_subj = ttk.Label(i, text=trial0_saved[2],font=("Calibri", 10), bootstyle=SUCCESS)
                self.input_subj.grid(row=self.trial2_row+3, column=1, padx=5, pady=5) 

                self.input_subj = ttk.Label(i, text=trial0_saved[3],font=("Calibri", 10), bootstyle=SUCCESS)
                self.input_subj.grid(row=self.trial2_row+3, column=3, padx=5, pady=5) 

                self.input_subj = ttk.Label(i, text=trial0_saved[5],font=("Calibri", 10), bootstyle=SUCCESS)
                self.input_subj.grid(row=self.trial2_row+4, column=1, padx=5, pady=5) 

                self.input_subj = ttk.Label(i, text=trial0_saved[7],font=("Calibri", 10), bootstyle=SUCCESS)
                self.input_subj.grid(row=self.trial2_row+4, column=3, padx=5, pady=5)  


    # ---------------------------------------functions in frame 1---------------------------------------

    def trial1_Start(self):
        self.pause_bar = False
        self.stop_bar = False
        # save the data
        trial1_saved = []

        trial1_header = []
        trial1_header.append('Experiment Mode')
        trial1_header.append('Experiment Status')

        # make sure all data has been input
        is_correct = True
        if self.checkFields_frame0():
            is_correct = False

        # if all data has been submitted correctly
        if is_correct:
            if self.trial1_start_StinngVar_1.get() == "Automatic" and self.trial1_start_StinngVar_2.get() == "Auto":
                self.trial1_break = False
                for set_count in range(1,3):
                    for trial_count in range(1,11):
                        if self.trial1_break:
                            break
                        if set_count == 1:
                            trial1_saved.append("Left")
                        else:
                            trial1_saved.append("Right")
                        
                        trial1_saved.append("Trial " + str(trial_count))
                        trial1_maxFinal = dict(zip(trial1_header, trial1_saved))
                        
                        if self.trial_finish or self.is_start_trial1:
                            self.transmit("Task1", trial1_maxFinal)
                            print(trial1_maxFinal)
                            self.is_start_trial1 = False
                            trial1_saved.pop()
                            trial1_saved.pop()

                        # delete the old bar
                        self.delete_trial1_label()

                        # add label on the bar
                        self.add_trial1_status(set_count,trial_count) 

                        # start the progressive bar
                        self.start_trial1_bar(800)

                        time.sleep(5)

            elif self.trial1_start_StinngVar_1.get()[0] != "A" and self.trial1_start_StinngVar_2.get()[0] != "A":
                trial1_saved.append(self.trial1_start_StinngVar_1.get())
                trial1_saved.append(self.trial1_start_StinngVar_2.get())

                trial1_maxFinal = dict(zip(trial1_header, trial1_saved))
                if self.trial_finish or self.is_start_trial1:
                    self.transmit("Task1", trial1_maxFinal)
                    self.is_start_trial1 = False
                    print(trial1_maxFinal)
                # delete the old bar
                self.delete_trial1_label()

                if self.trial1_start_StinngVar_1.get() == "Left":
                    # add label on the bar
                    self.add_trial1_status(1,int(self.trial1_start_StinngVar_2.get()[6]))  
                else:
                    self.add_trial1_status(2,int(self.trial1_start_StinngVar_2.get()[6]))

                # start the progressive bar
                self.start_trial1_bar(800)      
            else:
                print("retrycancel: ",Messagebox.show_error(title='Oh no', message="Please choose correct task!"))   

    def add_trial1_status(self, set_number, trial_number):
        if set_number == 1:
            self.title_1_current_trial = ttk.Label(self.trial1_exp_lf, text="Left "+" Trial "+ str(trial_number),font=("Calibri", 12, "bold"), bootstyle=WARNING)
        else:
            self.title_1_current_trial = ttk.Label(self.trial1_exp_lf, text="Right "+" Trial "+ str(trial_number),font=("Calibri", 12, "bold"), bootstyle=WARNING)
        self.title_1_current_trial.grid(row=self.trial1_row+2, column=1, padx=5, pady=5)

        self.title_1_status_1 = ttk.Label(self.trial1_exp_lf, text="Strong force",font=("Calibri", 12, "bold"), bootstyle=WARNING)
        self.title_1_status_1.grid(row=self.trial1_row+2, column=3, padx=5, pady=5)   

        self.is_trial1_status = True

    def delete_trial1_label(self):
        if self.is_trial1_status:
            self.title_1_current_trial.grid_forget()
            self.title_1_status_1.grid_forget()

        self.is_trial1_status = False

    def trial1_stop(self):
        self.stop_bar = True
        self.trial_finish = True
        self.trial1_break = True
        self.min_value = 0
        self.title_1_fg.grid_forget()
        self.title_1_fg = ttk.Floodgauge(self.trial1_exp_lf, bootstyle=INFO, length=750, maximum=self.trial1_bar_max, font=("Calibri", 12, 'bold'),)
        self.title_1_fg.grid(row=self.trial1_row+8, column=0, columnspan=5, padx=5, pady=3)  
        self.title_1_fg['value'] = 0

    def start_trial1_bar(self, max):
        # start the progressive bar
        self.title_1_fg['maximum'] = max
        self.title_1_fg['value'] = 0

        # if bar has never been start 
        if self.has_started_bar and not self.trial_finish:
            self.min = self.min_value
        else:
            self.min = 0

        is_get_min = False

        for i in range(self.min, max):

            if self.stop_bar:
                self.title_1_fg['value'] = 0
                self.trial1_exp_lf.update()
                time.sleep(0.05)
            else:
                self.title_1_fg['value'] = i+1
                self.trial1_exp_lf.update()
                time.sleep(0.05) 
                
            if self.title_1_fg['value'] == max:
                self.trial_finish = True
                if self.trial1_start_StinngVar_1.get() != "Automatic":
                    self.trial1_stop()


    def add_trial1(self):
        self.trial1_start_pos = self.calculate_bar("trial1")

        self.trial1_1 = ttk.Label(self.frame1, text="| Start ",font=("Calibri", 10, "bold"))
        self.trial1_1.place(x=self.trial1_start_pos[0],y=495)  

        self.trial1_2 = ttk.Label(self.frame1, text="| out ",font=("Calibri", 10, "bold"))
        self.trial1_2.place(x=self.trial1_start_pos[2],y=495) 

        self.trial1_3 = ttk.Label(self.frame1, text="| out ",font=("Calibri", 10, "bold"))
        self.trial1_3.place(x=self.trial1_start_pos[4],y=495) 

        self.trial1_4 = ttk.Label(self.frame1, text="| out ",font=("Calibri", 10, "bold"))
        self.trial1_4.place(x=self.trial1_start_pos[6],y=495) 

        self.trial1_5 = ttk.Label(self.frame1, text="| out ",font=("Calibri", 10, "bold"))
        self.trial1_5.place(x=self.trial1_start_pos[8],y=495) 

        self.trial1_5 = ttk.Label(self.frame1, text="| out ",font=("Calibri", 10, "bold"))
        self.trial1_5.place(x=self.trial1_start_pos[10],y=495) 

        self.trial1_5 = ttk.Label(self.frame1, text="| out ",font=("Calibri", 10, "bold"))
        self.trial1_5.place(x=self.trial1_start_pos[12],y=495) 

        self.trial1_5 = ttk.Label(self.frame1, text="| out ",font=("Calibri", 10, "bold"))
        self.trial1_5.place(x=self.trial1_start_pos[14],y=495) 

        self.trial1_5 = ttk.Label(self.frame1, text="| out ",font=("Calibri", 10, "bold"))
        self.trial1_5.place(x=self.trial1_start_pos[16],y=495) 

        self.trial1_5 = ttk.Label(self.frame1, text="| out ",font=("Calibri", 10, "bold"))
        self.trial1_5.place(x=self.trial1_start_pos[18],y=495) 

        self.trial1_5 = ttk.Label(self.frame1, text="| out ",font=("Calibri", 10, "bold"))
        self.trial1_5.place(x=self.trial1_start_pos[20],y=495) 

        self.trial1_5 = ttk.Label(self.frame1, text="| End ",font=("Calibri", 10, "bold"))
        self.trial1_5.place(x=self.trial1_start_pos[22],y=495) 

        self.is_trial1 = True

    # ---------------------------------------functions in frame 2---------------------------------------
    def trial2_Start(self):
        self.pause_bar = False
        self.stop_bar = False
        # save the data
        trial2_saved = []

        trial2_header = []
        trial2_header.append('Experiment Mode')

        # make sure all data has been input
        is_correct = True
        if self.checkFields_frame0():
            is_correct = False

        # if all data has been submitted correctly
        if is_correct:
            trial2_saved.append(self.trial2_input.get())  
            trial2_maxFinal = dict(zip(trial2_header, trial2_saved))
            self.transmit("Task2", trial2_maxFinal)
            print(trial2_maxFinal)

    def add_trial2_status(self, set_number, trial_number):
        if set_number == 1:
            self.title_1_current_trial = ttk.Label(self.trial2_exp_lf, text="Left "+" Trial "+ str(trial_number),font=("Calibri", 12, "bold"), bootstyle=WARNING)
        else:
            self.title_1_current_trial = ttk.Label(self.trial2_exp_lf, text="Right "+" Trial "+ str(trial_number),font=("Calibri", 12, "bold"), bootstyle=WARNING)
        self.title_1_current_trial.grid(row=self.trial2_row+1, column=1, padx=5, pady=5)

        if trial_number == 1:
            self.title_1_status_1 = ttk.Label(self.trial2_exp_lf, text="Low Medium High order",font=("Calibri", 12, "bold"), bootstyle=WARNING)
            self.title_1_status_1.grid(row=self.trial2_row+1, column=3, padx=5, pady=5)   

            self.title_1_status_2 = ttk.Label(self.trial2_exp_lf, text="6.0  6.5  7.0        ",font=("Calibri", 12, "bold"), bootstyle=WARNING)
            self.title_1_status_2.grid(row=self.trial2_row+2, column=3, padx=5, pady=5) 
        
        elif trial_number == 2:
            self.title_1_status_1 = ttk.Label(self.trial2_exp_lf, text="Medium High Low order",font=("Calibri", 12, "bold"), bootstyle=WARNING)
            self.title_1_status_1.grid(row=self.trial2_row+1, column=3, padx=5, pady=5)   

            self.title_1_status_2 = ttk.Label(self.trial2_exp_lf, text="6.5  7.0  7.5        ",font=("Calibri", 12, "bold"), bootstyle=WARNING)
            self.title_1_status_2.grid(row=self.trial2_row+2, column=3, padx=5, pady=5) 
        
        elif trial_number == 3:
            self.title_1_status_1 = ttk.Label(self.trial2_exp_lf, text="High Low Medium order",font=("Calibri", 12, "bold"), bootstyle=WARNING)
            self.title_1_status_1.grid(row=self.trial2_row+1, column=3, padx=5, pady=5)   

            self.title_1_status_2 = ttk.Label(self.trial2_exp_lf, text="7.0  7.5  8.0        ",font=("Calibri", 12, "bold"), bootstyle=WARNING)
            self.title_1_status_2.grid(row=self.trial2_row+2, column=3, padx=5, pady=5) 

        elif trial_number == 4:
            self.title_1_status_1 = ttk.Label(self.trial2_exp_lf, text="Low Medium High order",font=("Calibri", 12, "bold"), bootstyle=WARNING)
            self.title_1_status_1.grid(row=self.trial2_row+1, column=3, padx=5, pady=5)   

            self.title_1_status_2 = ttk.Label(self.trial2_exp_lf, text="7.5  8.0  8.5        ",font=("Calibri", 12, "bold"), bootstyle=WARNING)
            self.title_1_status_2.grid(row=self.trial2_row+2, column=3, padx=5, pady=5) 
        
        elif trial_number == 5:
            self.title_1_status_1 = ttk.Label(self.trial2_exp_lf, text="Medium High Low order",font=("Calibri", 12, "bold"), bootstyle=WARNING)
            self.title_1_status_1.grid(row=self.trial2_row+1, column=3, padx=5, pady=5)   

            self.title_1_status_2 = ttk.Label(self.trial2_exp_lf, text="8.0  8.5  9.0        ",font=("Calibri", 12, "bold"), bootstyle=WARNING)
            self.title_1_status_2.grid(row=self.trial2_row+2, column=3, padx=5, pady=5) 
        
        elif trial_number == 6:
            self.title_1_status_1 = ttk.Label(self.trial2_exp_lf, text="High Low Medium order",font=("Calibri", 12, "bold"), bootstyle=WARNING)
            self.title_1_status_1.grid(row=self.trial2_row+1, column=3, padx=5, pady=5)   

            self.title_1_status_2 = ttk.Label(self.trial2_exp_lf, text="8.5  9.0  9.5        ",font=("Calibri", 12, "bold"), bootstyle=WARNING)
            self.title_1_status_2.grid(row=self.trial2_row+2, column=3, padx=5, pady=5)

        elif trial_number == 7:
            self.title_1_status_1 = ttk.Label(self.trial2_exp_lf, text="Low Medium High order",font=("Calibri", 12, "bold"), bootstyle=WARNING)
            self.title_1_status_1.grid(row=self.trial2_row+1, column=3, padx=5, pady=5)   

            self.title_1_status_2 = ttk.Label(self.trial2_exp_lf, text="9.0  9.5  10.0        ",font=("Calibri", 12, "bold"), bootstyle=WARNING)
            self.title_1_status_2.grid(row=self.trial2_row+2, column=3, padx=5, pady=5) 
        
        elif trial_number == 8:
            self.title_1_status_1 = ttk.Label(self.trial2_exp_lf, text="Medium High Low order",font=("Calibri", 12, "bold"), bootstyle=WARNING)
            self.title_1_status_1.grid(row=self.trial2_row+1, column=3, padx=5, pady=5)   

            self.title_1_status_2 = ttk.Label(self.trial2_exp_lf, text="9.5  10.0  6.0        ",font=("Calibri", 12, "bold"), bootstyle=WARNING)
            self.title_1_status_2.grid(row=self.trial2_row+2, column=3, padx=5, pady=5) 
        
        elif trial_number == 9:
            self.title_1_status_1 = ttk.Label(self.trial2_exp_lf, text="High Low Medium order",font=("Calibri", 12, "bold"), bootstyle=WARNING)
            self.title_1_status_1.grid(row=self.trial2_row+1, column=3, padx=5, pady=5)   

            self.title_1_status_2 = ttk.Label(self.trial2_exp_lf, text="10.0  6.0  6.5        ",font=("Calibri", 12, "bold"), bootstyle=WARNING)
            self.title_1_status_2.grid(row=self.trial2_row+2, column=3, padx=5, pady=5)


        self.is_trial2_status = True

    def delete_trial2_label(self):
        if self.is_trial2_status:
            self.title_1_current_trial.grid_forget()
            self.title_1_status_1.grid_forget()
            self.title_1_status_2.grid_forget()

        self.is_trial2_status = False

    def trial2_stop(self):
        self.stop_bar = True
        self.trial_finish = True
        self.trial2_break = True
        self.min_value = 0
        self.title_2_fg.grid_forget()
        self.title_2_fg = ttk.Floodgauge(self.trial2_exp_lf, bootstyle=INFO, length=750, maximum=self.trial1_bar_max, font=("Calibri", 12, 'bold'),)
        self.title_2_fg.grid(row=self.trial2_row+8, column=0, columnspan=5, padx=5, pady=3)  
        self.title_2_fg['value'] = 0

    def start_trial2_bar(self, max):
        # start the progressive bar
        self.title_2_fg['maximum'] = max
        self.title_2_fg['value'] = 0

        # if bar has never been start 
        if self.has_started_bar and not self.trial_finish:
            self.min = self.min_value
        else:
            self.min = 0

        is_get_min = False

        for i in range(self.min, max):

            if self.stop_bar:
                self.title_2_fg['value'] = 0
                self.trial2_exp_lf.update()
                time.sleep(0.05)
            else:
                self.title_2_fg['value'] = i+1
                self.trial2_exp_lf.update()
                time.sleep(0.05) 
                
            if self.title_2_fg['value'] == max:
                self.trial_finish = True


    # ---------------------------------------functions in frame 3---------------------------------------
    def trial3_Start(self):
        self.pause_bar = False
        self.stop_bar = False
        # save the data
        trial3_saved = []

        trial3_header = []
        trial3_header.append('Experiment Mode')
        trial3_header.append('Experiment Status')

        # make sure all data has been input
        is_correct = True
        if self.checkFields_frame0():
            is_correct = False

        # if all data has been submitted correctly
        if is_correct:
            if self.trial3_start_StinngVar_1.get() == "Automatic" and self.trial3_start_StinngVar_2.get() == "Auto":
                self.trial3_break = False
                for set_count in range(1,3):
                    for trial_count in range(1,10):
                        if self.trial3_break:
                            break
                        if set_count == 1:
                            trial3_saved.append("Left")
                        else:
                            trial3_saved.append("Right")
                        
                        trial3_saved.append("Trial " + str(trial_count))
                        trial3_maxFinal = dict(zip(trial3_header, trial3_saved))
                        
                        if self.trial_finish or self.is_start_trial1:
                            self.transmit("Task3", trial3_maxFinal)
                            print(trial3_maxFinal)
                            self.is_start_trial3 = False
                            trial3_saved.pop()
                            trial3_saved.pop()

                        if trial_count == 1 or trial_count == 4 or trial_count == 7:
                            self.delete_trial3_label()
                            self.add_trial3_low()  

                        elif trial_count == 2 or trial_count == 5 or trial_count == 8:
                            self.delete_trial3_label()
                            self.add_trial3_medium()

                        elif trial_count == 3 or trial_count == 6 or trial_count == 9:
                            self.delete_trial3_label()
                            self.add_trial3_high()

                        # add label on the bar
                        self.add_trial3_status(set_count,trial_count) 

                        # start the progressive bar
                        self.start_trial3_bar(500)


            elif self.trial3_start_StinngVar_1.get()[0] != "A" and self.trial3_start_StinngVar_2.get()[0] != "A":
                trial3_saved.append(self.trial3_start_StinngVar_1.get())
                trial3_saved.append(self.trial3_start_StinngVar_2.get())

                trial3_maxFinal = dict(zip(trial3_header, trial3_saved))
                if self.trial_finish or self.is_start_trial3:
                    self.transmit("Task3", trial3_maxFinal)
                    self.is_start_trial3 = False
                    print(trial3_maxFinal)
                # delete the old bar
                trial_count = int(self.trial3_start_StinngVar_2.get()[6])

                if trial_count == 1 or trial_count == 4 or trial_count == 7:
                    self.delete_trial3_label()
                    self.add_trial3_low()  

                elif trial_count == 2 or trial_count == 5 or trial_count == 8:
                    self.delete_trial3_label()
                    self.add_trial3_medium()

                elif trial_count == 3 or trial_count == 6 or trial_count == 9:
                    self.delete_trial3_label()
                    self.add_trial3_high()

                if self.trial3_start_StinngVar_1.get() == "Left":
                    # add label on the bar
                    self.add_trial3_status(1,int(self.trial3_start_StinngVar_2.get()[6]))  
                else:
                    self.add_trial3_status(2,int(self.trial3_start_StinngVar_2.get()[6]))

                # start the progressive bar
                self.start_trial3_bar(500)      
            else:
                print("retrycancel: ",Messagebox.show_error(title='Oh no', message="Please choose correct task!"))   

    def add_trial3_status(self, set_number, trial_number):
        if set_number == 1:
            self.title_3_current_trial = ttk.Label(self.trial3_exp_lf, text="Left "+" Trial "+ str(trial_number),font=("Calibri", 12, "bold"), bootstyle=WARNING)
        else:
            self.title_3_current_trial = ttk.Label(self.trial3_exp_lf, text="Right "+" Trial "+ str(trial_number),font=("Calibri", 12, "bold"), bootstyle=WARNING)
        self.title_3_current_trial.grid(row=self.trial3_row+1, column=1, padx=5, pady=5)

        if trial_number == 1:
            self.title_3_status_1 = ttk.Label(self.trial3_exp_lf, text="Low Medium High order",font=("Calibri", 12, "bold"), bootstyle=WARNING)
            self.title_3_status_1.grid(row=self.trial3_row+1, column=3, padx=5, pady=5)   

            self.title_3_status_2 = ttk.Label(self.trial3_exp_lf, text="6.0  6.5  7.0        ",font=("Calibri", 12, "bold"), bootstyle=WARNING)
            self.title_3_status_2.grid(row=self.trial3_row+2, column=3, padx=5, pady=5) 
        
        elif trial_number == 2:
            self.title_3_status_1 = ttk.Label(self.trial3_exp_lf, text="Medium High Low order",font=("Calibri", 12, "bold"), bootstyle=WARNING)
            self.title_3_status_1.grid(row=self.trial3_row+1, column=3, padx=5, pady=5)   

            self.title_3_status_2 = ttk.Label(self.trial3_exp_lf, text="6.5  7.0  7.5        ",font=("Calibri", 12, "bold"), bootstyle=WARNING)
            self.title_3_status_2.grid(row=self.trial3_row+2, column=3, padx=5, pady=5) 
        
        elif trial_number == 3:
            self.title_3_status_1 = ttk.Label(self.trial3_exp_lf, text="High Low Medium order",font=("Calibri", 12, "bold"), bootstyle=WARNING)
            self.title_3_status_1.grid(row=self.trial3_row+1, column=3, padx=5, pady=5)   

            self.title_3_status_2 = ttk.Label(self.trial3_exp_lf, text="7.0  7.5  8.0        ",font=("Calibri", 12, "bold"), bootstyle=WARNING)
            self.title_3_status_2.grid(row=self.trial3_row+2, column=3, padx=5, pady=5) 

        elif trial_number == 4:
            self.title_3_status_1 = ttk.Label(self.trial3_exp_lf, text="Low Medium High order",font=("Calibri", 12, "bold"), bootstyle=WARNING)
            self.title_3_status_1.grid(row=self.trial3_row+1, column=3, padx=5, pady=5)   

            self.title_3_status_2 = ttk.Label(self.trial3_exp_lf, text="7.5  8.0  8.5        ",font=("Calibri", 12, "bold"), bootstyle=WARNING)
            self.title_3_status_2.grid(row=self.trial3_row+2, column=3, padx=5, pady=5) 
        
        elif trial_number == 5:
            self.title_3_status_1 = ttk.Label(self.trial3_exp_lf, text="Medium High Low order",font=("Calibri", 12, "bold"), bootstyle=WARNING)
            self.title_3_status_1.grid(row=self.trial3_row+1, column=3, padx=5, pady=5)   

            self.title_3_status_2 = ttk.Label(self.trial3_exp_lf, text="8.0  8.5  9.0        ",font=("Calibri", 12, "bold"), bootstyle=WARNING)
            self.title_3_status_2.grid(row=self.trial3_row+2, column=3, padx=5, pady=5) 
        
        elif trial_number == 6:
            self.title_3_status_1 = ttk.Label(self.trial3_exp_lf, text="High Low Medium order",font=("Calibri", 12, "bold"), bootstyle=WARNING)
            self.title_3_status_1.grid(row=self.trial3_row+1, column=3, padx=5, pady=5)   

            self.title_3_status_2 = ttk.Label(self.trial3_exp_lf, text="8.5  9.0  9.5        ",font=("Calibri", 12, "bold"), bootstyle=WARNING)
            self.title_3_status_2.grid(row=self.trial3_row+2, column=3, padx=5, pady=5)

        elif trial_number == 7:
            self.title_3_status_1 = ttk.Label(self.trial3_exp_lf, text="Low Medium High order",font=("Calibri", 12, "bold"), bootstyle=WARNING)
            self.title_3_status_1.grid(row=self.trial3_row+1, column=3, padx=5, pady=5)   

            self.title_3_status_2 = ttk.Label(self.trial3_exp_lf, text="9.0  9.5  10.0        ",font=("Calibri", 12, "bold"), bootstyle=WARNING)
            self.title_3_status_2.grid(row=self.trial3_row+2, column=3, padx=5, pady=5) 
        
        elif trial_number == 8:
            self.title_3_status_1 = ttk.Label(self.trial3_exp_lf, text="Medium High Low order",font=("Calibri", 12, "bold"), bootstyle=WARNING)
            self.title_3_status_1.grid(row=self.trial3_row+1, column=3, padx=5, pady=5)   

            self.title_3_status_2 = ttk.Label(self.trial3_exp_lf, text="9.5  10.0  6.0        ",font=("Calibri", 12, "bold"), bootstyle=WARNING)
            self.title_3_status_2.grid(row=self.trial3_row+2, column=3, padx=5, pady=5) 
        
        elif trial_number == 9:
            self.title_3_status_1 = ttk.Label(self.trial3_exp_lf, text="High Low Medium order",font=("Calibri", 12, "bold"), bootstyle=WARNING)
            self.title_3_status_1.grid(row=self.trial3_row+1, column=3, padx=5, pady=5)   

            self.title_3_status_2 = ttk.Label(self.trial3_exp_lf, text="10.0  6.0  6.5        ",font=("Calibri", 12, "bold"), bootstyle=WARNING)
            self.title_3_status_2.grid(row=self.trial3_row+2, column=3, padx=5, pady=5)


        self.is_trial3_status = True

    def delete_trial3_label(self):
        if self.is_trial3_status:
            self.title_3_current_trial.grid_forget()
            self.title_3_status_1.grid_forget()
            self.title_3_status_2.grid_forget()

        self.is_trial3_status = False

    def trial3_stop(self):
        self.stop_bar = True
        self.trial_finish = True
        self.trial3_break = True
        self.min_value = 0
        self.title_3_fg.grid_forget()
        self.title_3_fg = ttk.Floodgauge(self.trial3_exp_lf, bootstyle=INFO, length=750, maximum=self.trial1_bar_max, font=("Calibri", 12, 'bold'),)
        self.title_3_fg.grid(row=self.trial3_row+8, column=0, columnspan=5, padx=5, pady=3)  
        self.title_3_fg['value'] = 0

    def start_trial3_bar(self, max):
        # start the progressive bar
        self.title_3_fg['maximum'] = max
        self.title_3_fg['value'] = 0

        # if bar has never been start 
        if self.has_started_bar and not self.trial_finish:
            self.min = self.min_value
        else:
            self.min = 0

        is_get_min = False

        for i in range(self.min, max):

            if self.stop_bar:
                self.title_3_fg['value'] = 0
                self.trial3_exp_lf.update()
                time.sleep(0.05)
            else:
                self.title_3_fg['value'] = i+1
                self.trial3_exp_lf.update()
                time.sleep(0.05) 
                
            if self.title_3_fg['value'] == max:
                self.trial_finish = True
                if self.trial3_start_StinngVar_1.get() != "Automatic":
                    self.trial3_stop()


    def add_trial3_low(self):
        self.trial3_start_pos = self.calculate_bar("trial3_low")

        self.trial3_low_1 = ttk.Label(self.frame3, text="| Start ",font=("Calibri", 10, "bold"))
        self.trial3_low_1.place(x=self.trial3_start_pos[0],y=605)  

        self.trial3_low_2 = ttk.Label(self.frame3, text="| low ",font=("Calibri", 10, "bold"))
        self.trial3_low_2.place(x=self.trial3_start_pos[1],y=605) 

        self.trial3_low_3 = ttk.Label(self.frame3, text="| relax ",font=("Calibri", 10, "bold"))
        self.trial3_low_3.place(x=self.trial3_start_pos[2],y=605) 

        self.trial3_low_4 = ttk.Label(self.frame3, text="| medium ",font=("Calibri", 10, "bold"))
        self.trial3_low_4.place(x=self.trial3_start_pos[3],y=605) 

        self.trial3_low_5 = ttk.Label(self.frame3, text="| relax ",font=("Calibri", 10, "bold"))
        self.trial3_low_5.place(x=self.trial3_start_pos[4],y=605) 

        self.trial3_low_6 = ttk.Label(self.frame3, text="| high ",font=("Calibri", 10, "bold"))
        self.trial3_low_6.place(x=self.trial3_start_pos[5],y=605) 

        self.trial3_low_7 = ttk.Label(self.frame3, text="| relax ",font=("Calibri", 10, "bold"))
        self.trial3_low_7.place(x=self.trial3_start_pos[6],y=605) 

        self.is_trial3_low = True

    def delete_trial3_low(self):
        self.trial3_low_1.place_forget()
        self.trial3_low_2.place_forget()
        self.trial3_low_3.place_forget()
        self.trial3_low_4.place_forget()
        self.trial3_low_5.place_forget()
        self.trial3_low_6.place_forget()
        self.trial3_low_7.place_forget()

        self.is_trial3_low = False

    def add_trial3_medium(self):
        self.trial3_start_pos = self.calculate_bar("trial3_medium")

        self.trial3_medium_1 = ttk.Label(self.frame3, text="| Start ",font=("Calibri", 10, "bold"))
        self.trial3_medium_1.place(x=self.trial3_start_pos[0],y=605)  

        self.trial3_medium_2 = ttk.Label(self.frame3, text="| medium ",font=("Calibri", 10, "bold"))
        self.trial3_medium_2.place(x=self.trial3_start_pos[1],y=605) 

        self.trial3_medium_3 = ttk.Label(self.frame3, text="| relax ",font=("Calibri", 10, "bold"))
        self.trial3_medium_3.place(x=self.trial3_start_pos[2],y=605) 

        self.trial3_medium_4 = ttk.Label(self.frame3, text="| high ",font=("Calibri", 10, "bold"))
        self.trial3_medium_4.place(x=self.trial3_start_pos[3],y=605) 

        self.trial3_medium_5 = ttk.Label(self.frame3, text="| relax ",font=("Calibri", 10, "bold"))
        self.trial3_medium_5.place(x=self.trial3_start_pos[4],y=605) 

        self.trial3_medium_6 = ttk.Label(self.frame3, text="| low ",font=("Calibri", 10, "bold"))
        self.trial3_medium_6.place(x=self.trial3_start_pos[5],y=605) 

        self.trial3_medium_7 = ttk.Label(self.frame3, text="| relax ",font=("Calibri", 10, "bold"))
        self.trial3_medium_7.place(x=self.trial3_start_pos[6],y=605) 

        self.is_trial3_medium = True
    
    def delete_trial3_medium(self):
        self.trial3_medium_1.place_forget()
        self.trial3_medium_2.place_forget()
        self.trial3_medium_3.place_forget()
        self.trial3_medium_4.place_forget()
        self.trial3_medium_5.place_forget()
        self.trial3_medium_6.place_forget()
        self.trial3_medium_7.place_forget()

        self.is_trial3_medium = False

    def add_trial3_high(self):
        self.trial3_start_pos = self.calculate_bar("trial3_high")

        self.trial3_high_1 = ttk.Label(self.frame3, text="| Start ",font=("Calibri", 10, "bold"))
        self.trial3_high_1.place(x=self.trial3_start_pos[0],y=605)  

        self.trial3_high_2 = ttk.Label(self.frame3, text="| high ",font=("Calibri", 10, "bold"))
        self.trial3_high_2.place(x=self.trial3_start_pos[1],y=605) 

        self.trial3_high_3 = ttk.Label(self.frame3, text="| relax ",font=("Calibri", 10, "bold"))
        self.trial3_high_3.place(x=self.trial3_start_pos[2],y=605) 

        self.trial3_high_4 = ttk.Label(self.frame3, text="| low ",font=("Calibri", 10, "bold"))
        self.trial3_high_4.place(x=self.trial3_start_pos[3],y=605) 

        self.trial3_high_5 = ttk.Label(self.frame3, text="| relax ",font=("Calibri", 10, "bold"))
        self.trial3_high_5.place(x=self.trial3_start_pos[4],y=605) 

        self.trial3_high_6 = ttk.Label(self.frame3, text="| medium ",font=("Calibri", 10, "bold"))
        self.trial3_high_6.place(x=self.trial3_start_pos[5],y=605) 

        self.trial3_high_7 = ttk.Label(self.frame3, text="| relax ",font=("Calibri", 10, "bold"))
        self.trial3_high_7.place(x=self.trial3_start_pos[6],y=605) 

        self.is_trial3_high = True
    
    def delete_trial3_high(self):
        self.trial3_high_1.place_forget()
        self.trial3_high_2.place_forget()
        self.trial3_high_3.place_forget()
        self.trial3_high_4.place_forget()
        self.trial3_high_5.place_forget()
        self.trial3_high_6.place_forget()
        self.trial3_high_7.place_forget()

        self.is_trial3_high = False

    def delete_trial3_label(self):
        if self.is_trial3_low:
            self.delete_trial3_low()
        elif self.is_trial3_medium:
            self.delete_trial3_medium()
        elif self.is_trial3_high:
            self.delete_trial3_high()




def launchGUI(conn, in_conn):
    # run the GUI
    root = ttk.Window(
            title="Torque GUI",        
            themename="litera",     
            size=(1100,800),        
            position=(100,100),     
            minsize=(0,0),         
            maxsize=(1100,800),    
            resizable=None,         
            alpha=1.0,              
    )
    gui = GUI(root, conn, in_conn)
    root.mainloop()
    exit()


if __name__=='__main__':
    launchGUI(conn=Queue(),in_conn=Queue())
    pass
