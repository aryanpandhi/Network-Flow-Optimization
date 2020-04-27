class RMIDrum():
    
    drum = ''
    color = ''
    quantity = 0
    capacity = 0

    def __init__(self, drum, color, quantity, capacity):
        self.drum = drum
        self.color = color
        self.quantity = quantity
        self.capacity = capacity 

class PFIDrum():

    drum = ''
    quantity = 0
    capacity = 0
    color = None
    size = None

    def __init__(self, drum, capacity):
        self.drum = drum
        self.capacity = capacity

class PIDrum():

    drum = ''
    quantity = 0
    capacity = 0

    def __init__(self, drum, capacity):
        self.drum = drum
        self.capacity = capacity

