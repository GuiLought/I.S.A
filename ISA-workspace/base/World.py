import Constants
from Character import Character

class World():
    def __init__(self,surface,draw):
        self.surface = surface
        self.draw = draw
        self.player = None
        self.world_data = None
    
    def update (self,screen_scroll):
        self.player.update()
        self.player.move(screen_scroll)
        
        
        