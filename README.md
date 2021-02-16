# An automated approach to analyze motion capture trials in OpenSim

A repository containing an OpenSim template pipeline structure for performing
common analyses (extraction from c3d, scaling, inverse kinematics, inverse
dynamics, residual reduction analysis, static optimization, computed muscle
controls, muscle analysis, joint reaction analysis, etc.). The user can include
his c3d files, and with minimum changes to the scripts, one can perform
different analyses through OpenSim.

Each folder has a specific structure and name convention that should be
preserved so that the different setup files (`.xml`) can locate the files needed
for the analyses. The user should navigate into the `script` folder located in
each sub-folder. Scripts for converting c3d files and performing standard
analyses in OpenSim are provided. A caution note here is that the user should
manually inspect the results between individual steps (e.g., scaling). Sometimes
a mismatch in the marker placement can cause problems, especially when we work
with new data sets. We provide the marker placement in these examples, but the
user should define this carefully for a different setting.

The examples are organized as follows:

- `tutorial`: a very simple example that demonstrates how to extract marker
  positions, EMG, and ground reaction forces from c3d files, perform scaling,
  inverse kinematics, inverse dynamics, and static optimization using OpenSim.
- `simple`: does the same thing as the `tutorial` but goes one step further and
  performs additional analysis such as joint reaction calculations.  `complex`:
  does the same as `simple`, but the residual reduction algorithm is involved in
  the pipeline. Sometimes, users prefer not to use this algorithm, so we provide
  simple and complex variants. In the complex example, we also perform computed
  muscle controls in OpenSim.
- `opensim_example**: application of the analysis on the OpenSim gait
  examples. In these examples, no c3d files are provided, and we work directly
  with the .trc and .mot files. This is used as a test between the GUI and the
  scripts.

*If you are experiencing issues with visualizing the models, please include the
Geometry folder in `OPENSIM_HOME`.*

# Cite

If you find this useful you can cite it as follows:

```bibtex
@misc{opensim-template-pipeline,
  author = {Stanev, Dimitar},
  title = {An automated approach to analyze motion capture trials in OpenSim},
  year = {2021},
  publisher = {GitHub},
  journal = {GitHub repository},
  url = {https://github.com/mitkof6/opensim_automated_pipeline}
}
```
