class Airplane:
    def __init__(self, airplane_id, position):
        self.id = airplane_id
        self.position = position

    def move(self, new_position):
        self.position = new_position

    def land(self):
        self.position = 'landed'