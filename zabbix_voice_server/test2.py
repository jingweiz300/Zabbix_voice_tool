import pyforms
from pyforms.basewidget import BaseWidget
from pyforms.controls   import ControlButton
from pyforms.controls import ControlText


class SimpleExample1(BaseWidget):

    def __init__(self):
        super(SimpleExample1,self).__init__('Simple example 1')

        #Definition of the forms fields
        self._firstname  = ControlText('First name', 'Default value')
        self._middlename = ControlText('Middle name')
        self._lastname   = ControlText('Lastname name')
        self._fullname   = ControlText('Full name')
        self._button     = ControlButton('Press this button')
        self._button.value = self.__buttonAction
        # Define the organization of the forms
        self.formset = [('_firstname', '_middlename', '_lastname'), '_button', '_fullname',
                        ' ']  # The ' ' is used to indicate that a empty space should be placed at the bottom of the window  # If you remove the ' ' the forms will occupy the entire window
        self.formset = [{'Tab1': ['_firstname', '||', '_middlename', '||', '_lastname'], 'Tab2': ['_fullname']}, '=',
            (' ', '_button', ' ')]
        self.mainmenu = [
            {'File': [{'Open': self.__openEvent}, '-', {'Save': self.__saveEvent}, {'Save as': self.__saveAsEvent}]},
            {'Edit': [{'Copy': self.__editEvent}, {'Past': self.__pastEvent}]}]


    def __openEvent(self):
        pass

    def __saveEvent(self):
        pass
    def __saveAsEvent(self):
        pass
    def __editEvent(self):
        pass
    def __pastEvent(self):
        pass
    def __buttonAction(self):
        """Button action event"""
        self._fullname.value = self._firstname.value + " " + self._middlename.value + " " + self._lastname.value
#Execute the application
if __name__ == "__main__": pyforms.start_app( SimpleExample1 )