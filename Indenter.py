import threading
import time

#custom  class imports
from StepperController import *
from ADCController import *
from Logger import *
from hx711 import HX711

class Indenter():

    def __init__(self, mplWidget):
        self.MPLWidget = mplWidget
        
        # set up the motor controller and ADC controller
        self.Stepper = StepperController(16)
        self.ADC = ADCController()
        self.Logger = Logger()

        self.x = []
        self.step = []
        self.load = []


    def loadAndShowResults(self, filename):
        self.x, self.step, self.load = self.Logger.loadFile(filename)
        self.MPLWidget.plotData(self.x, self.step, self.load)


    def saveResults(self, filename):
        self.Logger.saveFile(filename, self.x, self.step, self.load)


    def compareResults(self, filename):
        # to be implemented - load data from another CSV and overlay it on the current graph
        pass


    def startJogUp(self):
        self.Stepper.startMovingUp(2000)


    def stopJogging(self):
        self.Stepper.stopMoving()


    def startJogDown(self):
        self.Stepper.startMovingDown(2000)


    def takeStiffnessMeasurement(self, load):
        # launch a thread to handle taking the stiffness measurement
        #TODO: make sure that only one instance of this thread runs at a time!!!
        self.measurementLoopHandle = threading.Thread(name = 'measurementLoop', target = measurementLoop, args=(load, 1500 ))
        self.measurementLoopHandle.start()


    def emergencyStop(self):
        global killMeasurement
        # terminate the thread doing the stiffness measurement
        killMeasurement = True

        # TODO: start backing off the indenter to the home position here
        self.Stepper.stopMoving()

        print("stopped")


    def shutdown(self):
        Stepper.stopMoving()


killMeasurement = False
displacement = 0
TOLERANCE = 50
def measurementLoop(targetLoad, stepRate):
    global killMeasurement, displacement
    
    # set up the HX711
    #hx = HX711(5, 6)
    hx = HX711(29, 31)
    hx.set_offset(8214368.3125)
    hx.set_scale(243.8564841498559)
    stepper = StepperController(16)
    displacement = 0
    killMeasurement = False
    
    try:
        # move down until the target load is achieved
        load = hx.get_grams()
        stepper.startMovingDown(stepRate)
        while(load < targetLoad and not killMeasurement):
            hx.power_down()
            time.sleep(.001)
            hx.power_up()
            load = hx.get_grams()
            # TODO: log new data point here
            #print(stepper.getDisplacement())
        displacement = stepper.stopMoving()
        
        # TODO: delete me once next section works properly
        time.sleep(2)
        
        # once the target load is achieved, dwell at the target load for some time
        # TODO: make sure load is maintained for the dwell time by moving the indenter up and down
        # startTime = time.time()
        # while time.time() < startTime + 2:
        #     hx.power_down()
        #     hx.power_up()
        #     load = hx.get_grams()
            
        #     if load > (targetLoad + TOLERANCE):
        #         # move up
        #         displacement += stepper.stopMoving()
        #         stepper.startMovingUp(stepRate)

        #     elif load < (targetLoad - TOLERANCE):
        #         # move down
        #         displacement += stepper.stopMoving()
        #         stepper.startMovingDown(stepRate)

        #     else:
        #         # stop moving
        #         displacement += stepper.stopMoving()
            
        #     # TODO: log new data point here
        #     #print(stepper.getDisplacement())

        # move the indenter up by the number of steps we moved it down
        # TODO: implement the above comment
        stepper.startMovingUp(stepRate)
        while(abs(displacement) > abs(stepper.getDisplacement()) and not killMeasurement):
            hx.power_down()
            time.sleep(.001)
            hx.power_up()
            load = hx.get_grams()
            
            #TODO: log data here
            
        stepper.stopMoving()
        
    except (KeyboardInterrupt, SystemExit):
        stepper.stopMoving()
        cleanAndExit()

    return