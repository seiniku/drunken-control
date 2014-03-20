#translated from https://github.com/br3ttb/Arduino-PID-AutoTune-Library/blob/master/PID_AutoTune_v0/PID_AutoTune_v0.cpp
import time

class AutoTune(object):
    def __init__(value, output):
        self.value = value
        self.output = output
        self.controlType = 0 #default to PI
        self.noiseband = 0.25
        self.running = False
        self.oStep = 30
        self.nLookBack = 0
        self.sampleTime = 0
        SetLookbackSec(10)
        self.lastTime = Time.time()
        self.lastInputs[0,0]        
        
        ###?
        self.peaks = []
        self.peakType = 0
        self.peakCount = 0
        justChanged = False
        self.absMax = 0
        self.absMin = 0 
        self.setpoint = 0 
        self.outputStart = self.output
    def cancel(self):
        self.running = False
    
    def runtime(self):
        #??
        justevaled = False
        if peakCount > 9 and self.running:
            self.running = False
            FinishUp() ######madness
            return 1 #??????
        now = Time.time()
        
        #not sure about this one either
        if (now - self.lastTime) < self.sampleTime:
            return false

        self.lastTime = now
        refval = self.value
        justevaled = True

        if not self.running:
            #init working vars
            self.absMax = refval
            self.absMin = refval
            self.setpoint = refval
            running = True
            self.outputStart = self.output
            self.output = self.outputStart + self.oStep

        else:
            if refVal > self.absMax:
                self.absMax = refVal
            if refVal < self.absMin:
                self.absMin = refVal

        #oscillate the output base on the input's relation to setpoint
        if refVal > (setpoint + self.noiseBand):
            self.output = outputStart - self.oStep
        elif refVal < (setpoint - noiseBand):
            self.output = outputStart + self.oStep

        #weird spot for this..
        
        isMax = refVal == max(self.lastInputs)
        isMin = refVal == min(self.lastInputs)
        self.lastInputs.append(refVal)
        if len(lastInputs) > self.nLookBack:
            self.lastInputs.pop(0)

        #such bad
        #uh, if lastInputs isn't full then don't do mathsz?
        if len(self.lastInputs) < self.nLookBack:
            return 0

        if (isMax):
            if self.peakType==0:
                self.peakType = 1
            if self.peakType ==-1:
                self.peakType = 1
                self.justchanged=True
                self.peak2 = peak1
            self.peak1 = now
            self.peaks[self.peakCount] = refVal

        elif (isMin):
            if self.peakType == 0:
                self.peakType = -1
            if self.peaktype == 1:
                self.peakType = -1
                self.peakCount += 1
                self.justchanged = True

            if self.peakCount < 10:
                self.peaks[self.peakCount] = refVal

        if self.justchanged and self.peakCount > 2:
#try to tune    
            avgSeperation = (abs(self.peaks[self.peakCount-1]-self.peaks[self.peakCount-2]




#this doesn't make much sense either
    def setLoopbackSec(self,value):
        if value < 1:
            value = 1
        if value < 25:
            self.nLookBack = value * 4
            self.sampleTime = 250
        else:
            self.nLookBack = 100
            self.sampleTime = value * 10
    
    def getLoopbackSec(self):
        return self.nLoopBack * self.sampleTime / 1000

    def setNoiseBand(self,band):
        self.noiseband = band
    
    def getNoiseBand(self):
        return self.noiseband

    #why is this a magic number.. 0 = PI, 1 = PID
    def setControlType(self,value):
        self.controlType = value

    def getControlType(self):
        return self.controlType
    
    def setOutputStep(self,step):
        self.oStep = step
    
    def getOutputStep(self):
        return self.oStep

    def getKp(self, ku):
        if self.controlType == 1:
            kp = 0.6 * ku
        else:
            kp = 0.4 * ku
        return kp

    def getKi(self,ku,pu):
        if self.controlType == 1:
            ki = 1.2 * ku / pu
        else:
            ki = 0.48 * ku / pu
        return ki

    def getKd(self, ku, pu):
        if self.controlType == 1:
            kd = 0.075 * ku * pu
        else kd = 0
        return kd



