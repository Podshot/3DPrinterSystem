import sys
from PySide import QtGui, QtCore
import pyside_dynamic
import api_wrapper
import custom_widgets
from datetime import datetime
import os
import subprocess
import win32api

def calculate_position(parent, width, height):
    return (parent.x() + ((parent.width() / 2) - (width / 2)), parent.y() + ((parent.height() / 2) - (height / 2)))

def get_drives():
    drives = win32api.GetLogicalDriveStrings()
    drives = drives.split('\000')[:-1]
    return drives

class DriveSelectionDialog(QtGui.QDialog):
    
    def generate_function(self, drive):
        
        def func():
            setattr(self.parent(), "_sd_drive", drive)
        
        return func

    def init_ui(self):
        drives = get_drives()
        y = 35
        
        for i in xrange(len(drives)): # Use an integer loop to make Y positioning easier
            r_button = QtGui.QRadioButton(drives[i], self)
            r_button.toggled.connect(self.generate_function(drives[i]))
            r_button.setGeometry(25, y + (25 * i), 82, 17)
        
        self.button_widget.setGeometry(10, y + (len(drives) * 25), 240, 40)
        
        self.confirm_button.clicked.connect(self.close)
        self.cancel_button.clicked.connect(self.close)
        
        pos = calculate_position(self.parent(), 260, (y + 45) + (len(drives) * 25))
        self.setGeometry(pos[0], pos[1], 260, (y + 45) + (len(drives) * 25))
        
        self.show()
    
    def __init__(self, parent=None):
        super(DriveSelectionDialog, self).__init__(parent)
        
        pyside_dynamic.loadUi('Drive_Dialog.ui', self)
        
        self.init_ui()

class AccountEditingDialog(QtGui.QDialog):
    

    def fetch_user(self):
        username = self.name_field.text()
        user = self._wrapper.get_user(username)
        
        self.robotics_checkbox.setChecked(user['robotics'])
        self.admin_checkbox.setChecked(user['admin'])
    

    def blacklist_change(self, state):
        if state == QtCore.Qt.Checked:
            self.blacklist_reason_field.setVisible(True)
            self.blacklist_reason_label.setVisible(True)
        else:
            self.blacklist_reason_field.setVisible(False)
            self.blacklist_reason_label.setVisible(False)
    
    
    def init_ui(self):
        
        pos = calculate_position(self.parent(), 400, 200)
        self.setGeometry(pos[0], pos[1], 400, 200)
        
        self.blacklist_reason_field.setVisible(False)
        self.blacklist_reason_label.setVisible(False)
        
        self.fetch_button.clicked.connect(self.fetch_user)
        self.blacklisted_checkbox.stateChanged.connect(self.blacklist_change)
        
        self.show()
    
    def __init__(self, parent=None):
        super(AccountEditingDialog, self).__init__(parent)
        
        pyside_dynamic.loadUi('Account_Dialog.ui', self)
        
        self._wrapper = self.parent()._wrapper
        self.init_ui()

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
        
        pos = calculate_position(self.parent(), 400, 200)
        self.setGeometry(pos[0], pos[1], 400, 200)
        self.login_button.clicked.connect(self.login)
        if self._can_cancel:
            self.cancel_button.clicked.connect(self.close)
        else:
            self.cancel_button.clicked.connect(sys.exit)
    
    
    def __init__(self, parent=None, can_cancel=True):
        super(LoginDialog, self).__init__(parent)
        
        pyside_dynamic.loadUi('Login_Dialog.ui', self)
        
        self._can_cancel = can_cancel
        
        self.init_ui()

class MainWindow(QtGui.QMainWindow):
    default_options_text = '''<html><head/><body><p><span style=" font-size:9pt; font-weight:600;">{}: </span>{}</p></body></html>'''
    
    table_items = ["item_title", 'item_priority', 'item_date', 'item_for_robotics']
    
    def prepare_model(self, submission_id):
        
        def func():
            os.startfile(os.path.join('submissions', '{}.stl'.format(submission_id)))
            
        return func
    
    def generate_row(self, row, submission):
        data = {}
        for (key, value) in submission.iteritems():
            if key == 'date':
                obj = QtGui.QTableWidgetItem(str(datetime.strptime(submission['date'], "%B %d, %Y at %I:%M %p")))
            else:
                obj = QtGui.QTableWidgetItem(str(value))
            setattr(obj, 'submission_id', submission['id'])
            data["item_" + key] = obj
        for i in xrange(len(self.table_items)):
            self.submissions_table.setItem(row, i, data.get(self.table_items[i]))
            
    def download_submission(self, sub_id):
        
        def func():
            self.download_progressbar.setRange(0, 100)
            percentage = self._wrapper.download_submitted_file(sub_id, os.path.join(os.path.dirname(os.path.abspath(__file__)), "submissions"))
            for per in percentage:
                if isinstance(per, float):
                    self.download_progressbar.setValue(per)
            self.prepare_button.setEnabled(True)
        
        return func
    
    def mark_submission(self, sub_id, status):
        
        def func():
            self._wrapper.mark_submission(sub_id, status)
            
        return func
    
    def show_completed_change(self, state):
        if state == QtCore.Qt.Checked:
            self.submissions_table.setRowCount(len(self._all_submissions))
            for row in xrange(self.submissions_table.rowCount()):
                self.generate_row(row, self._all_submissions[row])
        else:
            self.submissions_table.setRowCount(len(self.submissions))
            for row in xrange(self.submissions_table.rowCount()):
                self.generate_row(row, self.submissions[row])
        
    def cell_selected(self, row, column):
        submission_id = self.submissions_table.item(row, column).submission_id
        data = self.submission_map[submission_id]
        
        self.title_label.setText(self.default_options_text.format("Submission Title", data['title']))
        
        self.rafts_option.setChecked(data['options']['rafts'])
        self.supports_option.setChecked(data['options']["supports"])
        
        self.color_label.setText(self.default_options_text.format("Color", data['options']['color'].capitalize()))
        self.infill_label.setText(self.default_options_text.format('Infill', str(data['options']['infill']) + '%'))
        
        self.class_course_label.setText(self.default_options_text.format('Course Name', data['assignment'].get('class_name', '')))
        self.class_teacher_label.setText(self.default_options_text.format('Teacher', data['assignment'].get('teacher', '')))
        self.class_due_date_label.setText(self.default_options_text.format('Due Date', data['assignment'].get('due_date', '')))
        
        self.scale_x_label.setText(str(float(data['options'].get("scale", (1, 1, 1))[0])))
        self.scale_y_label.setText(str(float(data['options'].get("scale", (1, 1, 1))[1])))
        self.scale_z_label.setText(str(float(data['options'].get("scale", (1, 1, 1))[2])))
        
        self.rotation_x_label.setText(str(float(data['options'].get("rotation", (0, 0, 0))[0])))
        self.rotation_y_label.setText(str(float(data['options'].get("rotation", (0, 0, 0))[1])))
        self.rotation_z_label.setText(str(float(data['options'].get("rotation", (0, 0, 0))[2])))  
        
        try:
            self.download_button.clicked.disconnect()
        except:
            pass
        
        self.download_button.clicked.connect(self.download_submission(submission_id))
        
        try:
            self.completed_button.clicked.disconnect()
            self.pending_button.clicked.disconnect()
            self.denied_button.clicked.disconnect()
        except:
            pass
        
        self.completed_button.clicked.connect(self.mark_submission(submission_id, 'completed'))
        self.pending_button.clicked.connect(self.mark_submission(submission_id, 'pending'))
        self.denied_button.clicked.connect(self.mark_submission(submission_id, 'denied'))
        
        exists = os.path.exists(os.path.join(os.path.dirname(os.path.abspath(__file__)), "submissions", '{}.stl'.format(submission_id)))
        
        if exists:
            self.prepare_button.setEnabled(True)
        else:
            self.prepare_button.setEnabled(False)
            
        try:
            self.prepare_button.clicked.disconnect()
        except:
            pass
        
        self.prepare_button.clicked.connect(self.prepare_model(submission_id))
        self.repaint()
        
    def update_table(self):
        self._all_submissions = self._wrapper.get_all_submissions()
        for sub in self._all_submissions:
            self.submission_map[sub['id']] = sub
        
        if self.show_completed_checkbox.isChecked():
            self.submissions[:] = self._all_submissions
        else:
            self.submissions[:] = [sub for sub in self._all_submissions if sub.get('status') != 'completed' and sub.get('status') != 'denied']
        
        self.submissions_table.setRowCount(len(self.submissions))
        for row in xrange(self.submissions_table.rowCount()):
            self.generate_row(row, self.submissions[row])
            
    
    def login(self):
        dialog = LoginDialog(self, can_cancel=False)
        
        dialog.exec_()
        
        if self._wrapper:
            self.statusBar.showMessage('Logged in as: {}'.format(self._wrapper.get_username()))
            self.update_table()
            
    def edit_account(self):
        dialog = AccountEditingDialog(self)
        
        dialog.exec_()
    
    
    def init_ui(self):
        self.statusBar.showMessage('Not logged in')
        
        self.actionChangeAccountProperties.triggered.connect(self.edit_account)
        self.actionExit.triggered.connect(self.close)
        self.actionRefresh.triggered.connect(self.update_table)
        
        self.submissions_table.cellClicked.connect(self.cell_selected)
        
        self.show_completed_checkbox.stateChanged.connect(self.show_completed_change)
          
        self.show()
        self.login()
    
    
    def __init__(self):
        super(MainWindow, self).__init__()
        custom_widgets_map = {
                          'QReadOnlyCheckBox': custom_widgets.QReadOnlyCheckBox,
                          #'STLViewerWidget': custom_widgets.STLViewerWidget,
                          }
        pyside_dynamic.loadUi("Main_Window_v2.ui", self, custom_widgets_map)
        
        self._wrapper = None
        
        self.submissions = []
        self.submission_map = {}
        
        self.init_ui()


if __name__ == "__main__":
    app = QtGui.QApplication(sys.argv)
    window = MainWindow()
    sys.exit(app.exec_())
