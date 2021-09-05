# ML Autoclicker
Thank you for checking out my first app! This was made exclusively using python and python packages. 
For now, there is only a standalone .exe for Windows which can be found here: https://github.com/jiakmao1/ML_Autoclicker/releases but the python and kivy files can also be found in this repository if using the python files are preferred.

![image](https://user-images.githubusercontent.com/90156923/132141732-fdf04288-67b9-41ef-8219-50e64054e4ca.png)

### What is ML Autoclicker?
ML Autoclicker is a program designed to allow the user to create a loop of actions for clicking on different parts of the screen. The inspiration comes from this https://sourceforge.net/projects/orphamielautoclicker/ autoclicker. In an attempt to expand upon this idea, ML Autoclicker allows similar autoclicking functionality, yet capability to click in multiple locations either in either an indefinite or specified loop. Alongside this comes the ability to save your configuration to any plain text file(.txt, .log, .docx, etc) to store for later use. This allows the user to easily load up configurations for different uses without having to manually set the autoclicker every startup.


### Key Features
* Add as many actions/steps as desired using the + and - buttons in the lower right portion of the screen
* Two modes of clicking: following the mouse, or at specified locations; toggleable in the lower left
* Select desired cursor locations either by typing them in or clicking the select button for each respective action/step
* Save/open configuration files for easy usage between sessions


### Notes
If you choose to download the python and kivy files, make sure you also download the logo.png file and make sure all of the files are in the same folder. Also, make sure python 3 is used as this program will probably not function with python 2

Python packages that might need to be installed(easiest way generally is using pip) :
* Kivy (for GUI)
* pynput (to control keyboard and mouse)
* plyer (to access the os' filechooser)
* ctypes (to control DPIAwareness on **Windows** for different resolution screens)
