import sys, os, re, shutil, webbrowser
from PyQt5 import QtWidgets, QtCore
from PyQt5.QtWidgets import QApplication, QMainWindow, QGridLayout, QSizePolicy

# Vehicle Lists ######

vehicles = ["a_bike",       "a_kart",       "b_bike",      "b_kart",      "c_bike",
            "c_kart",       "d_bike",       "d_kart",      "df_bike",     "df_kart",
            "df_bike_blue", "df_kart_blue", "df_bike_red", "df_kart_red", "e_bike",
            "e_kart"]

svehicleanims = ["bi","ka","bi","ka","bi",
                 "ka","bi","ka","bi","bi", #All small characters dont have special outside drift
                 "bi","ka","ka","ka","bi", #anims for some reason. Can just use inside drift anims.
                 "ka"]

mvehicleanims = ["bi","ka","bo","ka","bo",
                 "ka","bi","ka","bo","bo",
                 "bo","ka","ka","ka","bi",
                 "ka"]

lvehicleanims = ["bi","ka","bo","ka","bo",
                 "ka","bi","ka","bi","bi", #For some reason Standard Bike uses inside drift anims
                 "bi","ka","ka","ka","bi", #on large characters.
                 "ka"]

vehiclebrresmask = [[0,0] for _ in range(16)]

vehicletexturemask = [[0,0] for _ in range(16)]

VehicleBresCheckboxes = [] # Filled with QCheckBoxes generated from the vehicles list in VehicleBresWindow InitUI().
VehicleTexCheckboxes = [] # Filled with QCheckBoxes generated from the vehicles list in VehicleTexWindow InitUI().

# Character Lists ######

weights = ["l","l","l","l","l","l","l","l","l","l","l","l","l","l",
           "m","m","m","m","m","m","m","m","m","m","m","m","m","m",
           "s","s","s","s","s","s","s","s","s","s","s","s","s","s"]

characters = ["Funky Kong", "Rosalina",   "Bowser",     "Dry Bowser", "Wario", "Waluigi",   "Donkey Kong", "King Boo",   "Mii A Large (Male)",  "Mii B Large (Male)",  "Mii C Large (Male) (UNUSED IN-GAME)",  "Mii A Large (Female)",  "Mii B Large (Female)",  "Mii C Large (Female) (UNUSED IN-GAME)",
              "Mario",      "Yoshi",      "Birdo",      "Daisy",      "Peach", "Luigi",     "Bowser Jr",   "Diddy Kong", "Mii A Medium (Male)", "Mii B Medium (Male)", "Mii C Medium (Male) (UNUSED IN-GAME)", "Mii A Medium (Female)", "Mii B Medium (Female)", "Mii C Medium (Female) (UNUSED IN-GAME)",
              "Baby Daisy", "Baby Peach", "Baby Luigi", "Baby Mario", "Koopa", "Dry Bones", "Toad",        "Toadette",   "Mii A Small (Male)",  "Mii B Small (Male)",  "Mii C Small (Male) (UNUSED IN-GAME)",  "Mii A Small (Female)",  "Mii B Small (Female)",  "Mii C Small (Female) (UNUSED IN-GAME)"]

charids = ["fk", "rs", "kp", "bk", "wr","wl","dk","kt","la_mii_m","lb_mii_m","lc_mii_m","la_mii_f","lb_mii_f","lc_mii_f",
           "mr", "ys", "ca", "ds", "pc","lg","jr","dd","ma_mii_m","mb_mii_m","mc_mii_m","ma_mii_f","mb_mii_f","mc_mii_f",
           "bds","bpc","blg","bmr","nk","ka","ko","kk","sa_mii_m","sb_mii_m","sc_mii_m","sa_mii_f","sb_mii_f","sc_mii_f"]

ToolMode = 1
VehicleReplacementMode = 0
UseTireTexture = 0
UseMultiKartBrres = 0
AllKartSZS = 0


def find_files(szsfolder,charid,weight):
    filenames = []
    counter = 0
    for filename in os.listdir(szsfolder):
        if re.search(r"-{}".format(charid),filename) and filename[0] == weight:
            filenames.append(filename)
            counter += 1
    print("%s%s" % (counter," Files Found!"))
    return filenames

def decompress_szs(szsfolder,filenames):
    for filename in filenames:
        os.system(f'wszst extract "{szsfolder}/{filename}" --DEST "{szsfolder}/.temp/{filename}"')

def replace_brres(szsfolder,filenames,weight,brresgroup):
    if AllKartSZS != 0:
        os.system(f'wszst extract "{AllKartSZS}" --DEST "{szsfolder}/.temp/{os.path.basename(AllKartSZS)}"')
        TempAllKartSZS = szsfolder+"/.temp/"+os.path.basename(AllKartSZS)

    for filename in filenames:
        dest_path = szsfolder + "/.temp/" + filename
        if not os.path.exists(dest_path):
            continue
        for index, vehicle in enumerate(vehicles):
            if re.search(r"{}".format(vehicle)+"-",filename):
                vehiclename = weight+vehicle

                match weight:
                    case "s":
                        animtable = svehicleanims
                    case "m":
                        animtable = mvehicleanims
                    case "l":
                        animtable = lvehicleanims
                        
                if re.search(r"_4",filename):
                    animtype = animtable[index]+"m"
                else:
                    animtype = animtable[index]
                
                if ToolMode == 1 or ToolMode == 0:
                    match animtype:
                        case "bi":
                            newbrres = brresgroup.BIBrres
                        case "bim":
                            newbrres = brresgroup.BIMBrres
                        case "bo":
                            newbrres = brresgroup.BOBrres
                        case "bom":
                            newbrres = brresgroup.BOMBrres
                        case "ka":
                            newbrres = brresgroup.KABrres
                        case "kam":
                            newbrres = brresgroup.KAMBrres

                    os.remove(dest_path+"/"+"driver_model.brres")
                    newbrres = shutil.copy2(newbrres,dest_path+"/")
                    os.rename(newbrres,dest_path+"/"+"driver_model.brres")

                if ToolMode == 2 or ToolMode == 0:
                    if VehicleReplacementMode == 0:
                        if VehicleTexCheckboxes[index].checkState() == False:
                            continue
                        bodytex0name = "body"
                        tiretex0name = "tire"

                        match vehiclename:
                            case "lc_bike":
                                bodytex0name = "lc_bike_body"
                                tiretex0name = "lc_bike_tire"
                            case "lc_kart":
                                bodytex0name = "lc_kart_body"
                                tiretex0name = "lc_kart_tire"
                            case "ld_kart":
                                bodytex0name = "ld_kart_body"
                                tiretex0name = "ld_kart_tire"
                            case "ma_bike":
                                tiretex0name = "bike_tire"
                            case "mb_bike":
                                bodytex0name = "mb_bike_all"
                                tiretex0name = "mb_bike_tire"
                            case "mc_bike":
                                bodytex0name = "mc_bike_all"
                                tiretex0name = "mc_bike_tire"
                            case "mc_kart":
                                bodytex0name = "gesso3"
                                tiretex0name = "sc_tire"
                            case "md_bike":
                                bodytex0name = "md_bike_body"
                                tiretex0name = "md_bike_tire"
                            case "me_bike":
                                bodytex0name = "me_bike_body"
                                tiretex0name = "me_bike_tire"
                            case "me_kart":
                                bodytex0name = "me_kart_body"
                                tiretex0name = "me_kart_tire"
                            case "sa_bike":
                                bodytex0name = "sa_bike_all"
                                tiretex0name = "sa_bike_tire"
                            case "sc_kart":
                                bodytex0name = "sc_kart_all"
                                tiretex0name = "sc_tire"
                            case "sd_kart":
                                bodytex0name = "sd_kart_body"
                                tiretex0name = "sd_kart_tire"
                            case "se_kart":
                                bodytex0name = "se_kart_all"
                                tiretex0name = "se_kart_tire"

                        os.system(f'wszst extract "{dest_path}/kart_model.brres"')
                        os.system(f'wimgt encode "{vehicletexturemask[index][0]}" --transform TEX.CMPR --DEST "{dest_path}/kart_model.brres.d/Textures(NW4R)/{bodytex0name}" --n-mm=0 -r')
                        if UseTireTexture == 1:
                            os.system(f'wimgt encode "{vehicletexturemask[index][1]}" --transform TEX.CMPR --DEST "{dest_path}/kart_model.brres.d/Textures(NW4R)/{tiretex0name}" --n-mm=0 -r')
                        if AllKartSZS != 0 and not (re.search("_red",vehicle) or re.search("_blue",vehicle)):
                            os.system(f'wszst extract "{TempAllKartSZS}/{weight}{vehicle}.brres" --DEST "{TempAllKartSZS}/{weight}{vehicle}.d"')
                            os.system(f'wimgt encode "{vehicletexturemask[index][0]}" --transform TEX.CMPR --DEST "{TempAllKartSZS}/{weight}{vehicle}.d/Textures(NW4R)/{bodytex0name}" --n-mm=0 -r')
                            if UseTireTexture == 1:
                                os.system(f'wimgt encode "{vehicletexturemask[index][1]}" --transform TEX.CMPR --DEST "{TempAllKartSZS}/{weight}{vehicle}.d/Textures(NW4R)/{tiretex0name}" --n-mm=0 -r')
                            os.system(f'wszst create "{TempAllKartSZS}/{weight}{vehicle}.d" --DEST "{TempAllKartSZS}/{weight}{vehicle}.brres" -r')
                            shutil.rmtree(TempAllKartSZS+"/"+weight+vehicle+".d")

                        os.system(f'wszst create "{dest_path}/kart_model.brres.d" -r --brres')
                        shutil.rmtree(szsfolder+"/.temp/"+filename+"/kart_model.brres.d/")

                    elif VehicleReplacementMode == 1:
                        if re.search(r"_4",filename) and UseMultiKartBrres == 0:
                            continue
                        print(index,vehicle, VehicleBresCheckboxes[index].checkState())
                        if VehicleBresCheckboxes[index].checkState() == False:
                            continue
                        os.remove(dest_path+"/"+"kart_model.brres")

                        if re.search(r"_4",filename) and UseMultiKartBrres == 1:
                            newkartbrres = vehiclebrresmask[index][1]
                        else:
                            newkartbrres = vehiclebrresmask[index][0]
                        
                        print(newkartbrres,vehiclebrresmask,index)

                        newkartbrres = shutil.copy2(newkartbrres,dest_path+"/")
                        os.rename(newkartbrres,dest_path+"/"+"kart_model.brres")

def compress_szs(szsfolder,filenames,charid,rename):
    if rename != 0:
        renameid = charids[rename-1]

    for filename in filenames:
        newfilename = filename
        if rename != 0:
            newfilename = filename.replace(charid,renameid)
        os.system(f'wszst create "{szsfolder}/.temp/{filename}" --DEST "{szsfolder}/{newfilename}" -r')

    if (ToolMode == 2 or ToolMode == 0) and AllKartSZS != 0:
        os.system(f'wszst create "{szsfolder}/.temp/{os.path.basename(AllKartSZS)}" --DEST "{AllKartSZS}" -r')
    shutil.rmtree(szsfolder+"/.temp/")

def main_logic(szsfolder,charname,rename,brresgroup):
    index = characters.index(charname)
    charid = charids[index]
    weight = weights[index]

    filenames = find_files(szsfolder,charid,weight)
    print("index,charid,weight,filenames: ",index,charid,weight,filenames)
    print("VehicleReplacementMode,ToolMode,UseTireTex: ",VehicleReplacementMode,ToolMode,UseTireTexture)
    decompress_szs(szsfolder,filenames)
    if filenames.__len__() == 0:
        return 1
    replace_brres(szsfolder,filenames,weight,brresgroup)
    compress_szs(szsfolder,filenames,charid,rename)
    return 0

class BrresGroup:
    def __init__(self):
        self.BIBrres = 0
        self.BIMBrres = 0
        self.BOBrres = 0
        self.BOMBrres = 0
        self.KABrres = 0
        self.KAMBrres = 0

######################################################################################### GUI crap starts here (why is it so much bigger than logic)

###############
# Main Window #
###############
class MainWindow(QMainWindow):
    def __init__(self):
        super(MainWindow,self).__init__()
        self.setGeometry(400,300,780,440)
        self.setWindowTitle("Mass Character Creator v1.1")

        self.InitUI()

    def InitUI(self):
        self.BrresGroup = BrresGroup()
        self.OutputPath = 0
        self.VehicleTexWindow = 0
        self.VehicleBresWindow = 0

        self.ShowVehicleTexWindow()
        self.ShowVehicleBresWindow()

        self.grid = QGridLayout()
        self.LeftBtnLayout = QtWidgets.QGridLayout()
        widget = QtWidgets.QWidget()
        widget.setLayout(self.grid)
        self.setCentralWidget(widget)
        self.setMinimumSize(680,330)

        self.grid.addLayout(self.LeftBtnLayout,1,0,6,3)

        self.DriverGroup = QtWidgets.QButtonGroup(self)
        self.VehicleGroup = QtWidgets.QButtonGroup(self)
        
        # Labels
        self.CLabel = QtWidgets.QLabel(self)
        self.CLabel.setText("Made by Keta -- https://koopkorp.com")
        self.CLabel.setMaximumHeight(40)
        self.grid.addWidget(self.CLabel,0,0,1,3)
        

        self.TextLabel = QtWidgets.QLabel(self)
        self.TextLabel.setText("Press the Patch button once finished importing files and selecting character.")
        self.TextLabel.setMaximumHeight(40)
        self.grid.addWidget(self.TextLabel,0,3,1,8)

        # Scroll List
        self.CharacterList = QtWidgets.QListWidget(self)

        self.CharacterList.addItems(characters)
        self.CharacterList.currentRowChanged.connect(self.CharacterListSelected)
        self.CharacterList.setMinimumWidth(450)
        self.grid.addWidget(self.CharacterList,1,3,6,8)

        # Rename Files Dropdown
        self.RenameDDown = QtWidgets.QComboBox(self)
        self.RenameDDown.addItem("Disable Output File Renaming")
        self.RenameDDown.addItems(characters)
        self.RenameDDown.currentIndexChanged.connect(self.RenameDDownSelected)
        self.grid.addWidget(self.RenameDDown,7,0,1,3)

        # Buttons
        self.BIBrresBtn = QtWidgets.QPushButton(self)
        self.BIBrresBtn.setText("Bike Inside Drift driver_model.brres")
        self.BIBrresBtn.clicked.connect(self.BIFile)
        self.LeftBtnLayout.addWidget(self.BIBrresBtn,0,0,1,3)
        self.DriverGroup.addButton(self.BIBrresBtn)
        
        self.BIMBrresBtn = QtWidgets.QPushButton(self)
        self.BIMBrresBtn.setText("Multiplayer Bike Inside Drift driver_model.brres")
        self.BIMBrresBtn.clicked.connect(self.BIMFile)
        self.LeftBtnLayout.addWidget(self.BIMBrresBtn,1,0,1,3)
        self.DriverGroup.addButton(self.BIMBrresBtn)
        
        self.BOBrresBtn = QtWidgets.QPushButton(self)
        self.BOBrresBtn.setText("Bike Outside Drift driver_model.brres")
        self.BOBrresBtn.clicked.connect(self.BOFile)
        self.LeftBtnLayout.addWidget(self.BOBrresBtn,2,0,1,3)
        self.DriverGroup.addButton(self.BOBrresBtn)
        
        self.BOMBrresBtn = QtWidgets.QPushButton(self)
        self.BOMBrresBtn.setText("Multiplayer Bike Outside Drift driver_model.brres")
        self.BOMBrresBtn.clicked.connect(self.BOMFile)
        self.LeftBtnLayout.addWidget(self.BOMBrresBtn,3,0,1,3)
        self.DriverGroup.addButton(self.BOMBrresBtn)
        
        self.KABrresBtn = QtWidgets.QPushButton(self)
        self.KABrresBtn.setText("Kart driver_model.brres")
        self.KABrresBtn.clicked.connect(self.KAFile)
        self.LeftBtnLayout.addWidget(self.KABrresBtn,4,0,1,3)
        self.DriverGroup.addButton(self.KABrresBtn)
        
        self.KAMBrresBtn = QtWidgets.QPushButton(self)
        self.KAMBrresBtn.setText("Multiplayer Kart driver_model.brres")
        self.KAMBrresBtn.clicked.connect(self.KAMFile)
        self.LeftBtnLayout.addWidget(self.KAMBrresBtn,5,0,1,3)
        self.DriverGroup.addButton(self.KAMBrresBtn)

        # self.OutputPathBtn = QtWidgets.QPushButton(self)
        # self.OutputPathBtn.setText("Path to Driver.szs")
        # self.OutputPathBtn.clicked.connect(self.GetDriverSzs)
        # self.grid.addWidget(self.OutputPathBtn,7,3,1,8)

        self.OutputPathBtn = QtWidgets.QPushButton(self)
        self.OutputPathBtn.setText("Path to Folder With The 32 (or Less) SZS Archives")
        self.OutputPathBtn.clicked.connect(self.GetOutputPath)
        self.grid.addWidget(self.OutputPathBtn,7,3,1,8)

        self.PatchBtn = QtWidgets.QPushButton(self)
        self.PatchBtn.setText("Press to Patch")
        self.PatchBtn.clicked.connect(self.PatchCheck)
        self.PatchBtn.setMinimumHeight(60)
        self.PatchBtn.setSizePolicy(QtWidgets.QSizePolicy.Policy.Expanding,QtWidgets.QSizePolicy.Policy.Expanding)
        self.grid.addWidget(self.PatchBtn,8,3,2,8)

        # Setup Vehicle Masking Buttons
        self.MaskTexBtn = QtWidgets.QPushButton("Vehicle Texture Masking",self)
        self.MaskBresBtn = QtWidgets.QPushButton("Vehicle BRRES Masking",self)
        self.VehicleGroup.addButton(self.MaskTexBtn)
        self.VehicleGroup.addButton(self.MaskBresBtn)

        self.grid.addWidget(self.MaskTexBtn,10,0,1,3)
        self.grid.addWidget(self.MaskBresBtn,10,0,1,3)

        self.MaskTexBtn.clicked.connect(self.ShowVehicleTexWindow)
        self.MaskBresBtn.clicked.connect(self.ShowVehicleBresWindow)

        # Setup Vehicle Masking Type Checkboxes
        self.MaskTexCB = QtWidgets.QCheckBox("Replace Textures",self)
        self.MaskBresCB = QtWidgets.QCheckBox("Replace kart_model.brres",self)
        self.VehicleGroup.addButton(self.MaskTexCB)
        self.VehicleGroup.addButton(self.MaskBresCB)

        self.grid.addWidget(self.MaskTexCB,9,0,1,1)
        self.grid.addWidget(self.MaskBresCB,9,1,1,2)
        
        self.MaskTexCB.stateChanged.connect(self.ToggleVehToolMode)
        self.MaskBresCB.stateChanged.connect(self.ToggleVehToolMode)
        self.MaskTexCB.setChecked(True)

        # Choose replacement mode
        self.Mode0CB = QtWidgets.QCheckBox("Replace Both",self)
        self.Mode1CB = QtWidgets.QCheckBox("Replace Driver",self)
        self.Mode2CB = QtWidgets.QCheckBox("Replace Vehicle",self)

        self.grid.addWidget(self.Mode0CB,8,0)
        self.grid.addWidget(self.Mode1CB,8,1)
        self.grid.addWidget(self.Mode2CB,8,2)
        
        self.Mode0CB.stateChanged.connect(self.ToggleMode)
        self.Mode1CB.stateChanged.connect(self.ToggleMode)
        self.Mode2CB.stateChanged.connect(self.ToggleMode)
        self.Mode1CB.setChecked(True)
        
        sizepolicy = self.BIBrresBtn.sizePolicy()
        sizepolicy.setRetainSizeWhenHidden(True)

        for btn in (self.VehicleGroup.buttons()):
            btn.setSizePolicy(sizepolicy)

        sizepolicy.setVerticalPolicy(sizepolicy.Policy.Expanding)
        sizepolicy.setHorizontalPolicy(sizepolicy.Policy.Preferred)

        for btn in (self.DriverGroup.buttons()):
            btn.setSizePolicy(sizepolicy)



    def PatchCheck(self):
        print(self.CharacterList.currentItem().text())
        error = False
        if self.OutputPath == 0:
            self.TextLabel.setText("Invalid Path to The SZS Archives")
            error = True
        elif self.CharacterList.currentItem().text() not in characters:
            self.TextLabel.setText("Invalid Character Selection")
            error = True
        elif ToolMode == 1 or ToolMode == 0:
            if self.BrresGroup.BIBrres == 0:
                self.TextLabel.setText("Invalid Bike Inside Drift BRRES")
                error = True
            elif self.BrresGroup.BIMBrres == 0:
                self.TextLabel.setText("Invalid Multiplayer Bike Inside Drift BRRES")
                error = True
            elif self.BrresGroup.BOBrres == 0:
                self.TextLabel.setText("Invalid Bike Outside Drift BRRES")
                error = True
            elif self.BrresGroup.BOMBrres == 0:
                self.TextLabel.setText("Invalid Multiplayer Bike Outside Drift BRRES")
                error = True
            elif self.BrresGroup.KABrres == 0:
                self.TextLabel.setText("Invalid Kart BRRES")
                error = True
            elif self.BrresGroup.KAMBrres == 0:
                self.TextLabel.setText("Invalid Multiplayer Kart BRRES")
                error = True
        elif ToolMode == 2 or ToolMode == 0:
            match VehicleReplacementMode:
                case 0:
                    VehicleCheckboxes = VehicleTexCheckboxes
                    VehicleMask = vehicletexturemask
                    UseAlt = UseTireTexture
                    AltString = "Tire "
                    FType = "PNG"
                case 1:
                    VehicleCheckboxes = VehicleBresCheckboxes
                    VehicleMask = vehiclebrresmask
                    UseAlt = UseMultiKartBrres
                    AltString = "Multiplayer "
                    FType = "BRRES"

            for index, checkbox in enumerate(VehicleCheckboxes):
                if checkbox.checkState():
                    if VehicleMask[index][0] == 0:
                        self.TextLabel.setText(vehicles[index]+" "+FType+" is not Set! Please set path in Vehicle "+FType+" Masking window.\nIf not using "+AltString+FType+" uncheck the Use "+AltString+FType+" checkbox")
                        error = True
                    elif UseAlt == 1 and VehicleMask[index][1] == 0:
                        self.TextLabel.setText(vehicles[index]+" "+AltString+FType+" is not Set! Please set path in Vehicle "+FType+" Masking window.\nIf not using "+AltString+FType+" uncheck the Use "+AltString+FType+" checkbox")
                        error = True
                    

        if error == False:
            self.TextLabel.setText("In Progress...")
            print("Main Logic Args: ",self.OutputPath,self.CharacterList.currentItem().text(),self.BrresGroup)
            self.setEnabled(False)

            status = main_logic(self.OutputPath,self.CharacterList.currentItem().text(),self.RenameDDown.currentIndex(),self.BrresGroup)

            self.setEnabled(True)
            if status == 1:
                self.TextLabel.setText("There were no SZS files found in the folder. Please provide a folder populated with the appropriate SZS files.")
                return
            self.TextLabel.setText("Success! Files can be found at \n"+self.OutputPath)
        
    def RenameDDownSelected(self):
        if self.RenameDDown.currentIndex() != 0:
            self.TextLabel.setText("Output files will be renamed with "+self.RenameDDown.currentText()+"'s CharID of -"+charids[self.RenameDDown.currentIndex()-1]+".")
            return
        self.TextLabel.setText("Output files will keep the original CharID of the selected Character.")
        
    def CharacterListSelected(self):
        self.TextLabel.setText("Character "+self.CharacterList.currentItem().text()+" with a CharID of -"+charids[self.CharacterList.currentRow()]+" will be replaced.")
        
    # Handle Output Path File Dialog
    def GetOutputPath(self):
        self.OutputPath = QtWidgets.QFileDialog.getExistingDirectory(self)
        if not self.OutputPath:
            self.OutputPath = 0
            return
        self.TextLabel.setText("SZS Archives at: \n"+self.OutputPath)
        print("SZS Archives at: "+self.OutputPath)
        
    # Handle Driver.szs File Dialog
    def GetDriverSzs(self):
        self.DriverSZS,_ = QtWidgets.QFileDialog.getOpenFileName(self,'Open SZS File','','Driver.szs File (Driver.szs)')
        if not self.DriverSZS:
            self.DriverSZS = 0
            return
        self.TextLabel.setText("Driver.szs at: \n"+self.DriverSZS)
        print("Driver.szs at: "+self.DriverSZS)
        
    # Handle driver_model.brres File Dialogs
    def BIFile(self):
        self.BrresGroup.BIBrres,_ = QtWidgets.QFileDialog.getOpenFileName(self,'Open BRRES File','','BRRES File (*.brres)')
        if not self.BrresGroup.BIBrres:
            self.BrresGroup.BIBrres = 0
            self.TextLabel.setText("No BRRES File Selected (Bike Inside)")
            return
        BNRBrres = open(self.BrresGroup.BIBrres, "rb")
        BNRBrresData = BNRBrres.read(4).decode()
        BNRBrres.close
        if BNRBrresData != "bres":
            self.BrresGroup.BIBrres = 0
            self.TextLabel.setText("Corrupted Bike Inside BRRES (Invalid Header)")
            return
        self.TextLabel.setText("Bike Inside Brres at: \n"+self.BrresGroup.BIBrres)
        print("Bike Inside Brres at: "+self.BrresGroup.BIBrres)
            
    def BIMFile(self):
        self.BrresGroup.BIMBrres,_ = QtWidgets.QFileDialog.getOpenFileName(self,'Open BRRES File','','BRRES File (*.brres)')
        if not self.BrresGroup.BIMBrres:
            self.BrresGroup.BIMBrres = 0
            self.TextLabel.setText("No BRRES File Selected (Multiplayer Bike Inside)")
            return
        BNRBrres = open(self.BrresGroup.BIMBrres, "rb")
        BNRBrresData = BNRBrres.read(4).decode()
        BNRBrres.close
        if BNRBrresData != "bres":
            self.BrresGroup.BIMBrres = 0
            self.TextLabel.setText("Corrupted Multiplayer Bike Inside BRRES (Invalid Header)")
            return
        self.TextLabel.setText("Multiplayer Bike Inside BRRES at: \n"+self.BrresGroup.BIMBrres)
        print("Multiplayer Bike Inside BRRES at: "+self.BrresGroup.BIMBrres)
            
    def BOFile(self):
        self.BrresGroup.BOBrres,_ = QtWidgets.QFileDialog.getOpenFileName(self,'Open BRRES File','','BRRES File (*.brres)')
        if not self.BrresGroup.BOBrres:
            self.BrresGroup.BOBrres = 0
            self.TextLabel.setText("No BRRES File Selected (Bike Outside)")
            return
        BNRBrres = open(self.BrresGroup.BOBrres, "rb")
        BNRBrresData = BNRBrres.read(4).decode()
        BNRBrres.close
        if BNRBrresData != "bres":
            self.BrresGroup.BOBrres = 0
            self.TextLabel.setText("Corrupted Bike Outside BRRES (Invalid Header)")
            return
        self.TextLabel.setText("Bike Outside BRRES at: \n"+self.BrresGroup.BOBrres)
        print("Bike Outside BRRES at: "+self.BrresGroup.BOBrres)
            
    def BOMFile(self):
        self.BrresGroup.BOMBrres,_ = QtWidgets.QFileDialog.getOpenFileName(self,'Open BRRES File','','BRRES File (*.brres)')
        if not self.BrresGroup.BOMBrres:
            self.BrresGroup.BOMBrres = 0
            self.TextLabel.setText("No BRRES File Selected (Multiplayer Bike Outside)")
            return
        BNRBrres = open(self.BrresGroup.BOMBrres, "rb")
        BNRBrresData = BNRBrres.read(4).decode()
        BNRBrres.close
        if BNRBrresData != "bres":
            self.BrresGroup.BOMBrres = 0
            self.TextLabel.setText("Corrupted Multiplayer Bike Outside BRRES (Invalid Header)")
            return
        self.TextLabel.setText("Multiplayer Bike Outside BRRES at: \n"+self.BrresGroup.BOMBrres)
        print("Multiplayer Bike Outside BRRES at: "+self.BrresGroup.BOMBrres)
            
    def KAFile(self):
        self.BrresGroup.KABrres,_ = QtWidgets.QFileDialog.getOpenFileName(self,'Open BRRES File','','BRRES File (*.brres)')
        if not self.BrresGroup.KABrres:
            self.BrresGroup.KABrres = 0
            self.TextLabel.setText("No BRRES File Selected (Kart)")
            return
        BNRBrres = open(self.BrresGroup.KABrres, "rb")
        BNRBrresData = BNRBrres.read(4).decode()
        BNRBrres.close
        if BNRBrresData != "bres":
            self.BrresGroup.KABrres = 0
            self.TextLabel.setText("Corrupted Kart BRRES (Invalid Header)")
            return
        self.TextLabel.setText("Kart BRRES at: \n"+self.BrresGroup.KABrres)
        print("Kart BRRES at: "+self.BrresGroup.KABrres)
            
    def KAMFile(self):
        self.BrresGroup.KAMBrres,_ = QtWidgets.QFileDialog.getOpenFileName(self,'Open BRRES File','','BRRES File (*.brres)')
        if not self.BrresGroup.KAMBrres:
            self.BrresGroup.KAMBrres = 0
            self.TextLabel.setText("No BRRES File Selected (Multiplayer Kart)")
            return
        BNRBrres = open(self.BrresGroup.KAMBrres, "rb")
        BNRBrresData = BNRBrres.read(4).decode()
        BNRBrres.close
        if BNRBrresData != "bres":
            self.BrresGroup.KAMBrres = 0
            self.TextLabel.setText("Corrupted Multiplayer Kart BRRES (Invalid Header)")
            return
        
        self.TextLabel.setText("Multiplayer Kart BRRES at: \n"+self.BrresGroup.KAMBrres)
        print("Multiplayer Kart BRRES at: "+self.BrresGroup.KAMBrres)
        
    # Vehicle Texture Masking Window
    def ShowVehicleTexWindow(self):
        if self.VehicleTexWindow == 0:
            self.VehicleTexWindow = VehicleWindow("texture")
            return
        self.VehicleTexWindow.show()
            
    # Vehicle BRRES Masking Window
    def ShowVehicleBresWindow(self):
        if self.VehicleBresWindow == 0:
            self.VehicleBresWindow = VehicleWindow("brres")
            return
        self.VehicleBresWindow.show()

    def ToggleMode(self):
        if self.sender().checkState() == False:
            return
        
        global ToolMode
        smallsizepolicy = QSizePolicy()
        smallsizepolicy.setHorizontalPolicy(smallsizepolicy.Policy.Minimum)
        smallsizepolicy.setVerticalPolicy(smallsizepolicy.Policy.Fixed)
        smallsizepolicy.setRetainSizeWhenHidden(True)
        
        bigsizepolicy = QSizePolicy()
        bigsizepolicy.setHorizontalPolicy(smallsizepolicy.Policy.Expanding)
        bigsizepolicy.setVerticalPolicy(smallsizepolicy.Policy.Expanding)
        bigsizepolicy.setRetainSizeWhenHidden(True)

        match self.sender():
            case self.Mode0CB:
                ToolMode = 0

                self.Mode0CB.setEnabled(False)
                self.Mode1CB.setEnabled(True)
                self.Mode2CB.setEnabled(True)

                self.Mode1CB.setChecked(False)
                self.Mode2CB.setChecked(False)

                for button in self.DriverGroup.buttons():
                    button.show()

                self.MaskTexBtn.setSizePolicy(smallsizepolicy)
                self.LeftBtnLayout.removeWidget(self.MaskTexBtn)
                self.grid.addWidget(self.MaskTexBtn,10,0,1,3)
                
                self.MaskBresBtn.setSizePolicy(smallsizepolicy)
                self.LeftBtnLayout.removeWidget(self.MaskBresBtn)
                self.grid.addWidget(self.MaskBresBtn,10,0,1,3)

                for button in self.VehicleGroup.buttons():
                    button.show()

            case self.Mode1CB:
                ToolMode = 1
                
                self.Mode0CB.setEnabled(True)
                self.Mode1CB.setEnabled(False)
                self.Mode2CB.setEnabled(True)

                self.Mode0CB.setChecked(False)
                self.Mode2CB.setChecked(False)

                for button in self.DriverGroup.buttons():
                    button.show()
                    
                self.MaskTexBtn.setSizePolicy(smallsizepolicy)
                self.LeftBtnLayout.removeWidget(self.MaskTexBtn)
                self.grid.addWidget(self.MaskTexBtn,10,0,1,3)
                
                self.MaskBresBtn.setSizePolicy(smallsizepolicy)
                self.LeftBtnLayout.removeWidget(self.MaskBresBtn)
                self.grid.addWidget(self.MaskBresBtn,10,0,1,3)

                for button in self.VehicleGroup.buttons():
                    button.hide()

            case self.Mode2CB:
                ToolMode = 2
                
                self.Mode0CB.setEnabled(True)
                self.Mode1CB.setEnabled(True)
                self.Mode2CB.setEnabled(False)

                self.Mode0CB.setChecked(False)
                self.Mode1CB.setChecked(False)

                for button in self.DriverGroup.buttons():
                    button.hide()
                
                self.MaskTexBtn.setSizePolicy(bigsizepolicy)
                self.grid.removeWidget(self.MaskTexBtn)
                self.LeftBtnLayout.addWidget(self.MaskTexBtn,0,0,1,3)
                
                self.MaskBresBtn.setSizePolicy(bigsizepolicy)
                self.grid.removeWidget(self.MaskBresBtn)
                self.LeftBtnLayout.addWidget(self.MaskBresBtn,0,0,1,3)

                for button in self.VehicleGroup.buttons():
                    button.show()

        match self.MaskBresCB.isChecked():
            case True:
                self.MaskTexBtn.hide()
            case False:
                self.MaskBresBtn.hide()
        
    def ToggleVehToolMode(self):
        if self.sender().checkState() == False:
            return
        global VehicleReplacementMode
        match self.sender():
            case self.MaskTexCB:
                self.MaskBresCB.setChecked(False)
                self.MaskBresBtn.hide()
                self.MaskTexBtn.show()
                VehicleReplacementMode = 0
                self.VehicleBresWindow.hide()
            case self.MaskBresCB:
                self.MaskTexCB.setChecked(False)
                self.MaskTexBtn.hide()
                self.MaskBresBtn.show()
                VehicleReplacementMode = 1
                self.VehicleTexWindow.hide()


    def closeEvent(self,event):
        QApplication.closeAllWindows()


        
####################################
# Holds Vehicle Texture Tick Boxes #
####################################
class VehicleWindow(QtWidgets.QWidget):
    def __init__(self,wintype):
        super(VehicleWindow,self).__init__()
        self.setGeometry(400,300,600,200)
        if wintype == "texture":
            self.setWindowTitle("Vehicle PNG Masking")
        elif wintype == "brres":
            self.setWindowTitle("Vehicle BRRES Masking")

        self.wintype = wintype

        self.InitUI()

    def InitUI(self):
        grid = QGridLayout()
        self.TireButtons = QtWidgets.QButtonGroup()
        self.MultiBRRESButtons = QtWidgets.QButtonGroup()
        self.setLayout(grid)

        sizepolicy = QtWidgets.QSizePolicy()

        match self.wintype:
            case "texture":
                self.togglealt = QtWidgets.QCheckBox("Use Tire PNG?",self)
            case "brres":
                self.togglealt = QtWidgets.QCheckBox("Use Multiplayer BRRES?",self)
        
        grid.addWidget(self.togglealt,8,5)
        self.togglealt.toggled.connect(self.AltCheckboxToggled)
        
        
        kartcount = 0
        for i,vehicle in enumerate(vehicles):
            checkbox = QtWidgets.QCheckBox(vehicle,self)
            btn1 = QtWidgets.QPushButton("Path to Body PNG",self)
            sizepolicy = btn1.sizePolicy()
            sizepolicy.setRetainSizeWhenHidden(True)
            btn1.setSizePolicy(sizepolicy)
            
            if self.wintype == "brres":
                btn1.setText("Path to Normal BRRES")
                btn2 = QtWidgets.QPushButton("Path to Multiplayer BRRES",self)
                btn2.setSizePolicy(sizepolicy)
                btn2.clicked.connect(lambda state, x=vehicle,y=True: self.TexButtonClicked(x,y))
                self.MultiBRRESButtons.addButton(btn2)
            else:
                btn2 = QtWidgets.QPushButton("Path to Tire PNG",self)
                btn2.setSizePolicy(sizepolicy)
                btn2.clicked.connect(lambda state, x=vehicle,y=True: self.TexButtonClicked(x,y))
                self.TireButtons.addButton(btn2)

            checkbox.toggled.connect(lambda state, x=vehicle,y=checkbox,z=btn1,a=btn2: self.VehCheckboxToggled(y,x,z,a))
            btn1.clicked.connect(lambda state, x=vehicle,y=False: self.TexButtonClicked(x,y))

            if re.search("kart",vehicle):
                grid.addWidget(checkbox,i-kartcount-1,3)
                grid.addWidget(btn1,i-kartcount-1,4)
                grid.addWidget(btn2,i-kartcount-1,5)
                kartcount += 1
            else:
                grid.addWidget(checkbox,i-kartcount,0)
                grid.addWidget(btn1,i-kartcount,1)
                grid.addWidget(btn2,i-kartcount,2)
            
            match self.wintype:
                case "brres":
                    VehicleBresCheckboxes.append(checkbox)
                case "texture":
                    VehicleTexCheckboxes.append(checkbox)
                    
            btn1.hide()
            btn2.hide()

        if self.wintype == "texture":
            self.AllKartBtn = QtWidgets.QPushButton("xx-allkart.szs")
            self.AllKartBtn.setSizePolicy(sizepolicy)
            self.AllKartBtn.clicked.connect(self.GetAllKartSzs)
            grid.addWidget(self.AllKartBtn,8,4)
        
    # Handle xx-allkart.szs File Dialog
    def GetAllKartSzs(self):
        global AllKartSZS
        AllKartSZS,_ = QtWidgets.QFileDialog.getOpenFileName(self,'Open SZS File','','xx-allkart.szs File (*-allkart.szs)')
        if not AllKartSZS:
            AllKartSZS = 0
            return
        print("xx-allkart.szs at: "+AllKartSZS)

    def VehCheckboxToggled(self,checkbox,vehicle,btn1,btn2):
        match self.wintype:
            case "brres":
                VehicleCheckboxes = VehicleBresCheckboxes
                vehiclemask = vehiclebrresmask
                UseAlt = UseMultiKartBrres
            case "texture":
                VehicleCheckboxes = VehicleTexCheckboxes
                vehiclemask = vehicletexturemask
                UseAlt = UseTireTexture
                
        index = VehicleCheckboxes.index(checkbox)

        if checkbox.isChecked():
            btn1.show()
            if UseAlt == 0:
                return
            btn2.show()
        else:
            vehiclemask[index] = [0,0]
            btn1.hide()
            btn2.hide()

    def TexButtonClicked(self, vehicle, altfile):
        match self.wintype:
            case "brres":
                vehiclemask = vehiclebrresmask
                VehicleCheckboxes = VehicleBresCheckboxes
                filetype = ['Open BRRES File','','BRRES (*.brres)']
            case "texture":
                vehiclemask = vehicletexturemask
                VehicleCheckboxes = VehicleTexCheckboxes
                filetype = ['Open PNG File','','PNG (*.png)']

        index = vehicles.index(vehicle)
    
        if VehicleCheckboxes[index].checkState():
            if altfile:
                vehiclemask[index][1],_ = QtWidgets.QFileDialog.getOpenFileName(self,*filetype)
            else:
                vehiclemask[index][0],_ = QtWidgets.QFileDialog.getOpenFileName(self,*filetype)

            if not vehiclemask[index]:
                vehiclemask[index] = [0,0]
                return
            
            if altfile:
                print(vehicle+" Alt File: ",os.path.basename(vehiclemask[index][1]))
            else:
                print(vehicle+" File: ",os.path.basename(vehiclemask[index][0]))
        
    def AltCheckboxToggled(self):
        global UseTireTexture
        global UseMultiKartBrres
        match self.wintype:
            case "brres":
                VehicleCheckboxes = VehicleBresCheckboxes
                ButtonGroup = self.MultiBRRESButtons
            case "texture":
                VehicleCheckboxes = VehicleTexCheckboxes
                ButtonGroup = self.TireButtons
        if self.togglealt.isChecked():
            match self.wintype:
                case "brres":
                    UseMultiKartBrres = 1
                case "texture":
                    UseTireTexture = 1

            for i,button in enumerate(ButtonGroup.buttons()):
                if VehicleCheckboxes[i].isChecked():
                    button.show()
        else:
            match self.wintype:
                case "brres":
                    UseMultiKartBrres = 0
                case "texture":
                    UseTireTexture = 0

            for i,button in enumerate(ButtonGroup.buttons()):
                if VehicleCheckboxes[i].isChecked():
                    button.hide()





def window():
    app = QApplication(sys.argv)
    win = MainWindow()

    win.show()
    sys.exit(app.exec_())

if shutil.which("wimgt") and shutil.which("wszst"):
    window()
else:
    app = QApplication(sys.argv)
    widget = QtWidgets.QWidget()
    warnbox = QtWidgets.QMessageBox(widget)
    warnbox.setWindowTitle("Missing Prerequisites!")
    warnbox.setText("Wiimm's SZS Tools are not installed! Download them at https://szs.wiimm.de/download.html")

    cancel = warnbox.addButton("Close",QtWidgets.QMessageBox.ButtonRole.RejectRole)
    download = warnbox.addButton("Download",QtWidgets.QMessageBox.ButtonRole.AcceptRole)

    warnbox.exec_()

    if warnbox.clickedButton() is cancel:
        sys.exit()
    elif warnbox.clickedButton() is download:
        webbrowser.open("https://szs.wiimm.de/download.html")
        sys.exit()

    sys.exit(app.exec_())
