from mpf.core.mode import Mode

class Base(Mode):

    colors = ("white","yellow","red","green","blue","orange","magenta","cyan","purple")

    def mode_start(self, **kwargs):
        # When the two top targets have been hit, change bumper colors
        self.player.jetBumperMultiplier = 1
        self.add_mode_event_handler('sg_jetbumptargets_complete', self.bumperUpgrade)

    def bumperUpgrade( self, **kwargs ):
        self.player.jetBumperMultiplier += 1
        indVal = (self.player.jetBumperMultiplier-1)%9
        c = Base.colors[ indVal ]
        self.machine.lights.l_jet_bump_t.color( c )
        self.machine.lights.l_jet_bump_tl.color( c )
        self.machine.lights.l_jet_bump_tr.color( c )

        