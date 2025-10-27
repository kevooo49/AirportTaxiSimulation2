class AirportModel:
    def __init__(self):
        self.airplanes = []
        self.schedule = []

    def step(self):
        for airplane in self.airplanes:
            airplane.move()
            if airplane.position == "runway":
                airplane.land()

    def schedule_airplanes(self, airplane):
        self.schedule.append(airplane)