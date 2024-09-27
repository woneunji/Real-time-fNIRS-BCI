# RealTime-fNIRS-BCI
Real-Time fNIRS-BCI system for target detection in DSR task.

## Method

• Data were acquired using NIRSports2 (NIRx Medical Technologies, Germany) with 20 prefrontal channels.
• The experimental paradigm was implemented using PsychoPy, and fNIRS data were recorded with Aurora fNIRS software.
• Real-time communication between the two was facilitated using PyLSL.

## Experiment

• The DSR(Discrimination/Selection Response) Task measures the ability to quickly identify and respond to a target stimulus among various stimuli [1].
• We used 'O' and 'X' as stimuli, with 'O' being the target stimulus.
• A total of 10 sessions were conducted, consisting of 5 randomized target sessions and 5 non-target sessions. In the target session, "O" appeared 30% of the time and "X" 70%, with "O" appearing around the midpoint, while in the non-target session, only "X" was presented.
![0503_fig1](https://github.com/user-attachments/assets/2f786ba6-96fb-4493-a4b2-dc9faa1a8dd0)
![0503_fig2](https://github.com/user-attachments/assets/7fcc44da-18d5-4476-9d0b-3d64b0e0ba82)


## Data Preprocessing

• We utilized the Python MNE-NIRS library for preprocessing the fNIRS data.
• You can refer to the mne_fnirs_analysis.ipynb file for the detailed process.

## Real-time System Design
• Each time a session begins, the trigger is input into the BCI system, and fNIRS raw data is accumulated in the buffer.
• After preprocessing, features are extracted and input into the classification model to perform the final prediction.
• PsychoPy, Aurora fNIRS (for recording), and the fNIRS-BCI all communicate with each other using pylsl.

<img src="https://github.com/user-attachments/assets/fdbca801-fe0e-4749-a7cc-3777de96b0b1.png  width="200" height="400"/>
▲ The proposed real-time fNIRS-BCI system design


## Reference

[1] Shin J. et al. Simultaneous acquisition of EEG and NIRS during cognitive tasks for an open access dataset. Sci Data 5, 2018
