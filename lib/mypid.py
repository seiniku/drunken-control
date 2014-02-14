#wtf
import time
class mypid(object):
    def __init__(self,kp=1.0, ki=1.0, kd=1.0, history_depth=-1):
        self.kp = kp
        self.ki = ki
        self.kd = kd
        self.history_depth = history_depth
        self.target = 0.0
        self.last_time = None
        self.previous_error = 0.0
        self.integral = 0.0
        self.history = [0] * history_depth 
        self.previous_value = 0.0



    def set_target(self, target):
        self.target = target

    def reset(self):
        self.previous_error = 0.0
        self.integral = 0.0
        self.last_time = None
        self.previous_value = 0.0

    def get_error(self,value):
        out = self.target - value
        current_time = time.time()
        if self.last_time is None:
            delta_time = 1
        else:
            delta_time = current_time - self.last_time
        self.last_time = current_time
        return out, delta_time

    def get_proportional(self,error):
        return self.kp * error

    def get_derivative(self, value, delta_time):
        return self.kd * ((value - self.previous_value)/delta_time);

    def get_integral(self, error, delta_time):
        #classic
        self.integral += self.ki * error * delta_time

        #with_history
        if self.history_depth != -1:
            self.history.append(self.ki * error * delta_time)
            self.history = self.history[(self.history_depth-1):] #keeps the last n items of the list
            self.integral += float(sum(self.history)) / float(self.history_depth)
        if self.integral > 100:
            self.integral = 100
        elif self.integral < 0:
            self.integral = -100
        return self.integral 

    def get_duty(self, value, target):
        minlimit = 0
        maxlimit = 100
        self.target = target
        err, delta_time = self.get_error(value)
        duty = self.get_proportional(err) + self.get_integral(err,delta_time) - self.get_derivative(value,delta_time)
        self.previous_error = err
        self.previous_value = value
        if duty > maxlimit:
            duty = maxlimit
        elif duty < minlimit:
            duty = minlimit
        
        print str(value) + '/' + str(target) + ' duty: '+ str(duty) + ' integral: ' + str(self.integral)
        return duty



#proportional = kp*diff
#deriv = Kd*rate of change
#integ = Ki*sum of errors

if __name__=="__main__":
   # pid = mypid(history_depth=3)
    pid = mypid(kp=1, ki=1, kd=1)
    print pid.get_duty(34,150)
    time.sleep(2)
    print pid.get_duty(38,150)
    time.sleep(2)
    print pid.get_duty(50,150)
    time.sleep(2)
    print pid.get_duty(60,150)
    time.sleep(2)
    print pid.get_duty(76,150)
    time.sleep(2)
    print pid.get_duty(90,150)
    time.sleep(2)
    print pid.get_duty(110,150)
    time.sleep(2)
    print pid.get_duty(130,150)
    time.sleep(2)
    print pid.get_duty(150,150)
    time.sleep(2)
    print pid.get_duty(160,150)
    time.sleep(2)
