# Collect kinematic data and perform ensemble analysis.
#
# author: Dimitar Stanev <jimstanev@gmail.com>
##
import os
import btk
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from utils import read_from_storage, extract_gait_cycle_intervals
from utils import normalize_interpolate_dataframe
from matplotlib.backends.backend_pdf import PdfPages

##
# define working directory

working_dir = os.path.abspath('./CP_GAIT_2.0_10-EXCELLENT_PATIENTS')
exclude_directories = ['kinematic_analysis']

subject_dirs = [directory
                for directory in os.listdir(working_dir)
                if os.path.isdir(os.path.join(working_dir, directory)) and
                directory not in exclude_directories]
output_dir = os.path.join(working_dir, exclude_directories[0])

##
# functions

def extract_gait_cycle_intervals(c3d_file_path):
    """Extracts gait cycle intervals from .c3d file.

    Parameters
    ----------
    c3d_file_path: file path

    Returns
    -------
    tuple: right and left leg intervals

    """
    c3d = btk.btkAcquisitionFileReader()
    c3d.SetFilename(c3d_file_path)
    c3d.Update()
    acq = c3d.GetOutput()
    fps = acq.GetPointFrequency()
    first_frame = acq.GetFirstFrame()
    opensim_sync = first_frame / fps

    # extract all events from c3d file
    right_events = {}
    left_events = {}
    for i in range(acq.GetEventNumber()):
        label = acq.GetEvent(i).GetLabel()
        time = acq.GetEvent(i).GetTime() - opensim_sync
        context = acq.GetEvent(i).GetContext()
        if context == 'Right':
            right_events.update({time: label})

        if context == 'Left':
            left_events.update({time: label})

    right_events = dict(sorted(right_events.items()))
    left_events = dict(sorted(left_events.items()))

    # print(right_events)
    # print(left_events)

    # extract intervals
    def extract_intervals_from_events(events):
        intervals = []
        start = None
        for key, val in events.items():
            if val == 'Foot Strike':
                if start is None:
                    start = key
                else:
                    intervals.append([start, key])
                    start = key

        return intervals

    right_intervals = extract_intervals_from_events(right_events)
    left_intervals = extract_intervals_from_events(left_events)

    return right_intervals, left_intervals


##
# collect all kinematics files

ensemble_right = []
ensemble_left = []
for directory in subject_dirs:
    # file path
    ik_file_path = os.path.join(working_dir,
                                directory,
                                'inverse_kinematics/'
                                'task_InverseKinematics.mot')
    c3d_file_path = os.path.join(working_dir,
                                 directory,
                                 'experimental_data/'
                                 'task.c3d')

    # load kinematics
    kinematics_df = read_from_storage(ik_file_path, 0.01, True)

    # extract gait cycle
    right_intervals, left_intervals = extract_gait_cycle_intervals(c3d_file_path)

    # partition trial on interval, normalize and collect into list
    for interval in right_intervals:
        df = kinematics_df[(kinematics_df.time >= interval[0]) &
                           (kinematics_df.time <= interval[1])]
        df_norm = normalize_interpolate_dataframe(df)
        ensemble_right.append(df_norm)

    for interval in left_intervals:
        df = kinematics_df[(kinematics_df.time >= interval[0]) &
                           (kinematics_df.time <= interval[1])]
        df_norm = normalize_interpolate_dataframe(df)
        ensemble_left.append(df_norm)


##
# compare kinematics for left and right legs

trials_right = pd.concat(ensemble_right, keys=range(len(ensemble_right)))
trials_left = pd.concat(ensemble_left, keys=range(len(ensemble_left)))
coordinates = ['hip_flexion', 'hip_adduction', 'hip_rotation',
               'knee_angle', 'ankle_angle']

with PdfPages(os.path.join(output_dir, 'left_vs_right_leg.pdf')) as pdf:
    for coordinate in coordinates:
        fig = plt.figure()
        sns.lineplot(data=trials_right, x='time', y=coordinate + '_r', label='right')
        sns.lineplot(data=trials_left, x='time', y=coordinate + '_l', label='left')
        plt.xlabel('gait cycle [0, 1]')
        plt.ylabel(coordinate.replace('_', ' ') + ' (deg)')
        plt.legend()
        fig.tight_layout()
        pdf.savefig(fig)
        plt.close()

##
