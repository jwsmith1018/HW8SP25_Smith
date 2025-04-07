#region imports
import numpy as np
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg
from matplotlib.figure import Figure
import PyQt5.QtWidgets as qtw
from PyQt5.QtWidgets import QFileDialog, QVBoxLayout, QLabel, QPushButton, QWidget, QApplication, QHBoxLayout, QLineEdit
import sys

# importing from previous work on least squares fit
from LeastSquares import LeastSquaresFit_Class
#endregion

#region class definitions
class Pump_Model():
    """
    Model class for storing pump data and least squares fit results.
    """
    def __init__(self):
        self.PumpName = ""
        self.FlowUnits = ""
        self.HeadUnits = ""

        self.FlowData = np.array([])
        self.HeadData = np.array([])
        self.EffData = np.array([])

        self.HeadCoefficients = np.array([])
        self.EfficiencyCoefficients = np.array([])

        self.LSFitHead = LeastSquaresFit_Class()
        self.LSFitEff = LeastSquaresFit_Class()

class Pump_Controller():
    """
    Controller class for handling logic between view and model.
    """
    def __init__(self):
        self.Model = Pump_Model()
        self.View = Pump_View()

    #region functions to modify data of the model
    def ImportFromFile(self, data):
        self.Model.PumpName = data[0].strip()
        L = data[2].split()
        self.Model.FlowUnits = L[0]
        self.Model.HeadUnits = L[1]
        self.SetData(data[3:])
        self.updateView()

    def SetData(self, data):
        self.Model.FlowData = np.array([])
        self.Model.HeadData = np.array([])
        self.Model.EffData = np.array([])

        for L in data:
            Cells = L.strip().split()
            self.Model.FlowData = np.append(self.Model.FlowData, float(Cells[0]))
            self.Model.HeadData = np.append(self.Model.HeadData, float(Cells[1]))
            self.Model.EffData = np.append(self.Model.EffData, float(Cells[2]))

        self.LSFit()

    def LSFit(self):
        self.Model.LSFitHead.x = self.Model.FlowData
        self.Model.LSFitHead.y = self.Model.HeadData
        self.Model.LSFitHead.LeastSquares(3)

        self.Model.LSFitEff.x = self.Model.FlowData
        self.Model.LSFitEff.y = self.Model.EffData
        self.Model.LSFitEff.LeastSquares(3)
    #endregion

    #region functions interacting with view
    def setViewWidgets(self, w):
        self.View.setViewWidgets(w)

    def updateView(self):
        self.View.updateView(self.Model)
    #endregion

class Pump_View():
    """
    View class to display the pump model data using a GUI and matplotlib.
    """
    def __init__(self):
        self.LE_PumpName = QLineEdit()
        self.LE_FlowUnits = QLineEdit()
        self.LE_HeadUnits = QLineEdit()
        self.LE_HeadCoefs = QLineEdit()
        self.LE_EffCoefs = QLineEdit()
        self.ax = None
        self.canvas = None

    def updateView(self, Model):
        self.LE_PumpName.setText(Model.PumpName)
        self.LE_FlowUnits.setText(Model.FlowUnits)
        self.LE_HeadUnits.setText(Model.HeadUnits)
        self.LE_HeadCoefs.setText(Model.LSFitHead.GetCoeffsString())
        self.LE_EffCoefs.setText(Model.LSFitEff.GetCoeffsString())
        self.DoPlot(Model)

    def DoPlot(self, Model):
        headx, heady, headRSq = Model.LSFitHead.GetPlotInfo(3, npoints=500)
        effx, effy, effRSq = Model.LSFitEff.GetPlotInfo(3, npoints=500)

        self.ax.clear()
        ax1 = self.ax
        ax2 = ax1.twinx()

        ax1.plot(Model.FlowData, Model.HeadData, 'bo', label='Head Data')
        ax1.plot(headx, heady, 'b-', label=f'Head Fit (R²={headRSq:.4f})')

        ax2.plot(Model.FlowData, Model.EffData, 'rs', label='Eff. Data')
        ax2.plot(effx, effy, 'r-', label=f'Eff. Fit (R²={effRSq:.4f})')

        ax1.set_xlabel(f"Flow Rate ({Model.FlowUnits})")
        ax1.set_ylabel(f"Head ({Model.HeadUnits})", color='b')
        ax2.set_ylabel("Efficiency (%)", color='r')

        ax1.tick_params(axis='y', labelcolor='b')
        ax2.tick_params(axis='y', labelcolor='r')

        ax1.set_title(f"Performance Curves for {Model.PumpName}")
        ax1.legend(loc='upper left')
        ax2.legend(loc='upper right')

        self.canvas.draw()

    def setViewWidgets(self, w):
        self.LE_PumpName, self.LE_FlowUnits, self.LE_HeadUnits, self.LE_HeadCoefs, self.LE_EffCoefs, self.ax, self.canvas = w
#endregion

#region main app
class MainApp(QWidget):
    def __init__(self):
        super().__init__()
        self.controller = Pump_Controller()
        self.initUI()

    def initUI(self):
        layout = QVBoxLayout()

        # Top controls
        self.btnLoad = QPushButton("Load File")
        self.btnLoad.clicked.connect(self.loadData)
        layout.addWidget(self.btnLoad)

        self.lePumpName = QLineEdit()
        self.leFlowUnits = QLineEdit()
        self.leHeadUnits = QLineEdit()
        self.leHeadCoefs = QLineEdit()
        self.leEffCoefs = QLineEdit()

        layout.addWidget(QLabel("Pump Name"))
        layout.addWidget(self.lePumpName)
        layout.addWidget(QLabel("Flow Units"))
        layout.addWidget(self.leFlowUnits)
        layout.addWidget(QLabel("Head Units"))
        layout.addWidget(self.leHeadUnits)
        layout.addWidget(QLabel("Head Coefficients"))
        layout.addWidget(self.leHeadCoefs)
        layout.addWidget(QLabel("Efficiency Coefficients"))
        layout.addWidget(self.leEffCoefs)

        # Plot
        self.fig = Figure(figsize=(6, 4))
        self.canvas = FigureCanvasQTAgg(self.fig)
        self.ax = self.fig.add_subplot(111)
        layout.addWidget(self.canvas)

        self.setLayout(layout)
        self.setWindowTitle("Pump Performance GUI")

        # Provide widgets to controller
        w = (self.lePumpName, self.leFlowUnits, self.leHeadUnits, self.leHeadCoefs, self.leEffCoefs, self.ax, self.canvas)
        self.controller.setViewWidgets(w)

    def loadData(self):
        fname, _ = QFileDialog.getOpenFileName(self, 'Open file', '', "Text files (*.txt)")
        if fname:
            with open(fname, 'r') as file:
                data = file.readlines()
                self.controller.ImportFromFile(data)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = MainApp()
    ex.show()
    sys.exit(app.exec_())
#endregion
