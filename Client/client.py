import sys
from PySide import QtGui
import pyside_dynamic
import api_wrapper
import custom_widgets

class MainWindow(QtGui.QMainWindow):
    default_title_text = '<b>Submission Title:</b>'

    def cell_selected(self, row, column):
        data = self.submissions[row]
        
        self.title_label.setText(self.default_title_text + " " + data["title"])
        self.rafts_option.setChecked(data['options']['rafts'])
        self.supports_option.setChecked(data['options']["supports"])
    
    def init_ui(self):
        self.submissions = api_wrapper.get_all_submissions()
        
        self.submissions_table.setRowCount(len(self.submissions))
        for row in xrange(self.submissions_table.rowCount()):
            item_title = QtGui.QTableWidgetItem(self.submissions[row]["title"])
            item_priority = QtGui.QTableWidgetItem(str(self.submissions[row]['priority']))
            setattr(item_title, 'id', self.submissions[row]['id'])
            setattr(item_priority, 'id', self.submissions[row]['id'])
            self.submissions_table.setItem(row, 0, item_title)
            self.submissions_table.setItem(row, 1, item_priority)
            
        self.submissions_table.cellClicked.connect(self.cell_selected)
        
        self.test_button.clicked.connect(self.on_test_button_clicked)
        
        self.show()
    
    
    def __init__(self):
        super(MainWindow, self).__init__()
        custom_widgets_map = {
                          'QReadOnlyCheckBox': custom_widgets.QReadOnlyCheckBox
                          }
        pyside_dynamic.loadUi("untitled.ui", self, custom_widgets_map)
        
        self.submissions = []
        
        self.init_ui()
        
    def on_test_button_clicked(self):
        print "Test!"


if __name__ == "__main__":
    app = QtGui.QApplication(sys.argv)
    window = MainWindow()
    sys.exit(app.exec_())
