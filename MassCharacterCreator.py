import sys, os, re, shutil
from PyQt5 import QtWidgets, QtCore
from PyQt5.QtWidgets import QApplication, QMainWindow, QGridLayout

# Vehicle Lists ######

vehicles = ["a_bike",     "a_kart", "b_bike",      "b_kart",     "c_bike",
            "c_kart",     "d_bike", "d_kart",      "df_bike",    "df_bike_blue",
            "df_bike_red","df_kart","df_kart_blue","df_kart_red","e_bike",
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
    for filename in filenames:
        dest_path = szsfolder + "/.temp/" + filename
        if not os.path.exists(dest_path):
            continue
        for vehicle in vehicles:
            if re.search(r"{}".format(vehicle),filename):
                index = vehicles.index(vehicle)

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
                break

def compress_szs(szsfolder,filenames,charid,rename):
    if rename != 0:
        renameid = charids[rename-1]

    for filename in filenames:
        if rename != 0:
            newfilename = filename.replace(charid,renameid)
        os.system(f'wszst create "{szsfolder}/.temp/{filename}" --DEST "{szsfolder}/{newfilename}" -r')
    shutil.rmtree(szsfolder+"/.temp/")

def main_logic(szsfolder,charname,rename,brresgroup):
    index = characters.index(charname)
    charid = charids[index]
    weight = weights[index]

    filenames = find_files(szsfolder,charid,weight)
    print("index,charid,weight,filenames: ",index,charid,weight,filenames)
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


class MainWindow(QMainWindow):
    def __init__(self):
        super(MainWindow,self).__init__()
        self.setGeometry(400,300,715,440)
        self.setWindowTitle("Mass Character Create v1.0")

        self.InitUI()

    def InitUI(self):
        self.BrresGroup = BrresGroup()
        self.OutputPath = 0

        grid = QGridLayout()
        widget = QtWidgets.QWidget()
        widget.setLayout(grid)
        self.setCentralWidget(widget)
        
        # Labels
        self.CLabel = QtWidgets.QLabel(self)
        self.CLabel.setText("Made by Keta -- https://koopkorp.com")
        self.CLabel.setMaximumHeight(40)
        grid.addWidget(self.CLabel,0,0)
        

        self.ErrorLabel = QtWidgets.QLabel(self)
        self.ErrorLabel.setText("Press the Patch button once finished importing files and selecting character.")
        self.ErrorLabel.setMaximumHeight(40)
        self.setMinimumWidth(200)
        grid.addWidget(self.ErrorLabel,0,1)

        # Scroll List
        self.CharacterList = QtWidgets.QListWidget(self)

        self.CharacterList.addItems(characters)
        self.CharacterList.currentRowChanged.connect(self.CharacterListSelected)
        grid.addWidget(self.CharacterList,2,1,7,2)

        # Rename Files Dropdown
        self.RenameDDown = QtWidgets.QComboBox(self)
        self.RenameDDown.addItem("Disable Output File Renaming")
        self.RenameDDown.addItems(characters)
        self.RenameDDown.currentIndexChanged.connect(self.RenameDDownSelected)
        grid.addWidget(self.RenameDDown,8,0)

        # Buttons

        self.BIBrresBtn = QtWidgets.QPushButton(self)
        self.BIBrresBtn.setText("Path to Inside Drift driver_model.brres")
        self.BIBrresBtn.clicked.connect(self.BIFile)
        self.BIBrresBtn.setMinimumHeight(40)
        grid.addWidget(self.BIBrresBtn,2,0)
        
        self.BIMBrresBtn = QtWidgets.QPushButton(self)
        self.BIMBrresBtn.setText("Path to Multiplayer Inside Drift driver_model.brres")
        self.BIMBrresBtn.clicked.connect(self.BIMFile)
        self.BIMBrresBtn.setMinimumHeight(40)
        grid.addWidget(self.BIMBrresBtn,3,0)
        
        self.BOBrresBtn = QtWidgets.QPushButton(self)
        self.BOBrresBtn.setText("Path to Outside Drift driver_model.brres")
        self.BOBrresBtn.clicked.connect(self.BOFile)
        self.BOBrresBtn.setMinimumHeight(40)
        grid.addWidget(self.BOBrresBtn,4,0)
        
        self.BOMBrresBtn = QtWidgets.QPushButton(self)
        self.BOMBrresBtn.setText("Path to Multiplayer Outside Drift driver_model.brres")
        self.BOMBrresBtn.clicked.connect(self.BOMFile)
        self.BOMBrresBtn.setMinimumHeight(40)
        grid.addWidget(self.BOMBrresBtn,5,0)
        
        self.KABrresBtn = QtWidgets.QPushButton(self)
        self.KABrresBtn.setText("Path to Kart driver_model.brres")
        self.KABrresBtn.clicked.connect(self.KAFile)
        self.KABrresBtn.setMinimumHeight(40)
        grid.addWidget(self.KABrresBtn,6,0)
        
        self.KAMBrresBtn = QtWidgets.QPushButton(self)
        self.KAMBrresBtn.setText("Path to Multiplayer Kart driver_model.brres")
        self.KAMBrresBtn.clicked.connect(self.KAMFile)
        self.KAMBrresBtn.setMinimumHeight(40)
        grid.addWidget(self.KAMBrresBtn,7,0)

        self.OutputPathBtn = QtWidgets.QPushButton(self)
        self.OutputPathBtn.setText("Path to Folder With The 32 (or Less) SZS Archives")
        self.OutputPathBtn.clicked.connect(self.GetOutputPath)
        grid.addWidget(self.OutputPathBtn,8,1,9,2)

        self.PatchBtn = QtWidgets.QPushButton(self)
        self.PatchBtn.setText("Press to Patch")
        self.PatchBtn.clicked.connect(self.PatchCheck)
        self.PatchBtn.setMinimumHeight(60)
        grid.addWidget(self.PatchBtn,11,1,14,2)


    def PatchCheck(self):
        print(self.CharacterList.currentItem().text())
        if self.OutputPath == 0:
            self.ErrorLabel.setText("Invalid Path to The SZS Archives")
        elif self.CharacterList.currentItem().text() not in characters:
            self.ErrorLabel.setText("Invalid Character Selection")
        elif self.BrresGroup.BIBrres == 0:
            self.ErrorLabel.setText("Invalid Bike Inside Drift BRRES")
        elif self.BrresGroup.BIMBrres == 0:
            self.ErrorLabel.setText("Invalid Multiplayer Bike Inside Drift BRRES")
        elif self.BrresGroup.BOBrres == 0:
            self.ErrorLabel.setText("Invalid Bike Outside Drift BRRES")
        elif self.BrresGroup.BOMBrres == 0:
            self.ErrorLabel.setText("Invalid Multiplayer Bike Outside Drift BRRES")
        elif self.BrresGroup.KABrres == 0:
            self.ErrorLabel.setText("Invalid Kart BRRES")
        elif self.BrresGroup.KAMBrres == 0:
            self.ErrorLabel.setText("Invalid Multiplayer Kart BRRES")
        else:
            self.ErrorLabel.setText("In Progress...")
            print("Main Logic Args: ",self.OutputPath,self.CharacterList.currentItem().text(),self.BrresGroup)
            self.setEnabled(False)
            status = main_logic(self.OutputPath,self.CharacterList.currentItem().text(),self.RenameDDown.currentIndex(),self.BrresGroup)
            self.setEnabled(True)
            if status == 1:
                self.ErrorLabel.setText("There were no SZS files found in the folder. Please provide a folder populated with the appropriate SZS files.")
                return
            self.ErrorLabel.setText("Success! Files can be found at "+self.OutputPath)
        
    def RenameDDownSelected(self):
        if self.RenameDDown.currentIndex() != 0:
            self.ErrorLabel.setText("Output files will be renamed with "+self.RenameDDown.currentText()+"'s CharID of -"+charids[self.RenameDDown.currentIndex()-1]+".")
            return
        self.ErrorLabel.setText("Output files will keep the original CharID of the selected Character.")
        
    def CharacterListSelected(self):
        self.ErrorLabel.setText("Character "+self.CharacterList.currentItem().text()+" with a CharID of -"+charids[self.CharacterList.currentRow()]+" will be replaced.")
        
    def GetOutputPath(self):
        self.OutputPath = QtWidgets.QFileDialog.getExistingDirectory(self)
        if not self.OutputPath:
            self.OutputPath = 0
            return
        self.ErrorLabel.setText("SZS Archives at: "+self.OutputPath)
        print("SZS Archives at: "+self.OutputPath)
        

    def BIFile(self):
        self.BrresGroup.BIBrres,_ = QtWidgets.QFileDialog.getOpenFileName(self)
        if not self.BrresGroup.BIBrres:
            self.BrresGroup.BIBrres = 0
            self.ErrorLabel.setText("No Brres File Selected (Bike Inside)")
            return
        BNRBrres = open(self.BrresGroup.BIBrres, "rb")
        BNRBrresData = BNRBrres.read(4).decode()
        BNRBrres.close
        if BNRBrresData != "bres":
            self.BrresGroup.BIBrres = 0
            self.ErrorLabel.setText("Corrupted Bike Inside Brres (Invalid Header)")
            return
        self.ErrorLabel.setText("Bike Inside Brres at: "+os.path.basename(self.BrresGroup.BIBrres))
        print("Bike Inside Brres at: "+self.BrresGroup.BIBrres)
            
    def BIMFile(self):
        self.BrresGroup.BIMBrres,_ = QtWidgets.QFileDialog.getOpenFileName(self)
        if not self.BrresGroup.BIMBrres:
            self.BrresGroup.BIMBrres = 0
            self.ErrorLabel.setText("No Brres File Selected (Multiplayer Bike Inside)")
            return
        BNRBrres = open(self.BrresGroup.BIMBrres, "rb")
        BNRBrresData = BNRBrres.read(4).decode()
        BNRBrres.close
        if BNRBrresData != "bres":
            self.BrresGroup.BIMBrres = 0
            self.ErrorLabel.setText("Corrupted Multiplayer Bike Inside Brres (Invalid Header)")
            return
        self.ErrorLabel.setText("Multiplayer Bike Inside Brres at: "+os.path.basename(self.BrresGroup.BIMBrres))
        print("Multiplayer Bike Inside Brres at: "+self.BrresGroup.BIMBrres)
            
    def BOFile(self):
        self.BrresGroup.BOBrres,_ = QtWidgets.QFileDialog.getOpenFileName(self)
        if not self.BrresGroup.BOBrres:
            self.BrresGroup.BOBrres = 0
            self.ErrorLabel.setText("No Brres File Selected (Bike Outside)")
            return
        BNRBrres = open(self.BrresGroup.BOBrres, "rb")
        BNRBrresData = BNRBrres.read(4).decode()
        BNRBrres.close
        if BNRBrresData != "bres":
            self.BrresGroup.BOBrres = 0
            self.ErrorLabel.setText("Corrupted Bike Outside Brres (Invalid Header)")
            return
        self.ErrorLabel.setText("Bike Outside Brres at: "+os.path.basename(self.BrresGroup.BOBrres))
        print("Bike Outside Brres at: "+self.BrresGroup.BOBrres)
            
    def BOMFile(self):
        self.BrresGroup.BOMBrres,_ = QtWidgets.QFileDialog.getOpenFileName(self)
        if not self.BrresGroup.BOMBrres:
            self.BrresGroup.BOMBrres = 0
            self.ErrorLabel.setText("No Brres File Selected (Multiplayer Bike Outside)")
            return
        BNRBrres = open(self.BrresGroup.BOMBrres, "rb")
        BNRBrresData = BNRBrres.read(4).decode()
        BNRBrres.close
        if BNRBrresData != "bres":
            self.BrresGroup.BOMBrres = 0
            self.ErrorLabel.setText("Corrupted Multiplayer Bike Outside Brres (Invalid Header)")
            return
        self.ErrorLabel.setText("Multiplayer Bike Outside Brres at: "+os.path.basename(self.BrresGroup.BOMBrres))
        print("Multiplayer Bike Outside Brres at: "+self.BrresGroup.BOMBrres)
            
    def KAFile(self):
        self.BrresGroup.KABrres,_ = QtWidgets.QFileDialog.getOpenFileName(self)
        if not self.BrresGroup.KABrres:
            self.BrresGroup.KABrres = 0
            self.ErrorLabel.setText("No Brres File Selected (Kart)")
            return
        BNRBrres = open(self.BrresGroup.KABrres, "rb")
        BNRBrresData = BNRBrres.read(4).decode()
        BNRBrres.close
        if BNRBrresData != "bres":
            self.BrresGroup.KABrres = 0
            self.ErrorLabel.setText("Corrupted Kart Brres (Invalid Header)")
            return
        self.ErrorLabel.setText("Kart Brres at: "+os.path.basename(self.BrresGroup.KABrres))
        print("Kart Brres at: "+self.BrresGroup.KABrres)
            
    def KAMFile(self):
        self.BrresGroup.KAMBrres,_ = QtWidgets.QFileDialog.getOpenFileName(self)
        if not self.BrresGroup.KAMBrres:
            self.BrresGroup.KAMBrres = 0
            self.ErrorLabel.setText("No Brres File Selected (Multiplayer Kart)")
            return
        BNRBrres = open(self.BrresGroup.KAMBrres, "rb")
        BNRBrresData = BNRBrres.read(4).decode()
        BNRBrres.close
        if BNRBrresData != "bres":
            self.BrresGroup.KAMBrres = 0
            self.ErrorLabel.setText("Corrupted Multiplayer Kart Brres (Invalid Header)")
            return
        
        self.ErrorLabel.setText("Multiplayer Kart Brres at: "+os.path.basename(self.BrresGroup.KAMBrres))
        print("Multiplayer Kart Brres at: "+self.BrresGroup.KAMBrres)
        

def window():
    app = QApplication(sys.argv)
    win = MainWindow()

    win.show()
    sys.exit(app.exec_())

window()