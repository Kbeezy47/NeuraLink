# src/pid.py

class PID:
    """A simple Proportional-Integral-Derivative (PID) controller."""
    def __init__(self, Kp, Ki, Kd, setpoint=0):
        self.Kp, self.Ki, self.Kd = Kp, Ki, Kd
        self.setpoint = setpoint
        self._prev_error, self._integral = 0, 0

    def update(self, process_value):
        error = self.setpoint - process_value
        self._integral += error
        derivative = error - self._prev_error
        output = self.Kp * error + self.Ki * self._integral + self.Kd * derivative
        self._prev_error = error
        return output

    def reset(self):
        self._integral, self._prev_error = 0, 0