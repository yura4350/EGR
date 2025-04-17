import time
import threading
from collections import deque
import Adafruit_ADS1x15

class PulseSensorReader(threading.Thread):
    """
    Background thread that reads from the ADS1015 + pulse sensor,
    computes an average BPM over the last N beats, and stores the
    most recent value in self.bpm.
    """
    def __init__(self, channel=0, gain=2/3, buffer_size=10):
        super().__init__(daemon=True)
        self.adc = Adafruit_ADS1x15.ADS1015(busnum=1)
        self.channel = channel
        self.gain = gain

        # algorithm state
        self.thresh = 525
        self.P = 512
        self.T = 512
        self.lastBeatTime = 0
        self.sampleCounter = 0
        self.firstBeat = True
        self.secondBeat = False
        self.Pulse = False
        self.IBI = 600
        self.rate_buf = deque(maxlen=buffer_size)
        self.bpm = 0

        self._running = True

    def run(self):
        lastTime = int(time.time() * 1000)

        while self._running:
            signal = self.adc.read_adc(self.channel, gain=self.gain)
            curTime = int(time.time() * 1000)
            self.sampleCounter += (curTime - lastTime)
            lastTime = curTime
            N = self.sampleCounter - self.lastBeatTime

            # find trough
            if signal < self.thresh and N > (self.IBI / 5.0) * 3.0:
                if signal < self.T:
                    self.T = signal

            # find peak
            if signal > self.thresh and signal > self.P:
                self.P = signal

            # look for heartbeat
            if N > 250:
                if (signal > self.thresh) and (not self.Pulse) and (N > (self.IBI / 5.0) * 3.0):
                    self.Pulse = True
                    self.IBI = self.sampleCounter - self.lastBeatTime
                    self.lastBeatTime = self.sampleCounter

                    if self.secondBeat:
                        self.secondBeat = False
                        self.rate_buf.extend([self.IBI] * self.rate_buf.maxlen)

                    if self.firstBeat:
                        self.firstBeat = False
                        self.secondBeat = True
                        # discard first beat
                        continue

                    # compute rolling average
                    self.rate_buf.append(self.IBI)
                    running_total = sum(self.rate_buf) / len(self.rate_buf)
                    self.bpm = 60000.0 / running_total

            # reset after no beat found
            if signal < self.thresh and self.Pulse:
                self.Pulse = False
                amp = self.P - self.T
                self.thresh = amp / 2 + self.T
                self.P = self.thresh
                self.T = self.thresh

            if N > 2500:
                # no beat for 2.5s -> reset
                self.thresh = 512
                self.P = 512
                self.T = 512
                self.lastBeatTime = self.sampleCounter
                self.firstBeat = True
                self.secondBeat = False

            time.sleep(0.005)

    def stop(self):
        self._running = False