# Automates the execution of OpenSim analyses.
#
# It is better to execute the analyses one by one in the OpenSim GUI and perform
# the necessary sanity checks to be sure. Once we are sure that all stages work
# properly (e.g., scaling), this script can be used to automate the
# process. Make sure that the initial and final time of the residual reduction
# algorithm corresponds to when the legs touch the force plates. To check this,
# plot the vertical force of the left and right legs (e.g.,
# experimental_data/walk_grf.mot) to identify the time interval.
#
# author: Dimitar Stanev <jimstanev@gmail.com>
##
import re
import os
from subprocess import PIPE, run, call
from utils import adjust_model_mass, subject_specific_isometric_force
from utils import plot_sto_file, replace_thelen_muscles_with_millard

##
# subject data

# 1.8m, 70 kg
subject_height = 1.8
generic_height = 1.70
subject_dir = os.path.abspath('../')
os.chdir(subject_dir)
print('subject dir:' + subject_dir)

# switches
adapt_mass = True
adapt_muscle_strength = True
calculate_muscle_activations = True
calculate_joint_reactions = True

##
# scale

os.chdir('scale/')
call(['opensim-cmd', 'run-tool', 'setup_scale.xml'])
os.chdir(subject_dir)

##
# inverse kinematics

os.chdir('inverse_kinematics/')
call(['opensim-cmd', 'run-tool', 'setup_ik.xml'])
plot_sto_file('task_InverseKinematics.mot', 'task_InverseKinematics.pdf', 3)
plot_sto_file('task_ik_marker_errors.sto', 'task_ik_marker_errors.pdf', 3)
plot_sto_file('task_ik_model_marker_locations.sto',
              'task_ik_model_marker_locations.pdf', 3)
os.chdir(subject_dir)

##
# residual reduction algorithm and model adjustment

os.chdir('residual_reduction_algorithm/')
rra_output = run(['opensim-cmd', 'run-tool', 'setup_rra.xml'],
                 stdout=PIPE, stderr=PIPE, universal_newlines=True)
print(rra_output.stdout)

# find mass change from RRA output (perform only when RRA does not suggest much
# mass change)
if adapt_mass:
    mass_change = float(re.findall(
        '[-+]?[.]?[\d]+(?:,\d\d\d)*[\.]?\d*(?:[eE][-+]?\d+)?',
        re.search('Total mass change: .?[0-9]+[.][0-9]+',
                  rra_output.stdout).group(0))[0])

    # load model and manually adjust body masses (RRA adjusts only CoM not body
    # masses)
    adjust_model_mass('model_adjusted.osim', mass_change)

# adjust max isometric force of subject-specific model based on height and
# weight regression model
if adapt_muscle_strength:
    subject_specific_isometric_force('../model/model_generic.osim',
                                     'model_adjusted.osim',
                                     generic_height,
                                     subject_height)

os.chdir(subject_dir)

##
# inverse dynamics

os.chdir('inverse_dynamics/')
call(['opensim-cmd', 'run-tool', 'setup_id.xml'])
plot_sto_file('task_InverseDynamics.sto', 'task_InverseDynamics.pdf', 3)
os.chdir(subject_dir)

##
# muscle analysis

os.chdir('muscle_analysis/')
replace_thelen_muscles_with_millard(
    '../residual_reduction_algorithm/model_adjusted.osim', '.')
call(['opensim-cmd', 'run-tool', 'setup_ma.xml'])
plot_sto_file('task_MuscleAnalysis_NormalizedFiberLength.sto',
              'task_MuscleAnalysis_NormalizedFiberLength.pdf', 3)
plot_sto_file('task_MuscleAnalysis_NormFiberVelocity.sto',
              'task_MuscleAnalysis_NormFiberVelocity.pdf', 3)
os.chdir(subject_dir)

##
# static optimization

if calculate_muscle_activations:
    os.chdir('static_optimization/')
    call(['opensim-cmd', 'run-tool', 'setup_so.xml'])
    plot_sto_file('task_StaticOptimization_activation.sto',
                  'task_StaticOptimization_activation.pdf', 3)
    plot_sto_file('task_StaticOptimization_force.sto',
                  'task_StaticOptimization_force.pdf', 3)
    os.chdir(subject_dir)

##
# joint reaction analysis

if calculate_muscle_activations and calculate_joint_reactions:
    os.chdir('joint_reaction_analysis/')
    call(['opensim-cmd', 'run-tool', 'setup_jra.xml'])
    plot_sto_file('task_JointReaction_ReactionLoads.sto',
                  'task_JointReaction_ReactionLoads.pdf', 3)
    os.chdir(subject_dir)


##
# computed muscle controls (takes more time)

if calculate_muscle_activations:
    os.chdir('computed_muscle_controls/')
    call(['opensim-cmd', 'run-tool', 'setup_cmc.xml'])
    # plot_sto_file('task_states.sto', 'task_states.pdf', 3)
    plot_sto_file('task_Actuation_force.sto', 'task_Actuation_force.pdf', 3)
    plot_sto_file('task_MuscleAnalysis_NormalizedFiberLength.sto',
                  'task_MuscleAnalysis_NormalizedFiberLength.pdf', 3)
    plot_sto_file('task_MuscleAnalysis_NormFiberVelocity.sto',
                  'task_MuscleAnalysis_NormFiberVelocity.pdf', 3)
    os.chdir(subject_dir)

##
