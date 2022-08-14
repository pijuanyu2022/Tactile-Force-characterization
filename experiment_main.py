from cmath import pi
from multiprocessing import Process, Queue
from data_intake import data_sender
from Saver import data_saver
from GUI import launchGUI as gui_run
from dataclasses import dataclass, field
from typing import List
from collections import deque
from plotter import animation_control
from threading import Timer
import numpy as np
from numpy import *
import math


@dataclass
class MainExperiment:
    # Experimental state and control
    experiment_mode: str = "DEFAULT"
    mode_state: str = "DEFAULT"
    current_trial: str = "Prepare"
    current_status: str = "Prepare"
    task: str = "Prepare"
    mode_status: str = "Prepare"

    # pressure
    pressure_value: float = 1
    solenoid_value: int = 0

    target_pressure: float = 1
    target_solenoid: int = 0

    Fx: float = 1.0
    Fy: float = 1.0
    Fz: float = 1.0
    Mx: float = 1.0
    My: float = 1.0
    Mz: float = 1.0


    # Info about the participants
    subject_number: float = 0
    participant_age: float = 0
    participant_gender: str = "UNSPECIFIED"
    participant_years_since_stroke: int = 0
    participant_dominant_arm: str = "RIGHT"
    participant_paretic_arm: str = "NONE"
    participant_diabetes: str = "NO"
    
    shoulder_aduction_angle: float = 0
    elbow_flexion_angle: float = 0
    arm_length: float = 0
    midloadcell_to_elbowjoint: float = 0

    subject_type: str = "UNSPECIFIED"

    timestep: float = 0



def main():
    # Emonitor section, delegating the subprocess and connection
    QUEUES = []
    # Process and queues for the GUI

    gui_queue = Queue()
    gui_out_queue = Queue()
    QUEUES.append(gui_queue)
    QUEUES.append(gui_out_queue)

    gui_p = Process(target=gui_run, args=(gui_queue, gui_out_queue))
    gui_p.start()

    # Initialize data collection
    HZ = 100

    data_intake_queue = Queue()
    data_intake_comm_queue = Queue()
    QUEUES.append(data_intake_queue)
    QUEUES.append(data_intake_comm_queue)
    data_intake_p = Process(
        target=data_sender, args=(1 / HZ, data_intake_queue, data_intake_comm_queue)
    )
    data_intake_p.start()

    # Initialize plotting
    plotting_comm_queue = Queue()
    QUEUES.append(plotting_comm_queue)
    plotting_p = Process(target=animation_control, args=(plotting_comm_queue,))
    plotting_p.start()

    # Initialize the experiment dataclass
    experiment = MainExperiment()
    
    data_buffer = deque()

    is_saved_folder = False
    is_saved = False
    is_saved_folder = False

    is_saved_data = True
    is_saved_trial1 = True
    is_saved_trial2 = True
    is_saved_trial3 = True

    is_ending_trial1 = False
    is_ending_trial2 = False
    is_ending_trial3 = False
    running = True

    while running:

        data = None

        while not data_intake_queue.empty():
            data_seq = data_intake_queue.get()
            for point in data_seq:
                data_buffer.append(point)

        if data_buffer:
            data = data_buffer.popleft()
            experiment.Fz, experiment.Fy, experiment.Fx, experiment.Mz, experiment.My, experiment.Mx, experiment.solenoid_value, experiment.pressure_value, experiment.timestep= data

        # Get the data from the remote controls
        while not gui_queue.empty():
            header, gui_data = gui_queue.get()

            if header == "Task0_save":
                experiment.task = "Task0_save"
                # Subject information
                experiment.subject_number = gui_data["Subject Number"]
                experiment.participant_age = gui_data["Age"]
                experiment.subject_type = gui_data["Subject Type"]
                experiment.participant_gender = gui_data["Gender"]
                experiment.participant_diabetes = gui_data["Diabetes"]
                experiment.participant_years_since_stroke = gui_data["Years since Stroke"]
                experiment.participant_dominant_arm = gui_data["Dominant Arm"]
                experiment.participant_paretic_arm = gui_data["Testing Arm"]

                # save the data
                is_saved_folder = True
                if int(experiment.subject_number) < 10:
                    subject_saver = data_saver(experiment.subject_type+"0"+str(int(experiment.subject_number))+"/")
                elif int(experiment.subject_number) < 0 and int(experiment.subject_number) > 99:
                    print("It is an Error")
                else:
                    subject_saver = data_saver(experiment.subject_type+"0"+str(int(experiment.subject_number))+"/")

                subject_saver.add_header(
                    [
                        "Subject Number",
                        "Age",
                        "Gender",
                        "Subject Type",
                        "Diabetes",
                        "Years since Stroke",
                        "Dominant Arm",
                        "Testing Arm",
                    ]
                )   

                # add data in the subject file
                subject_saver.add_data(
                    [
                        experiment.subject_number,
                        experiment.participant_age,
                        experiment.participant_gender,
                        experiment.subject_type,
                        experiment.participant_diabetes,
                        experiment.participant_years_since_stroke,
                        experiment.participant_dominant_arm,
                        experiment.participant_paretic_arm,
                        experiment.shoulder_aduction_angle,
                        experiment.elbow_flexion_angle,
                        experiment.arm_length,
                        experiment.midloadcell_to_elbowjoint
                    ]
                )
                subject_saver.save_data("Subject_Information", "Sub")
                subject_saver.clear()

                # Create 2 files to save data for 2 tasks
                saver_trial0 = data_saver(experiment.subject_type+"0"+str(int(experiment.subject_number))+"/")
                saver_trial1 = data_saver(experiment.subject_type+"0"+str(int(experiment.subject_number))+"/")
                saver_trial2 = data_saver(experiment.subject_type+"0"+str(int(experiment.subject_number))+"/")
                saver_trial3 = data_saver(experiment.subject_type+"0"+str(int(experiment.subject_number))+"/")

                saver_matrix = [saver_trial0, saver_trial1, saver_trial2, saver_trial3]
                for i in range(4):
                    saver_matrix[i].add_header(
                        [
                            "Time",
                            "Pressure value",
                            "Fz (N)",
                            "Fy (N)",
                            "Fx (N)",
                            "Mz (Nm)",
                            "My (Nm)",
                            "Mx (Nm)",
                        ]
                    )

            elif header == "Task0_control":
                # At present, the task is Trial 0_control, it will be used to control the device manually
                experiment.task = "Task0_control"

                # set the target pressure value and the solenoid data
                experiment.target_pressure = gui_data["Pressure regulator value"]
                experiment.target_solenoid = gui_data["Solenoid value"]

            elif header == "Task1":
                # At present, the task is Trial 1 MAX Measurement
                experiment.task = "Task1"

                # get the experiment mode Left Right
                experiment.mode_state = gui_data["Experiment Mode"]

                # get the start time when the trial 1 is starting
                initial_time_trial1 = experiment.timestep

                # if the data in trial 1 has been saved, then delete the old data
                if is_saved_trial1:
                    saver_trial1.clear()
                
                is_saved_trial1 = False

            elif header == "Task2":
                # At present, the task is Trial 2 MAX Measurement
                experiment.task = "Task2"

                # get the experiment mode Left Right
                experiment.mode_state = gui_data["Experiment Mode"]

                # get the start time when the trial 1 is starting
                initial_time_trial2 = experiment.timestep

                # if the data in trial 1 has been saved, then delete the old data
                if is_saved_trial2:
                    saver_trial2.clear()
                
                is_saved_trial2 = False

            elif header == "Task3":
                experiment.task = "Task3"

                # Mode: Automatic, Up direction, In direction, Up and In direction
                experiment.mode_state = gui_data["Experiment Mode"]

                experiment.mode_status = gui_data["Experiment Status"]

                # get the start time when the trial 2 is starting
                initial_time_trial3 = experiment.timestep

                if is_saved_trial3:
                    saver_trial3.clear()
                
                is_saved_trial3 = False
            
            elif header == "Save_data":
                experiment.task = "Save_data"

                is_saved_data = False

            elif header == "Stop":
                experiment.task = "Stop"

            elif header == "Close":
                gui_p.terminate()
                running = False

        if not data:
            continue

        # start to save the data
        if is_saved_folder:
            for i in range(4):
                saver_matrix[i].add_data(
                    [
                        experiment.timestep,
                        experiment.pressure_value,
                        experiment.Fz,
                        experiment.Fy,
                        experiment.Fx,
                        experiment.Mz,
                        experiment.My,
                        experiment.Mx,
                    ]
                )
        
        if experiment.task == "Task0_control":
            data_intake_comm_queue.put(experiment.target_pressure)
            data_intake_comm_queue.put(experiment.target_solenoid)
        
        if experiment.task == "Save_data":
            if is_saved_data == False:
                saver_trial0.save_data("Characterization", "Pressure Characterization")
                is_saved_data = True
        # -------- ------------------------------------------------Trial Type 1: MAX Measurement-------------------------------------------------
        if experiment.task == "Task1":
            
            # 1: retract
            # 0: pop
            # get the time in the trail 1
            trial1_time = experiment.timestep - initial_time_trial1
            
            print(trial1_time)

            time_duration = 2

            if trial1_time < 0.5:
                data_intake_comm_queue.put(3100)
            elif trial1_time > 0.5 and trial1_time <= 0.5+time_duration*1:
                data_intake_comm_queue.put(1)
            elif trial1_time > 0.5+time_duration*1 and trial1_time <= 0.5+time_duration*2:
                data_intake_comm_queue.put(0)
            elif trial1_time > 0.5+time_duration*2 and trial1_time <= 0.5+time_duration*3:
                data_intake_comm_queue.put(1)
            elif trial1_time > 0.5+time_duration*3 and trial1_time <= 0.5+time_duration*4:
                data_intake_comm_queue.put(0)
            elif trial1_time > 0.5+time_duration*4 and trial1_time <= 0.5+time_duration*5:
                data_intake_comm_queue.put(1)
            elif trial1_time > 0.5+time_duration*5 and trial1_time <= 0.5+time_duration*6:
                data_intake_comm_queue.put(0)
            elif trial1_time > 0.5+time_duration*6 and trial1_time <= 0.5+time_duration*7:
                data_intake_comm_queue.put(1)
            elif trial1_time > 0.5+time_duration*7 and trial1_time <= 0.5+time_duration*8:
                data_intake_comm_queue.put(0)
            elif trial1_time > 0.5+time_duration*8 and trial1_time <= 0.5+time_duration*9:
                data_intake_comm_queue.put(1)
            elif trial1_time > 0.5+time_duration*9 and trial1_time <= 0.5+time_duration*10:
                data_intake_comm_queue.put(0)
            elif trial1_time > 0.5+time_duration*10 and trial1_time <= 0.5+time_duration*11:
                data_intake_comm_queue.put(1)
            elif trial1_time > 0.5+time_duration*11 and trial1_time <= 0.5+time_duration*12:
                data_intake_comm_queue.put(0)
            elif trial1_time > 0.5+time_duration*12 and trial1_time <= 0.5+time_duration*13:
                data_intake_comm_queue.put(1)
            elif trial1_time > 0.5+time_duration*13 and trial1_time <= 0.5+time_duration*14:
                data_intake_comm_queue.put(0)
            elif trial1_time > 0.5+time_duration*14 and trial1_time <= 0.5+time_duration*15:
                data_intake_comm_queue.put(1)
            elif trial1_time > 0.5+time_duration*15 and trial1_time <= 0.5+time_duration*16:
                data_intake_comm_queue.put(0)
            elif trial1_time > 0.5+time_duration*16 and trial1_time <= 0.5+time_duration*17:
                data_intake_comm_queue.put(1)
            elif trial1_time > 0.5+time_duration*17 and trial1_time <= 0.5+time_duration*18:
                data_intake_comm_queue.put(0)
            elif trial1_time > 0.5+time_duration*18 and trial1_time <= 0.5+time_duration*19:
                data_intake_comm_queue.put(1)
                is_ending_trial1 = True
            
            if is_ending_trial1 and is_saved_trial1 == False:
                    saver_trial1.save_data("Anatomical Localiation Scan", experiment.mode_state)
                    is_saved_trial1 = True
        # --------------------------------------------------------Trial Type 2: Pre Experiment-------------------------------------------------
        if experiment.task == "Task2":
            task2_time = experiment.timestep - initial_time_trial2
            data_intake_comm_queue.put(experiment.target_pressure)
            data_intake_comm_queue.put(experiment.target_solenoid)


        # --------------------------------------------------------Trial Type 3: Stimulation Task-------------------------------------------------
        if experiment.task == "Task3":
            task3_time = experiment.timestep - initial_time_trial3

            if experiment.mode_status == "Trial 1":
                # low medium high
                # 6.0 6.5 7.0
                
                pressure_change_1 = 0.5
                out_1 = pressure_change_1 + 2.0
                relax_1 = out_1 + 6.0

                pressure_change_2 = relax_1 + 0.5
                out_2 = pressure_change_2 + 2.0
                relax_2 = out_2 + 6.5

                pressure_change_3 = relax_2 + 0.5
                out_3 = pressure_change_3 + 2.0
                relax_3 = out_3 + 7.0

                if task3_time < pressure_change_1:
                    data_intake_comm_queue.put(2300)
                elif task3_time >= pressure_change_1 and task3_time <= out_1:
                    data_intake_comm_queue.put(0)
                elif task3_time >= out_1 and task3_time <= relax_1:
                    data_intake_comm_queue.put(1)


                elif task3_time >= relax_1 and task3_time <= pressure_change_2:
                    data_intake_comm_queue.put(2700)
                elif task3_time >= pressure_change_2 and task3_time <= out_2:
                    data_intake_comm_queue.put(0)
                elif task3_time >= out_2 and task3_time <= relax_2:
                    data_intake_comm_queue.put(1)
                
                elif task3_time >= relax_2 and task3_time <= pressure_change_3:
                    data_intake_comm_queue.put(3100)
                elif task3_time >= pressure_change_3 and task3_time <= out_3:
                    data_intake_comm_queue.put(0)
                elif task3_time >= out_3 and task3_time <= relax_3:
                    data_intake_comm_queue.put(1)
                
                elif task3_time >= relax_3:
                    is_ending_trial3 = True
            
            elif experiment.mode_status == "Trial 2":
                # medium high low 
                # 6.5 7.0 7.5
                
                pressure_change_1 = 0.5
                out_1 = pressure_change_1 + 2.0
                relax_1 = out_1 + 6.5

                pressure_change_2 = relax_1 + 0.5
                out_2 = pressure_change_2 + 2.0
                relax_2 = out_2 + 7.0

                pressure_change_3 = relax_2 + 0.5
                out_3 = pressure_change_3 + 2.0
                relax_3 = out_3 + 7.5

                if task3_time < pressure_change_1:
                    data_intake_comm_queue.put(2700)
                elif task3_time >= pressure_change_1 and task3_time <= out_1:
                    data_intake_comm_queue.put(0)
                elif task3_time >= out_1 and task3_time <= relax_1:
                    data_intake_comm_queue.put(1)


                elif task3_time >= relax_1 and task3_time <= pressure_change_2:
                    data_intake_comm_queue.put(3100)
                elif task3_time >= pressure_change_2 and task3_time <= out_2:
                    data_intake_comm_queue.put(0)
                elif task3_time >= out_2 and task3_time <= relax_2:
                    data_intake_comm_queue.put(1)
                
                elif task3_time >= relax_2 and task3_time <= pressure_change_3:
                    data_intake_comm_queue.put(2300)
                elif task3_time >= pressure_change_3 and task3_time <= out_3:
                    data_intake_comm_queue.put(0)
                elif task3_time >= out_3 and task3_time <= relax_3:
                    data_intake_comm_queue.put(1)
                
                elif task3_time >= relax_3:
                    is_ending_trial3 = True

            elif experiment.mode_status == "Trial 3":
                # high low medium
                # 7.0 7.5 8.0
                
                pressure_change_1 = 0.5
                out_1 = pressure_change_1 + 2.0
                relax_1 = out_1 + 7.0

                pressure_change_2 = relax_1 + 0.5
                out_2 = pressure_change_2 + 2.0
                relax_2 = out_2 + 7.5

                pressure_change_3 = relax_2 + 0.5
                out_3 = pressure_change_3 + 2.0
                relax_3 = out_3 + 8.0

                if task3_time < pressure_change_1:
                    data_intake_comm_queue.put(3100)
                elif task3_time >= pressure_change_1 and task3_time <= out_1:
                    data_intake_comm_queue.put(0)
                elif task3_time >= out_1 and task3_time <= relax_1:
                    data_intake_comm_queue.put(1)


                elif task3_time >= relax_1 and task3_time <= pressure_change_2:
                    data_intake_comm_queue.put(2300)
                elif task3_time >= pressure_change_2 and task3_time <= out_2:
                    data_intake_comm_queue.put(0)
                elif task3_time >= out_2 and task3_time <= relax_2:
                    data_intake_comm_queue.put(1)
                
                elif task3_time >= relax_2 and task3_time <= pressure_change_3:
                    data_intake_comm_queue.put(2700)
                elif task3_time >= pressure_change_3 and task3_time <= out_3:
                    data_intake_comm_queue.put(0)
                elif task3_time >= out_3 and task3_time <= relax_3:
                    data_intake_comm_queue.put(1)
                
                elif task3_time >= relax_3:
                    is_ending_trial3 = True
            
            elif experiment.mode_status == "Trial 4":
                # low medium high
                # 7.5 8.0 8.5
                
                pressure_change_1 = 0.5
                out_1 = pressure_change_1 + 2.0
                relax_1 = out_1 + 7.5

                pressure_change_2 = relax_1 + 0.5
                out_2 = pressure_change_2 + 2.0
                relax_2 = out_2 + 8.0

                pressure_change_3 = relax_2 + 0.5
                out_3 = pressure_change_3 + 2.0
                relax_3 = out_3 + 8.5

                if task3_time < pressure_change_1:
                    data_intake_comm_queue.put(2300)
                elif task3_time >= pressure_change_1 and task3_time <= out_1:
                    data_intake_comm_queue.put(0)
                elif task3_time >= out_1 and task3_time <= relax_1:
                    data_intake_comm_queue.put(1)


                elif task3_time >= relax_1 and task3_time <= pressure_change_2:
                    data_intake_comm_queue.put(2700)
                elif task3_time >= pressure_change_2 and task3_time <= out_2:
                    data_intake_comm_queue.put(0)
                elif task3_time >= out_2 and task3_time <= relax_2:
                    data_intake_comm_queue.put(1)
                
                elif task3_time >= relax_2 and task3_time <= pressure_change_3:
                    data_intake_comm_queue.put(3100)
                elif task3_time >= pressure_change_3 and task3_time <= out_3:
                    data_intake_comm_queue.put(0)
                elif task3_time >= out_3 and task3_time <= relax_3:
                    data_intake_comm_queue.put(1)
                
                elif task3_time >= relax_3:
                    is_ending_trial3 = True

            elif experiment.mode_status == "Trial 5":
                # medium high low
                # 8.0 8.5 9.0
                
                pressure_change_1 = 0.5
                out_1 = pressure_change_1 + 2.0
                relax_1 = out_1 + 8.0

                pressure_change_2 = relax_1 + 0.5
                out_2 = pressure_change_2 + 2.0
                relax_2 = out_2 + 8.5

                pressure_change_3 = relax_2 + 0.5
                out_3 = pressure_change_3 + 2.0
                relax_3 = out_3 + 9.0

                if task3_time < pressure_change_1:
                    data_intake_comm_queue.put(2700)
                elif task3_time >= pressure_change_1 and task3_time <= out_1:
                    data_intake_comm_queue.put(0)
                elif task3_time >= out_1 and task3_time <= relax_1:
                    data_intake_comm_queue.put(1)


                elif task3_time >= relax_1 and task3_time <= pressure_change_2:
                    data_intake_comm_queue.put(3100)
                elif task3_time >= pressure_change_2 and task3_time <= out_2:
                    data_intake_comm_queue.put(0)
                elif task3_time >= out_2 and task3_time <= relax_2:
                    data_intake_comm_queue.put(1)
                
                elif task3_time >= relax_2 and task3_time <= pressure_change_3:
                    data_intake_comm_queue.put(2300)
                elif task3_time >= pressure_change_3 and task3_time <= out_3:
                    data_intake_comm_queue.put(0)
                elif task3_time >= out_3 and task3_time <= relax_3:
                    data_intake_comm_queue.put(1)
                
                elif task3_time >= relax_3:
                    is_ending_trial3 = True
            
            elif experiment.mode_status == "Trial 6":
                # high low medium
                # 8.5 9.0 9.5
                
                pressure_change_1 = 0.5
                out_1 = pressure_change_1 + 2.0
                relax_1 = out_1 + 8.5

                pressure_change_2 = relax_1 + 0.5
                out_2 = pressure_change_2 + 2.0
                relax_2 = out_2 + 9.0

                pressure_change_3 = relax_2 + 0.5
                out_3 = pressure_change_3 + 2.0
                relax_3 = out_3 + 9.5

                if task3_time < pressure_change_1:
                    data_intake_comm_queue.put(3100)
                elif task3_time >= pressure_change_1 and task3_time <= out_1:
                    data_intake_comm_queue.put(0)
                elif task3_time >= out_1 and task3_time <= relax_1:
                    data_intake_comm_queue.put(1)


                elif task3_time >= relax_1 and task3_time <= pressure_change_2:
                    data_intake_comm_queue.put(2300)
                elif task3_time >= pressure_change_2 and task3_time <= out_2:
                    data_intake_comm_queue.put(0)
                elif task3_time >= out_2 and task3_time <= relax_2:
                    data_intake_comm_queue.put(1)
                
                elif task3_time >= relax_2 and task3_time <= pressure_change_3:
                    data_intake_comm_queue.put(2700)
                elif task3_time >= pressure_change_3 and task3_time <= out_3:
                    data_intake_comm_queue.put(0)
                elif task3_time >= out_3 and task3_time <= relax_3:
                    data_intake_comm_queue.put(1)
                
                elif task3_time >= relax_3:
                    is_ending_trial3 = True
            
            elif experiment.mode_status == "Trial 7":
                # low medium high
                # 9.0 9.5 10.0
                
                pressure_change_1 = 0.5
                out_1 = pressure_change_1 + 2.0
                relax_1 = out_1 + 9.0

                pressure_change_2 = relax_1 + 0.5
                out_2 = pressure_change_2 + 2.0
                relax_2 = out_2 + 9.5

                pressure_change_3 = relax_2 + 0.5
                out_3 = pressure_change_3 + 2.0
                relax_3 = out_3 + 10.0

                if task3_time < pressure_change_1:
                    data_intake_comm_queue.put(2300)
                elif task3_time >= pressure_change_1 and task3_time <= out_1:
                    data_intake_comm_queue.put(0)
                elif task3_time >= out_1 and task3_time <= relax_1:
                    data_intake_comm_queue.put(1)


                elif task3_time >= relax_1 and task3_time <= pressure_change_2:
                    data_intake_comm_queue.put(2700)
                elif task3_time >= pressure_change_2 and task3_time <= out_2:
                    data_intake_comm_queue.put(0)
                elif task3_time >= out_2 and task3_time <= relax_2:
                    data_intake_comm_queue.put(1)
                
                elif task3_time >= relax_2 and task3_time <= pressure_change_3:
                    data_intake_comm_queue.put(3100)
                elif task3_time >= pressure_change_3 and task3_time <= out_3:
                    data_intake_comm_queue.put(0)
                elif task3_time >= out_3 and task3_time <= relax_3:
                    data_intake_comm_queue.put(1)
                
                elif task3_time >= relax_3:
                    is_ending_trial3 = True
            
            elif experiment.mode_status == "Trial 8":
                # medium high low
                # 9.5 10.0 6.0
                
                pressure_change_1 = 0.5
                out_1 = pressure_change_1 + 2.0
                relax_1 = out_1 + 9.5

                pressure_change_2 = relax_1 + 0.5
                out_2 = pressure_change_2 + 2.0
                relax_2 = out_2 + 10.0

                pressure_change_3 = relax_2 + 0.5
                out_3 = pressure_change_3 + 2.0
                relax_3 = out_3 + 6.0

                if task3_time < pressure_change_1:
                    data_intake_comm_queue.put(2700)
                elif task3_time >= pressure_change_1 and task3_time <= out_1:
                    data_intake_comm_queue.put(0)
                elif task3_time >= out_1 and task3_time <= relax_1:
                    data_intake_comm_queue.put(1)


                elif task3_time >= relax_1 and task3_time <= pressure_change_2:
                    data_intake_comm_queue.put(3100)
                elif task3_time >= pressure_change_2 and task3_time <= out_2:
                    data_intake_comm_queue.put(0)
                elif task3_time >= out_2 and task3_time <= relax_2:
                    data_intake_comm_queue.put(1)
                
                elif task3_time >= relax_2 and task3_time <= pressure_change_3:
                    data_intake_comm_queue.put(2300)
                elif task3_time >= pressure_change_3 and task3_time <= out_3:
                    data_intake_comm_queue.put(0)
                elif task3_time >= out_3 and task3_time <= relax_3:
                    data_intake_comm_queue.put(1)
                
                elif task3_time >= relax_3:
                    is_ending_trial3 = True
            
            elif experiment.mode_status == "Trial 9":
                # high low medium
                # 10.0 6.0 6.5
                
                pressure_change_1 = 0.5
                out_1 = pressure_change_1 + 2.0
                relax_1 = out_1 + 10.0

                pressure_change_2 = relax_1 + 0.5
                out_2 = pressure_change_2 + 2.0
                relax_2 = out_2 + 6.0

                pressure_change_3 = relax_2 + 0.5
                out_3 = pressure_change_3 + 2.0
                relax_3 = out_3 + 6.5

                if task3_time < pressure_change_1:
                    data_intake_comm_queue.put(3100)
                elif task3_time >= pressure_change_1 and task3_time <= out_1:
                    data_intake_comm_queue.put(0)
                elif task3_time >= out_1 and task3_time <= relax_1:
                    data_intake_comm_queue.put(1)


                elif task3_time >= relax_1 and task3_time <= pressure_change_2:
                    data_intake_comm_queue.put(2300)
                elif task3_time >= pressure_change_2 and task3_time <= out_2:
                    data_intake_comm_queue.put(0)
                elif task3_time >= out_2 and task3_time <= relax_2:
                    data_intake_comm_queue.put(1)
                
                elif task3_time >= relax_2 and task3_time <= pressure_change_3:
                    data_intake_comm_queue.put(2700)
                elif task3_time >= pressure_change_3 and task3_time <= out_3:
                    data_intake_comm_queue.put(0)
                elif task3_time >= out_3 and task3_time <= relax_3:
                    data_intake_comm_queue.put(1)
                
                elif task3_time >= relax_3:
                    is_ending_trial3 = True




            if is_ending_trial3 and is_saved_trial3 == False:
                    saver_trial3.save_data("Stimulation tasks", experiment.mode_state)
                    is_saved_trial3 = True
                    print("SAVE THE FILE")

        # --------------------------------------------------------input data into monitor and plotter-------------------------------------------------
        # Initializes the dict of outputs with zeros
        # Care should be taken S.T. dict is initialized with valid, legal
        # arguments

        if not plotting_comm_queue.full():
            # These are the values to be plotted. The first value MUST be the
            # timestep, but the rest may be changed
            graph_titles = [
                "Pressure Value (psi)",
                "Solenoid Value (O or 1)",
                "Force sensor Fz (N)",
                "Force sensor Fy (N)",
                "Force sensor Fx (N)",
                "Force sensor Mz (Nm)",
                "Force sensor My (Nm)",
                "Force sensor Mx (Nm)",
            ]

            graph_data = [
                experiment.timestep,
                experiment.pressure_value,
                experiment.solenoid_value,
                experiment.Fz,
                experiment.Fy,
                experiment.Fx,
                experiment.Mz,
                experiment.My,
                experiment.Mx,
            ]
            plotting_comm_queue.put((graph_data, graph_titles))

    # Exit all processes

    # Exit the DAQ
    data_intake_comm_queue.put("EXIT")
    plotting_comm_queue.put("EXIT")
    data_intake_p.join()
    plotting_p.join()

    # Clear the queues
    for queue in QUEUES:
        while not queue.empty():
            queue.get_nowait()


if __name__ == "__main__":
    main()