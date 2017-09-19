from mpf.core.mode import Mode
from numpy import zeros, uint8

class Bonus10(Mode):

    def mode_start(self, **kwargs):
        # When the two top targets have been hit, change bumper colors
        # self.player.jetBumperMultiplier = 1
        self.add_mode_event_handler('shot_adv_bonus_hit', self.hit)
        self.bls = [ getattr( self.machine.lights, "l_bonus{}".format(i) ) for i in range(10) ]
        self.cs = zeros(30,dtype=uint8).reshape((3,10))
        self.hit()

    def colorSet(self):
    	for i, bl in enumerate(self.bls):
    		bl.color( self.cs[:,i].tolist() )

    def mode_stop(self, **kwargs):
    	self.cs[:] = 0
    	self.colorSet()

    def hit( self, **kwargs ):
        self.cs[:,:self.player.bonusHitCount] = 175
        self.colorSet()
        