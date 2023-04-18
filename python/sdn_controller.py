from mininet.node import Controller

class SDNController(Controller):
    def __init__(self, name, **kwargs):
        Controller.__init__(self, name, **kwargs)

        self.net = None

        if kwargs['net']:
            self.net = kwargs['net']
            print(self.net.get("s0"))

    def start(self):
        # Add your custom code to start the controller here
        print("Tjupapi")

    def stop(self):
        # Add your custom code to stop the controller here
        pass

