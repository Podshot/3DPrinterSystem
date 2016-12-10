import sys
from PySide import QtGui, QtCore
import pyside_dynamic
import api_wrapper
import custom_widgets
from datetime import datetime
import os
import subprocess

def calculate_position(parent, width, height):
    return (parent.x() + ((parent.width() / 2) - (width / 2)), parent.y() + ((parent.height() / 2) - (height / 2)))

def run_process(args):
    proc = subprocess.Popen(args, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    while proc.poll() is None:
        line = proc.stdout.readline()
        if line:
            print '[{}]: {}'.format(os.path.basename(args[0]), )
    return

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
            pass
        
        return func
    
    def generate_row(self, row, submission):
        data = {}
        #print submission['date']
        #print datetime.strptime(submission['date'], "%B %d, %Y at %I:%M %p")
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
        
        if os.path.exists(os.path.join(os.path.dirname(os.path.abspath(__file__)), "submissions", '{}.stl'.format(submission_id))):
            self.prepare_button.setEnabled(True)
            #self.viewer = custom_widgets.STLViewerWidget(self)
            self.viewer.open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "submissions", '{}.stl'.format(submission_id)))
            self.viewer.initializeGL()
        else:
            self.prepare_button.setEnabled(False)
            
        try:
            self.prepare_button.clicked.disconnect()
        except:
            pass
        
        self.prepare_button.clicked.connect(self.prepare_model(submission_id))
        
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
            #item_title = QtGui.QTableWidgetItem(self.submissions[row]["title"])
            #item_priority = QtGui.QTableWidgetItem(str(self.submissions[row]['priority']))
            #self.submissions_table.setItem(row, 0, item_title)
            #self.submissions_table.setItem(row, 1, item_priority)
            
    
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
        
        #geom = self.viewer.geometry()
        #self.viewer = custom_widgets.STLViewerWidget()
        #self.viewer.setGeometry(geom)
        #self.viewer.open(os.path.join('submissions', 'bedf1621-f95a-496b-83b6-f20c3abe7f26.stl'))
        
        self.actionChangeAccountProperties.triggered.connect(self.edit_account)
        self.actionExit.triggered.connect(self.close)
        self.actionRefresh.triggered.connect(self.update_table)
        
        self.submissions_table.cellClicked.connect(self.cell_selected)
        
        self.show_completed_checkbox.stateChanged.connect(self.show_completed_change)
        
        #self.download_progressbar.setRange(0, 100)
        #self.download_progressbar.setValue(0)
          
        self.show()
        self.login()
    
    
    def __init__(self):
        super(MainWindow, self).__init__()
        custom_widgets_map = {
                          'QReadOnlyCheckBox': custom_widgets.QReadOnlyCheckBox,
                          'STLViewerWidget': custom_widgets.STLViewerWidget,
                          }
        pyside_dynamic.loadUi("Main_Window.ui", self, custom_widgets_map)
        
        self._wrapper = None
        
        self.submissions = []
        self.submission_map = {}
        
        self.init_ui()
        
    def on_test_button_clicked(self):
        print "Test!"


if __name__ == "__main__":
    app = QtGui.QApplication(sys.argv)
    window = MainWindow()
    sys.exit(app.exec_())
