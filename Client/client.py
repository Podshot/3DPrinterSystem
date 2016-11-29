import sys
from PySide import QtGui
import pyside_dynamic  # @UnresolvedImport
import api_wrapper  # @UnresolvedImport
import custom_widgets  # @UnresolvedImport

class LoginDialog(QtGui.QDialog):
    

    def login(self):
        username = self.username_field.text()
        password = self.password_field.text()
        wrapper = api_wrapper.APIWrapper(username, password)
        if wrapper.login_failed():
            self.failed_label.setVisible(True)
        else:
            self.parent()._wrapper = wrapper
            self.close()
    
    
    def init_ui(self):
        self.failed_label.setVisible(False)
        
        self.setGeometry(self.parent().x(), self.parent().y(), 400, 200)
        self.login_button.clicked.connect(self.login)
        self.cancel_button.clicked.connect(self.close)
    
    
    def __init__(self, parent=None):
        super(LoginDialog, self).__init__(parent)
        
        pyside_dynamic.loadUi('Login_Dialog.ui', self)
        
        self.init_ui()

class MainWindow(QtGui.QMainWindow):
    default_title_text = '<b>Submission Title:</b> '
    default_status_text = '<b>Status:</b> '

    def cell_selected(self, row, column):
        data = self.submissions[row]
        
        self.title_label.setText(self.default_title_text + data["title"])
        self.rafts_option.setChecked(data['options']['rafts'])
        self.supports_option.setChecked(data['options']["supports"])
        
    def update_table(self):
        self.submissions = self._wrapper.get_all_submissions()
        
        self.submissions_table.setRowCount(len(self.submissions))
        for row in xrange(self.submissions_table.rowCount()):
            item_title = QtGui.QTableWidgetItem(self.submissions[row]["title"])
            item_priority = QtGui.QTableWidgetItem(str(self.submissions[row]['priority']))
            setattr(item_title, 'id', self.submissions[row]['id'])
            setattr(item_priority, 'id', self.submissions[row]['id'])
            self.submissions_table.setItem(row, 0, item_title)
            self.submissions_table.setItem(row, 1, item_priority)
            
    
    def login(self):
        dialog = LoginDialog(self)
        
        dialog.exec_()
        
        if self._wrapper:
            self.actionSignIn.setVisible(False)
            self.actionSignOut.setVisible(True)
            self.statusBar.showMessage('Logged in as: {}'.format(self._wrapper.get_username()))
            self.update_table()
    
    
    def init_ui(self):
        self.statusBar.showMessage('Not logged in')
        
        self.actionSignIn.triggered.connect(self.login)
        
        self.actionExit.triggered.connect(self.close)
        
        self.submissions_table.cellClicked.connect(self.cell_selected)
        self.test_button.clicked.connect(self.on_test_button_clicked)
        
        self.show()
    
    
    def __init__(self):
        super(MainWindow, self).__init__()
        custom_widgets_map = {
                          'QReadOnlyCheckBox': custom_widgets.QReadOnlyCheckBox
                          }
        pyside_dynamic.loadUi("Main_Window.ui", self, custom_widgets_map)
        
        self._wrapper = None
        
        self.submissions = []
        
        self.init_ui()
        
    def on_test_button_clicked(self):
        print "Test!"


if __name__ == "__main__":
    app = QtGui.QApplication(sys.argv)
    window = MainWindow()
    sys.exit(app.exec_())
