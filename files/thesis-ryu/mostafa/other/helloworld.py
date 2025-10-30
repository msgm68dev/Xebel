from ryu.base import app_manager

class MyHello(app_manager.RyuApp):
    def __init__(self, *args, **kwargs):
        super(MyHello, self).__init__(*args, **kwargs)
