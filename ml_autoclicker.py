from kivy.config import Config
Config.set('graphics','resizable',False)
Config.set('kivy','exit_on_escape',False)
from time import sleep as Sleep
from os import popen
from copy import deepcopy
from kivy.app import App 
from kivy.lang import Builder
from kivy.clock import mainthread
from kivy.core.window import Window
from kivy.factory import Factory
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.spinner import Spinner
from kivy.uix.button import Button
from kivy.uix.popup import Popup
from kivy.properties import StringProperty,ObjectProperty,BooleanProperty
from pynput import mouse,keyboard
import threading
from plyer import filechooser
import ctypes


awareness = ctypes.c_int()
ctypes.windll.shcore.SetProcessDpiAwareness(2)
Builder.load_file('ml_layout.kv')

class HoverBehavior(object):
    hovered = BooleanProperty(False)
    border_point= ObjectProperty(None)
    def __init__(self, **kwargs):
        self.register_event_type('on_enter')
        self.register_event_type('on_leave')
        Window.bind(mouse_pos=self.on_mouse_pos)
        super().__init__(**kwargs)

    def on_mouse_pos(self, *args):
        if not self.get_root_window():
            return 
        pos = args[1]
        inside = self.collide_point(*self.to_widget(*pos))
        if self.hovered == inside:
            return
        self.border_point = pos
        self.hovered = inside
        if inside:
            self.dispatch('on_enter')
        else:
            self.dispatch('on_leave')

    def on_enter(self):
        pass

    def on_leave(self):
        pass

Factory.register('HoverBehavior', HoverBehavior)

#Class for main window#
class Test(FloatLayout):
    #Some necesarry class variables#
    DictofDefaults = {
        "checkbox":True,
        "mousex":"0",
        "mousey":"0",
        "clicks":"1",
        "spinner":"Left",
        "hour1":"0",
        "minute1":"0",
        "second1":"0",
        "millis1":"500",
        "hour2":"0",
        "minute2":"0",
        "second2":"0",
        "millis2":"0",
        "looptimes":"1"}
    ridlist = ["r1","r2","r3","r4"]
    riddefault = {
        "r1":True,
        "r2":False,
        "r3":True,
        "r4":False
    }
    hotkeybool = True
    popupactive = False
    popupcancel = False
    loadup = False
    ridhash = dict()
    TextInputDict = dict()
    runinputDict = dict()
    keyList = dict()
    label = 0
    rowMax = 1
    defaulthotkey = keyboard.Key.esc
    startlabel = StringProperty()
    stoplabel = StringProperty()
    configfile = "Config file not set..."

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.loadup = True
        for rid in self.ridlist:
            self.ridhash[rid] = self.riddefault[rid]
        for k,v in self.ridhash.items():
            if v == True:
                self.ids[k].state = "down"
            
        self.butstate = self.ids["startbut"].state
        self.keylistencont = keyboard.Listener(on_press=self.hotkeyinfo,on_release=self.keypress)
        self.keylistencont.start()

        if "Key." in str(self.defaulthotkey):
            self.startlabel = f'Start({str(self.defaulthotkey)[4:].capitalize()})'
            self.stoplabel = f'Stop({str(self.defaulthotkey)[4:].capitalize()})'
        else:
            self.startlabel = f'Start(\'{self.defaulthotkey}\')'
            self.stoplabel = f'Stop(\'{self.defaulthotkey}\')'
        self.trackmousecont = mouse.Listener(on_move=self.mousemove)
        if self.ridhash["r1"] == True:
            self.trackmousecont.start()
        self.loadup = False
        Window.bind(on_request_close=self.exitcheck)
        self.refhotkey = deepcopy(self.defaulthotkey)
        self.refradiohash = deepcopy(self.ridhash)
        self.refinputhash = deepcopy(self.TextInputDict)

    def exitcheck(self,*args):
        if list(self.TextInputDict.values()) != list(self.refinputhash.values()) \
            or self.defaulthotkey != self.refhotkey \
            or list(self.ridhash.values()) != list(self.refradiohash.values()):
            self.exitpopup = ExitWindow("Exit Confirmation","Do you want to save before exiting?\n\n")
            self.exitpopup.open()
            return True
        else:
            return False

    def openFilemain(self):
        self.disabled = True
        self.counter = 0
        path = filechooser.open_file(
                            title="Open File", 
                            filters=[
                                ("All Files (*.*)", "*.*"),
                                ("Text Documents (*.txt)","*.txt")],)
        self.disabled = False
        try:
            self.pathopen = path[0]
            tempcheckfile = popen(f'more {self.pathopen}').readlines()
            tempcheckfile = popen(f'more {self.pathopen}').read().splitlines()
            if tempcheckfile[0] == "#This is an ML Autoclicker config file#":
                self.pathname = path[0]
                if "\\" in path[0]:
                    filename = path[0].split("\\")
                elif "/" in path[0]:
                    filename = path[0].split("/")
                self.configfile = filename[-1]
            with open(path[0],"r") as Configfile:
                readFile = Configfile.read().splitlines()
            for line in readFile:
                if line == '':
                    continue
                elif "Number" in line:
                    templine = line.split(":")
                    self.rowMax = int(templine[1])
                elif "Hotkey" in line:
                    templine = line.split(":")
                    self.defaulthotkey = keyboard.Key[templine[1]]
                    self.startlabel = f'Start({str(self.defaulthotkey)[4:].capitalize()})'
                    self.stoplabel = f'Stop({str(self.defaulthotkey)[4:].capitalize()})'
                elif "Radio_Button_Hash" in line:
                    self.counter = 1
                elif self.counter == 1 and line != "" and "User_Input_Hash:" not in line:
                    templine = line.split(":")
                    if "True" in templine[1]:
                        self.ridhash[templine[0]] = True
                    elif "False" in templine[1]:
                        self.ridhash[templine[0]] = False
                elif "User_Input_Hash:" in line:
                    self.counter = 2
                elif self.counter == 2 and line != "" and "Radio_Button_Hash" not in line:
                    templine = line.split(":")
                    if len(templine) == 3:
                        if templine[2] == "True":
                            self.TextInputDict[(templine[0],templine[1])] = True
                        elif templine[2] == "False":
                            self.TextInputDict[(templine[0],templine[1])] = False
                        else:
                            self.TextInputDict[(templine[0],templine[1])] = templine[2]
                    elif len(templine) == 2:
                        self.TextInputDict[templine[0]] = str(templine[1])
            self.refhotkey = deepcopy(self.defaulthotkey)
            self.refradiohash = deepcopy(self.ridhash)
            self.refinputhash = deepcopy(self.TextInputDict)
        except:
            if len(path[0]) > 48 :
                if "\\" in path[0]:
                    filename = path[0].split("\\")
                elif "/" in path[0]:
                    filename = path[0].split("/")
                temppath = filename[-1]
                labeltext = f"Not an ML Autoclicker config file:\n {temppath}"
                self.pogpopup3 = PopWindow("Error",labeltext)
                self.pogpopup3.size = ((len(path[0])/55)*self.pogpopup3.width,self.pogpopup3.height)
            else:
                labeltext = f"Not an ML Autoclicker config file::\n {path[0]}"
                self.pogpopup3 = PopWindow("Error",labeltext)
            self.pogpopup3.open()
            path = []
        self.ids["FileLabel"].text = self.configfile
        self.addData()
        path = []
    @mainthread
    def addData(self):
        self.loadup = True
        self.ids["MainTable"].clear_widgets()
        self.ids["MainTable"].add_widget(Row("0"))
        self.label = 0
        for row in range(1,self.rowMax):
            self.ids["MainTable"].addRow()
        for radio in self.ridhash.keys():
            if self.ridhash[radio] == True:
                self.ids[radio].state = "down"
        self.ids["rlooptimes"].text = str(self.TextInputDict[self.ids["rlooptimes"].name])
        for child in self.children[-1].children[0].children:
            for number,grandchild in enumerate(child.children):
                if number == 2:
                    templabel = grandchild.children[1].children[1].text
                    grandchild.children[1].children[0].active = self.TextInputDict[(templabel,"checkbox")]
                    for child in grandchild.children[0].children[0].children:
                        child.children[1].text = self.TextInputDict[(templabel,child.children[1].name)]
                elif number == 1:
                    templabel = child.children[2].children[1].children[1].text
                    grandchild.children[1].text = self.TextInputDict[(templabel,grandchild.children[1].name)]
                    grandchild.children[0].text = self.TextInputDict[(templabel,grandchild.children[0].name)]
                elif number ==0:
                    templabel = child.children[2].children[1].children[1].text
                    for greatgrandchild in grandchild.children:
                        for descendant in greatgrandchild.children:
                            descendant.children[1].text = self.TextInputDict[(templabel,descendant.children[1].name)]
    
        self.loadup = False

    def openFile(self):
        openThread = threading.Thread(target=self.openFilemain)
        openThread.start()

    def saveAsFilemain(self):
        self.disabled = True
        path = filechooser.save_file(title="Save as...", 
                             filters=[
                                ("All Files (*.*)", "*.*"),
                                ("Text Documents (*.txt)","*.txt")])
        self.disabled = False
        try:
            self.pathname = path[0]
            with open(path[0],"w") as writeFile:
                print("#This is an ML Autoclicker config file#\n\n",file=writeFile)
                print(f"Number of Rows:{Test.label+1}",file=writeFile)
                if "Key." in str(self.defaulthotkey):
                    print(f"Hotkey:{str(self.defaulthotkey)[4:]}",file=writeFile)
                else:
                    print(f"Hotkey:{str(self.defaulthotkey)}",file=writeFile)
                print(f"Radio_Button_Hash:",file=writeFile)
                for k,v in self.ridhash.items():
                    print((f"{k}:{v}" ),file=writeFile)
                print("User_Input_Hash:",file=writeFile)
                for k,v in self.TextInputDict.items():
                    if k == "looptimes":
                        print(f"{k}:{v}",file=writeFile)
                    else:
                        print(f"{k[0]}:{k[1]}:{v}",file=writeFile)
            self.refhotkey = deepcopy(self.defaulthotkey)
            self.refradiohash = deepcopy(self.ridhash)
            self.refinputhash = deepcopy(self.TextInputDict)

        except:
            pass

        try:
            if "\\" in path[0]:
                filename = path[0].split("\\")
            elif "/" in path[0]:
                filename = path[0].split("/")
            self.configfile = filename[-1]
        except:
            self.configfile = "Config file not set..."
        self.ids["FileLabel"].text = self.configfile

    def saveAsFile(self):
        openThread = threading.Thread(target=self.saveAsFilemain)
        openThread.start()

    def saveMain(self):
        if self.configfile == "Config file not set...":
            self.saveAsFile()
        else:
            with open(self.pathname,"w") as writeFile:
                print("#This is an ML Autoclicker config file#\n\n",file=writeFile)
                print(f"Number of Rows:{Test.label+1}",file=writeFile)
                if "Key." in str(self.defaulthotkey):
                    print(f"Hotkey:{str(self.defaulthotkey)[4:]}",file=writeFile)
                else:
                    print(f"Hotkey:{str(self.defaulthotkey)}",file=writeFile)
                print(f"Radio_Button_Hash:",file=writeFile)
                for k,v in self.ridhash.items():
                    print((f"{k}:{v}" ),file=writeFile)
                print("User_Input_Hash:",file=writeFile)
                for k,v in self.TextInputDict.items():
                    if k == "looptimes":
                        print(f"{k}:{v}",file=writeFile)
                    else:
                        print(f"{k[0]}:{k[1]}:{v}",file=writeFile)
            self.refhotkey = deepcopy(self.defaulthotkey)
            self.refradiohash = deepcopy(self.ridhash)
            self.refinputhash = deepcopy(self.TextInputDict)
            if "*" in self.ids["FileLabel"].text:
                self.configfile = self.configfile.replace("*","")
            self.ids["FileLabel"].text = self.configfile

    def save(self):
        openThread = threading.Thread(target=self.saveMain)
        openThread.start()

    def getValue(self):
        if self.loadup == False:
            for rid in self.ridlist:
                self.ridhash[rid] = self.ids[rid].active
                if list(self.ridhash.values()) != list(self.refradiohash.values()) and self.configfile != "Config file not set...":
                    if "*" not in self.configfile:
                        self.configfile = self.configfile+"*"
                        self.ids["FileLabel"].text = self.configfile
        if self.ridhash["r1"] == True:
            self.trackmousecont = mouse.Listener(on_move=self.mousemove)
            self.trackmousecont.start()
        elif self.ridhash["r1"] == False:
            self.trackmousecont.stop()

    #Main Function for the autoclicker#
    def click(self):
        self.Trigger = True
        self.mousecontrol = mouse.Controller()

        #Converting all delay input times into seconds#
        maxtemplist = []
        for key in Test.TextInputDict.keys():
            if type(key) == tuple:
                maxtemplist.append(int(key[0]))
            elif type(key) == str:
                continue
        maxlabel = max(set(maxtemplist))+1
        for templabel in range(0,maxlabel):
            templabel = str(templabel)
            tempdict = {
                "temph1" : 3600*int(Test.TextInputDict[(templabel,"hour1")]),
                "tempm1" : 60*int(Test.TextInputDict[(templabel,"minute1")]),
                "temps1" : int(Test.TextInputDict[(templabel,"second1")]),
                "tempms1" : (int(Test.TextInputDict[(templabel,"millis1")]))/1000}
            Test.runinputDict[(templabel,"delay1")] = sum(tempdict[key] for key in tempdict.keys())
            tempdict = {
                "temph2" : 3600*int(Test.TextInputDict[(templabel,"hour2")]),
                "tempm2" : 60*int(Test.TextInputDict[(templabel,"minute2")]),
                "temps2" : int(Test.TextInputDict[(templabel,"second2")]),
                "tempms2" : (int(Test.TextInputDict[(templabel,"millis2")]))/1000}
            Test.runinputDict[(templabel,"delay2")] = sum(tempdict[key] for key in tempdict.keys())

        #Main Loop for autoclicker#
        while self.Trigger  == True:
            if self.ridhash["r1"] == False:
                if self.ridhash["r3"] == False:
                    for loop in range(0,int(Test.TextInputDict["looptimes"])):
                        if self.Trigger == True:
                            for templabel in range(0,maxlabel):
                                templabel = str(templabel)
                                if self.Trigger == True:
                                    if Test.TextInputDict[(templabel,"checkbox")] == True:
                                        for i in range(0,int(Test.TextInputDict[(templabel,"clicks")])):
                                            if self.Trigger == True:
                                                self.mousecontrol.position = (int(Test.TextInputDict[(templabel,"mousex")]),int(Test.TextInputDict[(templabel,"mousey")]))
                                                self.mousecontrol.click(mouse.Button[Test.TextInputDict[(templabel,"spinner")].lower()])
                                                Sleep(Test.runinputDict[(templabel,"delay1")])
                                            elif self.Trigger == False:
                                                break
                                        Sleep(Test.runinputDict[(templabel,"delay2")])
                                elif self.Trigger == False:
                                    break

                        elif self.Trigger == False:
                            break
                    self.notbuttonstop()
                elif self.ridhash["r3"] == True:
                    for templabel in range(0,maxlabel):
                        templabel = str(templabel)
                        if self.Trigger == True:
                            if Test.TextInputDict[(templabel,"checkbox")] == True:
                                for i in range(0,int(Test.TextInputDict[(templabel,"clicks")])):
                                    if self.Trigger == True:
                                        self.mousecontrol.position = (int(Test.TextInputDict[(templabel,"mousex")]),int(Test.TextInputDict[(templabel,"mousey")]))
                                        self.mousecontrol.click(mouse.Button[Test.TextInputDict[(templabel,"spinner")].lower()])
                                        Sleep(Test.runinputDict[(templabel,"delay1")])
                                    elif self.Trigger == False:
                                        break
                                Sleep(Test.runinputDict[(templabel,"delay2")])
                        elif self.Trigger == False:
                            break
            elif self.ridhash["r1"] == True:
                if self.ridhash["r3"] == False:
                    for loop in range(0,int(Test.TextInputDict["looptimes"])):
                        if self.Trigger == True:
                            for templabel in range(0,maxlabel):
                                templabel = str(templabel)
                                if self.Trigger == True:
                                    if Test.TextInputDict[(templabel,"checkbox")] == True:
                                        for i in range(0,int(Test.TextInputDict[(templabel,"clicks")])):
                                            if self.Trigger == True:
                                                self.mousecontrol.position = (self.track_x,self.track_y)
                                                self.mousecontrol.click(mouse.Button[Test.TextInputDict[(templabel,"spinner")].lower()])
                                                Sleep(Test.runinputDict[(templabel,"delay1")])
                                            elif self.Trigger == False:
                                                break
                                        Sleep(Test.runinputDict[(templabel,"delay2")])
                                elif self.Trigger == False:
                                    break
                        elif self.Trigger == False:
                            break
                    self.notbuttonstop()
                elif self.ridhash["r3"] == True:
                    for templabel in range(0,maxlabel):
                        templabel = str(templabel)
                        if self.Trigger == True:
                            if Test.TextInputDict[(templabel,"checkbox")] == True:
                                for i in range(0,int(Test.TextInputDict[(templabel,"clicks")])):
                                    if self.Trigger == True:
                                        self.mousecontrol.position = (self.track_x,self.track_y)
                                        self.mousecontrol.click(mouse.Button[Test.TextInputDict[(templabel,"spinner")].lower()])
                                        Sleep(Test.runinputDict[(templabel,"delay1")])
                                    elif self.Trigger == False:
                                        break
                                Sleep(Test.runinputDict[(templabel,"delay2")])
                        elif self.Trigger == False:
                            break

    def stop(self):
        if self.butstate == "down":
            self.Trigger = False
            self.butstate = "normal"

    def notbuttonstop(self):
        self.stop()
        self.ids["startbut"].state = "normal"
        self.ids["stopbut"].state = "down"
        Sleep(0.1)
        self.ids["stopbut"].state = "normal"
        self.hotkeybool = True

    def start(self):
        if self.butstate == "normal":
            self.clickinstance = threading.Thread(target=self.click)
            self.butstate = "down"
            self.clickinstance.start()

    def hotkeyboolpress(self):
        self.hotkeybool = False

    def hotkeyinfo(self,key):
        keypress = str(self.keylistencont.canonical(key))
        if keypress not in self.keyList.keys():
            self.keyList[keypress] = keypress
        tempkeycheck = list(self.keyList.keys())
        if "Key.ctrl" in tempkeycheck and Window.focus == True:
            if "Key.shift" in tempkeycheck and "'s'" in tempkeycheck:
                self.saveAsFile()
            elif "'s'" in tempkeycheck and "Key.shift" not in tempkeycheck:
                self.save()
            elif "'o'" in tempkeycheck:
                self.openFile()

    def keypress(self,key):
        keyrelease = str(self.keylistencont.canonical(key))
        if key == self.defaulthotkey: 
            if self.hotkeybool == True and self.popupactive == False:
                Test.start(self)
                self.ids["startbut"].state = "down"
                self.hotkeybool = False
            elif self.hotkeybool == False:
                self.notbuttonstop()
        self.keyList.pop(keyrelease)

    def mousemove(self,x,y):
        self.track_x = x
        self.track_y = y
        
    def giveNumber(self,instance,name):
            Test.TextInputDict[name] = instance
            if list(self.TextInputDict.values()) != list(self.refinputhash.values()) and self.configfile != "Config file not set...":
                if "*" not in self.configfile:
                    self.configfile = self.configfile+"*"
                    self.ids["FileLabel"].text = self.configfile

    def set_hotkey(self):
        self.pogpopup = PopWindow("Choose Hotkey","Press any key")
        self.keylisten = keyboard.Listener(on_release=self.on_key_release)
        self.keylisten.start()
        self.pogpopup.open()

    def on_key_release(self,key):
        self.defaulthotkey = key
        if self.defaulthotkey != self.refhotkey and self.configfile != "Config file not set...":
            if "*" not in self.configfile:
                self.configfile = self.configfile+"*"
                self.ids["FileLabel"].text = self.configfile
        if "Key." in str(self.defaulthotkey):
            self.startlabel = f'Start({str(self.defaulthotkey)[4:].capitalize()})'
            self.stoplabel = f'Stop({str(self.defaulthotkey)[4:].capitalize()})'
        else:
            self.startlabel = f'Start(\'{self.defaulthotkey}\')'
            self.stoplabel = f'Stop(\'{self.defaulthotkey}\')'
        self.pogpopup.dismiss()
        self.keylisten.stop()

    def giveInfo(self):
        labelinfo = [
            "About ML Autoclicker:\n",
            "ML Autoclicker allows multiple locations\n",
            "to be selected for clicking. Use it to loop\n",
            "clicks indefinitely or only for a certain\n",
            "number of iterations.\n\n",
            "Instructions:\n",
            "1.  Add/remove desired number of steps \n",
            "by using the +/- buttons in the lower right.\n",
            "2.  Select whether to click following your mouse\n",
            "or at predetermined locations.\n",
            "3.  Select whether to loop indefinitely\n",
            "or for a certain number of times.\n",
            "4.  If \"Pick Location\" is enabled,\n",
            "click the \"Select\" button for each location desired.\n",
            "5.  Choose the number of clicks \n",
            "and click type for each step.\n",
            "6.  Choose the delay for clicks within each step\n",
            "as well as the delay \n",
            "before moving on to the next step.\n"
            "Note:To increase the delay between loop iterations,\n",
            "just increase the delay of the final step\n"
            "7.  After creating your desired autoclicker, you can\n",
            "save the configuration as a text file for later use."]
        self.pogpopup = PopWindow("Instructions/Information","".join(labelinfo))
        self.pogpopup.size = (400,600)
        self.pogpopup.open()

#Class for Scrollview which holds Row widgets#
class Table(BoxLayout):
    RowID = list()
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.add_widget(Row("0"))

    def addRow(self):
        Test.label+=1
        self.add_widget(Row(str(Test.label)))
        self.cursorLocation()
        if Test.loadup == False:
            tempTest = AutoClicker.get_running_app().root
            if list(tempTest.TextInputDict.values()) != list(tempTest.refinputhash.values()) and tempTest.configfile != "Config file not set...":
                if "*" not in tempTest.configfile:
                    tempTest.configfile = tempTest.configfile+"*"
                    tempTest.ids["FileLabel"].text = tempTest.configfile
            
    def delRow(self):
        if Test.label >=1:
            templist = []
            for k,v in Test.TextInputDict.items():
                if str(k[0]) == str(Test.label):
                    templist.append(k)
            for thing in templist:
                Test.TextInputDict.pop(thing)
            
            Test.label-=1
            self.remove_widget(self.children[0])
            if Test.loadup == False:
                tempTest = AutoClicker.get_running_app().root
                if list(tempTest.TextInputDict.values()) != list(tempTest.refinputhash.values()) and tempTest.configfile != "Config file not set...":
                    if "*" not in tempTest.configfile:
                        tempTest.configfile = tempTest.configfile+"*"
                        tempTest.ids["FileLabel"].text = tempTest.configfile

    def cursorLocation(self):
        for child in self.children:
            if Test.ridhash["r2"] == False:
                child.ids["selectButton"].disabled = True
                child.ids["mousex"].disabled = True
                child.ids["mousey"].disabled = True
            elif Test.ridhash["r2"] == True:
                if child.ids["Checkbox"].active == True:
                    child.ids["selectButton"].disabled = False
                    child.ids["mousex"].disabled = False
                    child.ids["mousey"].disabled = False
                elif child.ids["Checkbox"].active == False:
                    child.ids["selectButton"].disabled = True
                    child.ids["mousex"].disabled = True
                    child.ids["mousey"].disabled = True

#Class for widgets to dynamically add in teh Table Class#
class Row(BoxLayout):
    txt = StringProperty()
    def __init__(self,label, **kwargs):
        super().__init__(**kwargs)
        self.txt = label
        self.uniqID = f'row{label}'
        Table.RowID.append(self.uniqID)
        inputkeyList = list(Test.TextInputDict.keys())
        for name in list(Test.DictofDefaults.keys()):
            if name =="looptimes":
                if name not in inputkeyList:
                    Test.TextInputDict[name] = Test.DictofDefaults[name]
            else:
                if (str(int(label)),name) not in inputkeyList:
                    Test.TextInputDict[(label,name)] = Test.DictofDefaults[name]

    def picklocation(self):
        self.pogpopup2 = PopWindow("Choose Location","Click anywhere to choose location")
        self.mouselisten = mouse.Listener(on_click=self.on_mouse_release)
        self.mouselisten.start()
        self.pogpopup2.open()
        
    def on_mouse_release(self,x,y,button,pressed):
        if self.pogpopup2.ids["cancelbutton"].hovered == False:
            self.mouselocation = (x,y)
            self.children[-1].children[0].children[0].children[0].children[1].text = str(self.mouselocation[1])
            self.children[-1].children[0].children[0].children[1].children[1].text = str(self.mouselocation[0])
            self.pogpopup2.dismiss()
        self.mouselisten.stop()

    def giveNumber(self,instance,name,actuallabel):
        if instance == "":
            instance = 0
        Test.TextInputDict[(str(actuallabel),name)] = instance
        tempTest = AutoClicker.get_running_app().root  
        if list(tempTest.TextInputDict.values()) != list(tempTest.refinputhash.values()) and tempTest.configfile != "Config file not set...":
            if "*" not in tempTest.configfile:
                tempTest.configfile = tempTest.configfile+"*"
                tempTest.ids["FileLabel"].text = tempTest.configfile
    def cursorLocation(self):
        if Test.ridhash["r2"] == False:
            self.ids["selectButton"].disabled = True
            self.ids["mousex"].disabled = True
            self.ids["mousey"].disabled = True
        elif Test.ridhash["r2"] == True:
            if self.ids["Checkbox"].active == True:
                self.ids["selectButton"].disabled = False
                self.ids["mousex"].disabled = False
                self.ids["mousey"].disabled = False
            elif self.ids["Checkbox"].active == False:
                self.ids["selectButton"].disabled = True
                self.ids["mousex"].disabled = True
                self.ids["mousey"].disabled = True

#Classes for custom kivy widgets#
class RadioBox():
    pass
class SpinOption(Button):
    pass
class MySpinner(Spinner,HoverBehavior):
    option_cls = ObjectProperty(SpinOption)

class PopWindow(Popup):
    titname = StringProperty()
    labelpopupname = StringProperty()
    def __init__(self,titlename,poplabeltext, **kwargs):
        super().__init__(**kwargs)
        self.titname = titlename
        self.labelpopupname = poplabeltext
    def passActiveValue(self,value):
        Test.popupactive = value
    def buttonbool(self,bool):
        self.popupcancel = bool
class ExitWindow(Popup):
    titname = StringProperty()
    labelpopupname = StringProperty()
    def __init__(self,titlename,poplabeltext, **kwargs):
        super().__init__(**kwargs)
        self.titname = titlename
        self.labelpopupname = poplabeltext
    def passActiveValue(self,value):
        Test.popupactive = value
    def buttonbool(self,bool):
        self.popupcancel = bool
    def exitSave(self):
        AutoClicker.get_running_app().root.save()
        self.dismiss()
        AutoClicker.get_running_app().stop()
class AutoClicker(App):
    def build(self):
        self.title = "ML AutoClicker"
        self.icon = "logo.png"
        return Test()

if __name__ == '__main__':
    AutoClicker().run()
