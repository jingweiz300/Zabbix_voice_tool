import pyforms
#from pyforms.basewidget import BaseWidget
from pyforms.basewidget import BaseWidget
from pyforms.controls   import ControlButton
from pyforms.controls import ControlText
from pyforms_gui.controls import control_password
from pyforms_gui.controls.control_list import ControlList
from pyforms_gui.controls.control_textarea import ControlTextArea
from pyforms_gui.controls.control_combo import ControlCombo
from pyforms_gui.controls.control_label import ControlLabel
from pyforms_gui.controls.control_mdiarea import ControlMdiArea
from pyforms_gui.controls.control_file import ControlFile

class myclass(BaseWidget):
    def __init__(self):
        super().__init__('apple')
        self._firstname = ControlText('First name', default='Chris')
        self._middlename = ControlText('Middle name')
        self._lastname   = control_password.ControlPassword('password',default='123456')
        self._fullname   = ControlText('fullname name')
        self._button     = ControlButton('Press this button')
        self._peopleList    = ControlList('arg1','arg2')
        self._testlabel    = ControlLabel('label')
        self._testmdiarea    = ControlMdiArea('ControlMdiArea')
        self._button.value = self.__buttonAction
        self._testfile = ControlFile('file')
        self._peopleList = ControlList('People', plusFunction=self.__addPersonBtnAction,
                                       minusFunction=self.__rmPersonBtnAction)
        self._peopleList.horizontalHeaders = ['First name', 'Middle name', 'password']
        self._peopleList += ['1','2','3']
    def __buttonAction(self):
        self._peopleList.init_form()

if __name__ == "__main__": pyforms.start_app( myclass )