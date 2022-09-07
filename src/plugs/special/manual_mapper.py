"""
plugs > manual_mapper.py

Contains code used to manually map control surface events to CC events in the
case where said events aren't handled.

This mapping is done by taking a snapshot of available device controls and
then assigning each control an index which it will output.

Authors:
* Miguel Guthridge [hdsq@outlook.com.au, HDSQ#2154]

This code is licensed under the GPL v3 license. Refer to the LICENSE file for
more details.
"""

from common.extension_manager import ExtensionManager
from control_surfaces import (
    Fader,
    Knob,
    ModXY,
    ControlShadowEvent,
)
from devices import DeviceShadow
from plugs import SpecialPlugin

# Only assign to CC values that are undefined by the MIDI spec
AVAILABLE_CCS = (
    [3, 9, 14, 15]
    + list(range(20, 32))
    + list(range(85, 91))
    + list(range(102, 120))
)
NUM_CCS = len(AVAILABLE_CCS)  # = 40

# After this, we cycle through all 16 channels to give 640 total events
# available, which should be more than enough for reasonable people.


class ManualMapper(SpecialPlugin):
    """
    A plugin that manually maps controls from faders, knobs and various other
    controls into CC events that users can manually assign to parameters.
    """

    def __init__(self, shadow: DeviceShadow) -> None:
        shadow.setMinimal(True)
        self._faders_start = 0
        self._knobs_start = len(shadow.bindMatches(
            Fader,
            self.eFaders,
            allow_substitution=False
        ))
        self._mods_start = len(shadow.bindMatches(
            Knob,
            self.eKnobs,
            allow_substitution=False
        )) + self._knobs_start
        shadow.bindMatches(
            ModXY,
            self.eMods,
            allow_substitution=False
        )
        super().__init__(shadow, [])

    @classmethod
    def create(cls, shadow: DeviceShadow) -> 'SpecialPlugin':
        return cls(shadow)

    @classmethod
    def shouldBeActive(cls) -> bool:
        return True

    @staticmethod
    def getChannelAndCc(index: int) -> tuple[int, int]:
        """
        Returns the channel and CC number that should be assigned to an event
        given the index of that event

        ### Args:
        * `index` (`int`): index of event

        ### Returns:
        * `tuple[int, int]`: MIDI channel and CC number
        """
        return (index // NUM_CCS), (AVAILABLE_CCS[index % NUM_CCS])

    @classmethod
    def editEvent(cls, control: ControlShadowEvent, start: int) -> bool:
        """
        Edits the event to make it into a CC event that can be processed by FL
        Studio
        """
        channel, cc = cls.getChannelAndCc(start + control.coordinate[1])
        control.midi.status = (0xB << 4) + channel
        control.midi.data1 = cc
        control.midi.data2 = int(control.value * 127)
        return False

    def eFaders(self, control: ControlShadowEvent, *args) -> bool:
        return self.editEvent(control, self._faders_start)

    def eKnobs(self, control: ControlShadowEvent, *args) -> bool:
        return self.editEvent(control, self._knobs_start)

    def eMods(self, control: ControlShadowEvent, *args) -> bool:
        return self.editEvent(control, self._mods_start)


ExtensionManager.special.register(ManualMapper)
