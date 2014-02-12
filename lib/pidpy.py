
class pidpy(object):
    ek_1 = 0.0  # e[k-1] = SP[k-1] - PV[k-1] = Tset_hlt[k-1] - Thlt[k-1]
    ek_2 = 0.0  # e[k-2] = SP[k-2] - PV[k-2] = Tset_hlt[k-2] - Thlt[k-2]
    xk_1 = 0.0  # PV[k-1] = Thlt[k-1]
    xk_2 = 0.0  # PV[k-2] = Thlt[k-1]
    yk_1 = 0.0  # y[k-1] = Gamma[k-1]
    yk_2 = 0.0  # y[k-2] = Gamma[k-1]
    lpf_1 = 0.0 # lpf[k-1] = LPF output[k-1]
    lpf_2 = 0.0 # lpf[k-2] = LPF output[k-2]
    
    yk = 0.0 # output
    
    GMA_HLIM = 100.0
    GMA_LLIM = 0.0
    
    def __init__(self, ts, kc, ti, td):
        self.kc = kc
        self.ti = ti
        self.td = td
        self.ts = ts
        self.k_lpf = 0.0
        self.k0 = 0.0
        self.k1 = 0.0
        self.k2 = 0.0
        self.k3 = 0.0
        self.lpf1 = 0.0
        self.lpf2 = 0.0
        self.ts_ticks = 0
        self.pid_model = 3
        self.pp = 0.0
        self.pi = 0.0
        self.pd = 0.0
        if (self.ti == 0.0):
            self.k0 = 0.0
        else:
            self.k0 = self.kc * self.ts / self.ti
        self.k1 = self.kc * self.td / self.ts
        self.lpf1 = (2.0 * self.k_lpf - self.ts) / (2.0 * self.k_lpf + self.ts)
        self.lpf2 = self.ts / (2.0 * self.k_lpf + self.ts) 
        
    def calcPID_reg4(self, xk, tset):
        ek = 0.0
        ek = tset - xk # calculate e[k] = SP[k] - PV[k]
        
        #-----------------------------------------------------------
        # Calculate PID controller:
        # y[k] = y[k-1] + kc*(PV[k-1] - PV[k] +
        # Ts*e[k]/Ti +
        # Td/Ts*(2*PV[k-1] - PV[k] - PV[k-2]))
        #-----------------------------------------------------------
        self.pp = self.kc * (pidpy.xk_1 - xk) # y[k] = y[k-1] + Kc*(PV[k-1] - PV[k])
        self.pi = self.k0 * ek  # + Kc*Ts/Ti * e[k]
        self.pd = self.k1 * (2.0 * pidpy.xk_1 - xk - pidpy.xk_2)
        pidpy.yk += self.pp + self.pi + self.pd
            
        pidpy.xk_2 = pidpy.xk_1  # PV[k-2] = PV[k-1]
        pidpy.xk_1 = xk    # PV[k-1] = PV[k]
        
        # limit y[k] to GMA_HLIM and GMA_LLIM
        if (pidpy.yk > pidpy.GMA_HLIM):
            pidpy.yk = pidpy.GMA_HLIM
        if (pidpy.yk < pidpy.GMA_LLIM):
            pidpy.yk = pidpy.GMA_LLIM
            
        return pidpy.yk
        

if __name__=="__main__":

    sampleTime = 2
    pid = PID(sampleTime,0,0,0)
    temp = 80
    setpoint = 100
    print pid.calcPID_reg4(temp, setpoint)
    
