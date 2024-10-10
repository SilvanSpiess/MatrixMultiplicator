import sys
from PyQt5.QtWidgets import QApplication, QWidget, QLineEdit, QLabel, QGridLayout, QVBoxLayout, QHBoxLayout, QPushButton, QComboBox
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont
from title_bar import TitleBar
from sympy import Matrix, latex
import pyperclip

#***********************************
# Stylesheet Dark / Light
#***********************************
window_style_sheet = ["""
                        QWidget {
                            background-color: #2E2E2E;  /* Dark background */
                            color: white;  /* Text color in white */
                        }
                        QLineEdit {
                            background-color: #4E4E4E;  /* Dark text boxes */
                            color: black;  /* Text color in white */
                            border: 1px solid #C0C0C0;  /* Light grey border */
                        }
                        QLabel {
                            color: white;  /* Labels in white */
                        }
                    """,
                    """
                            QWidget {
                                background-color: #F0F0F0;  /* Light background */
                                color: black;  /* Text color in black */
                            }
                            QLineEdit {
                                background-color: #FFFFFF;  /* White text boxes */
                                color: black;  /* Text color in black */
                                border: 1px solid #C0C0C0;  /* Light grey border */
                            }
                            QLabel {
                                color: black;  /* Labels in black */
                            }
                        """]

#***********************************
# Greek letters list
#***********************************
greek_letters = ['α', 'β', 'γ', 'δ', 'ε', 'ζ', 'η', 'θ', 'ι', 'κ', 'λ', 'μ', 'ν', 'ξ', 'ο', 'π', 'ρ', 'σ', 'τ', 'υ', 'φ', 'χ', 'ψ', 'ω']

max_rows, max_cols = 5,5

# pyinstaller --noconsole --onefile --distpath=./ --icon=icon.svg --name=Matrix_Multiplicators matrix_rechner.py 

from PyQt5.QtCore import pyqtSignal

class FocusLineEdit(QLineEdit):
    focus_in_signal = pyqtSignal()  
    def focusInEvent(self, event):
        super(FocusLineEdit, self).focusInEvent(event)
        self.focus_in_signal.emit()  # Emit the focus signal when focused

class MatrixMultiplicationApp(QWidget):
    def __init__(self):
        super().__init__()

        #***********************************
        # Setup main window
        #***********************************
        self.setWindowTitle("Matrizen Multiplikator")   
        self.setFixedSize(1250,625)
        self.setWindowFlags(Qt.FramelessWindowHint)
        self.setStyleSheet(window_style_sheet[0])
        self.setWindowIcon(TitleBar.iconFromBase64(TitleBar.image_base64))
        
        #***********************************
        # Initial conditions
        #***********************************
        self.current_line_edit = None
        self.matlab_code = ''
        self.latex_code = ''
        #***********************************
        # Dropdown widgets and layout
        #***********************************
        dropdown_mode = QComboBox()
        dropdown_mode.addItems(["Darkmode", "Lightmode"])
        dropdown_mode.setFixedSize(150, 30)
        dropdown_mode.setCursor(Qt.PointingHandCursor)
        dropdown_mode.setFocusPolicy(Qt.NoFocus)
        dropdown_mode.setCurrentIndex(0)

        dropdown_layout = QHBoxLayout()
        dropdown_layout.addWidget(dropdown_mode)
        dropdown_layout.addStretch(1)

        #***********************************
        # 'x' and '=' labels and layouts
        #***********************************
        equals_label = QLabel("x")
        equals_label.setFixedSize(50, 50)  
        equals_label.setFont(QFont("Arial", 36, QFont.Bold))  
        equals_label.setAlignment(Qt.AlignCenter)  
        equals_layout = QVBoxLayout()
        equals_layout.addStretch(1)
        equals_layout.addWidget(equals_label)
        equals_layout.addStretch(1)

        cross_label = QLabel("=")
        cross_label.setFixedSize(50, 50)
        cross_label.setFont(QFont("Arial", 48, QFont.Bold))  
        cross_label.setAlignment(Qt.AlignCenter) 
        cross_layout = QVBoxLayout()
        cross_layout.addStretch(1)
        cross_layout.addWidget(cross_label)
        cross_layout.addStretch(1)

        #***********************************
        # Matrizes and layout [M] 'x' [M] '=' [M]
        #***********************************
        self.left_matrix = self.create_matrix_grid(max_rows, max_cols, False, 40, 40)
        self.right_matrix = self.create_matrix_grid(max_rows, max_cols, False, 40, 40)
        self.result_matrix = self.create_matrix_grid(max_rows, max_cols, True, 90, 40)
        self.left_matrix.setObjectName('left_matrix')
        self.right_matrix.setObjectName('right_matrix')
        self.result_matrix.setObjectName('result_matrix')

        matrix_layout = QHBoxLayout()
        matrix_layout.setContentsMargins(20, 20, 20, 20)
        matrix_layout.addLayout(self.left_matrix)
        matrix_layout.addLayout(equals_layout)
        matrix_layout.addLayout(self.right_matrix)
        matrix_layout.addLayout(cross_layout)
        matrix_layout.addLayout(self.result_matrix)

        #***********************************
        # Greek letter buttons 'α' - 'ω' and layout
        #***********************************
        greek_button_layout = QHBoxLayout()
        greek_button_layout.setContentsMargins(20, 20, 20, 20)

        for letter in greek_letters:
            button = QPushButton(letter)
            button.setFixedSize(40, 40)
            button.setStyleSheet("""
                                    QPushButton {
                                        background-color: lightgrey; 
                                        color: black; 
                                        font-size: 18px;
                                        border-radius: 10px;  /* Rounded border */
                                    }
                                    QPushButton:hover {
                                        background-color: grey;  /* Hand cursor on hover */
                                    }
                                """)
            button.clicked.connect(lambda checked, l=letter: self.insert_greek_letter(l))
            button.setCursor(Qt.PointingHandCursor)
            greek_button_layout.addWidget(button)

        #***********************************
        # 'Compute' and 'Reset' buttons and layout
        #***********************************
        compute_button = QPushButton("Compute")
        compute_button.setFixedSize(300,40)
        compute_button.setStyleSheet("""
                                        QPushButton {
                                            background-color: green; 
                                            color: white; 
                                            font-size: 16px;
                                            border-radius: 10px;  /* Rounded border */
                                        }
                                        QPushButton:hover {
                                            background-color: #3CB043;  /* Hand cursor on hover */
                                        }
                                    """)
        compute_button.setCursor(Qt.PointingHandCursor)

        reset_button = QPushButton("Reset")
        reset_button.setFixedSize(300,40)
        reset_button.setStyleSheet("""
            QPushButton {
                background-color: red; 
                color: white; 
                font-size: 16px;
                border-radius: 10px;  /* Rounded border */
            }
            QPushButton:hover {
                background-color: #CC0000;  /* Hand cursor on hover */
            }
        """)
        reset_button.setCursor(Qt.PointingHandCursor)

        matlab_button = QPushButton("Matlab Output")
        matlab_button.setFixedSize(300,40)
        matlab_button.setStyleSheet("""
            QPushButton {
                background-color: lightgrey; 
                color: black; 
                font-size: 16px;
                border-radius: 10px;  /* Rounded border */
            }
            QPushButton:hover {
                background-color: grey;  /* Hand cursor on hover */
            }
        """)
        matlab_button.setCursor(Qt.PointingHandCursor)

        latex_button = QPushButton("Latex Output")
        latex_button.setFixedSize(300,40)
        latex_button.setStyleSheet("""
            QPushButton {
                background-color: lightgrey; 
                color: black; 
                font-size: 16px;
                border-radius: 10px;  /* Rounded border */
            }
            QPushButton:hover {
                background-color: grey;  /* Hand cursor on hover */
            }
        """)
        latex_button.setCursor(Qt.PointingHandCursor)

        buttons_layout = QHBoxLayout()
        buttons_layout.addWidget(compute_button)
        buttons_layout.addWidget(reset_button)
        buttons_layout.addWidget(matlab_button)
        buttons_layout.addWidget(latex_button)

        #***********************************
        # incorrect matrix label and layout
        #***********************************
        self.error_label = QLabel("")
        self.error_label.setFixedSize(700, 50)  
        self.error_label.setFont(QFont("Arial", 14, QFont.Bold))  
        self.error_label.setStyleSheet("QLabel { color : red; }")
        self.error_label.setAlignment(Qt.AlignCenter)  
        error_layout = QVBoxLayout()
        error_layout.addStretch(1)
        error_layout.addWidget(self.error_label)
        error_layout.addStretch(1)

        #***********************************
        # Main Layout:
        #  - Dropdown
        #  - [M]x[M]=[M]
        #  - greel_letters
        #  - compute and compute button
        #***********************************
        main_layout = QVBoxLayout()
        self.title_bar = TitleBar(self)
        main_layout.addWidget(self.title_bar)
        main_layout.addLayout(dropdown_layout)
        main_layout.addLayout(matrix_layout)
        main_layout.addLayout(greek_button_layout)
        main_layout.addLayout(buttons_layout)
        main_layout.addLayout(error_layout)

        #***********************************
        # Add main_layout to window
        #***********************************
        #self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.setLayout(main_layout)

        #***********************************
        # Connection functions
        #***********************************
        compute_button.clicked.connect(self.compute)
        reset_button.clicked.connect(self.reset)
        latex_button.clicked.connect(self.copy_latex_code)
        matlab_button.clicked.connect(self.copy_matlab_code)
        dropdown_mode.currentIndexChanged.connect(self.on_dropdown_mode_selection)

    #***********************************
    # Dropdown functions
    #***********************************
    def on_dropdown_mode_selection(self, index):
        self.setStyleSheet(window_style_sheet[index])
        self.title_bar.title_label.setStyleSheet(window_style_sheet[index])

    #***********************************
    # Grid and Matrices creation and handle funcions
    #***********************************
    def create_matrix_grid(self, rows, cols, read_only, width, height):
        grid = QGridLayout()
        for row in range(rows):
            for col in range(cols):
                line_edit = FocusLineEdit(self)                
                line_edit.setFixedSize(width, height)  
                line_edit.setAlignment(Qt.AlignCenter)  
                line_edit.setStyleSheet("background-color: lightgrey; border: 1px solid black;")
                if read_only:
                    line_edit.setReadOnly(True)
                else:
                    line_edit.focus_in_signal.connect(self.set_current_line_edit)
                line_edit.textChanged.connect(lambda text, le=line_edit: self.handle_text_change(le))
                grid.addWidget(line_edit, row, col)
        return grid

    def set_current_line_edit(self):
        self.current_line_edit = self.sender()

    def copy_matlab_code(self):
        pyperclip.copy(self.matlab_code)

    def copy_latex_code(self):
        pyperclip.copy(self.latex_code)

    def insert_greek_letter(self, letter):
        if self.current_line_edit is not None:
            self.current_line_edit.insert(letter)

    def handle_text_change(self, line_edit):
        if line_edit.text():
            line_edit.setStyleSheet("background-color: white; border: 1px solid black;")
        else:
            line_edit.setStyleSheet("background-color: lightgrey; border: 1px solid black;")

    #***********************************
    # Function which check for correctly filled matrices
    #***********************************
    def check_matrix_sizes(self, matrix):
        num_rows, num_cols = 0, 0
        # Find empty matrix
        if matrix.itemAtPosition(0, 0).widget().text().strip() == "":
            return 0, 0, False
        # Set dimensions
        for i in range(max_cols):
            if matrix.itemAtPosition(i, 0).widget().text().strip() != "":
                num_rows += 1
            if matrix.itemAtPosition(0, i).widget().text().strip() != "":
                num_cols += 1
        # Check dimensions with other rows and cols
        filled_rows = 0
        for row in range(max_rows):
            filled_cols = 0
            value_in_row = False
            for col in range(max_cols):
                if matrix.itemAtPosition(row, col).widget().text().strip() != "":
                    filled_cols += 1  
                    value_in_row = True              
            if value_in_row: 
                if filled_cols != num_cols:
                    return num_rows, num_cols, False
                filled_rows += 1  
        if filled_rows != num_rows:
            return num_rows, num_cols, False        
        return num_rows, num_cols, True

    #***********************************
    # Function which does the (meth) math
    #***********************************
    def compute(self):
        for widget in self.findChildren(QLineEdit, name='result_matrix'):
            widget.clear()
            widget.setStyleSheet("background-color: lightgrey; border: 1px solid black;")

        lm_rows, lm_cols, lm_valid = self.check_matrix_sizes(self.left_matrix)
        rm_rows, rm_cols, rm_valid = self.check_matrix_sizes(self.right_matrix)
        if (not lm_valid) and (not rm_valid):
            self.error_label.setText("Invalid Left and Right Matrix")
        elif not lm_valid:
            self.error_label.setText("Invalid Left Matrix")
        elif not rm_valid:
            self.error_label.setText("Invalid Right Matrix")
        elif lm_rows != rm_cols or lm_cols != rm_rows:
            self.error_label.setText("Invalid Matrix Dimensions!")
        else:
            self.error_label.setText("")

        M_R = Matrix([[self.right_matrix.itemAtPosition(i, j).widget().text() for i in range(rm_rows)] for j in range(rm_cols)])
        M_L = Matrix([[self.left_matrix.itemAtPosition(i, j).widget().text() for i in range(lm_rows)] for j in range(lm_cols)])

        M_Res = M_R * M_L

        self.matlab_code += f"{'M_L'} = ["
        for i in range(M_L.shape[0]):
            row_entries = ' '.join([str(M_L[i, j]) for j in range(M_L.shape[1])]) 
            self.matlab_code += row_entries
            if i < M_L.shape[0] - 1:
                self.matlab_code += "; "
        self.matlab_code += "];\n"

        self.matlab_code += f"{'M_R'} = ["
        for i in range(M_R.shape[0]):
            row_entries = ' '.join([str(M_R[i, j]) for j in range(M_R.shape[1])]) 
            self.matlab_code += row_entries
            if i < M_R.shape[0] - 1:
                self.matlab_code += "; "
        self.matlab_code += "];\n"

        self.matlab_code += 'M_Res = M_L * M_R'

        self.latex_code = latex(M_L) + '$\\times$' + latex(M_R) + '$=$' + latex(M_Res) 
        print(M_Res)
        print(self.latex_code)
        print(self.matlab_code)
        for row in range(M_Res.shape[0]):
            for col in range(M_Res.shape[1]):
                result_field = self.result_matrix.itemAtPosition(row, col).widget()                
                if result_field is not None:
                    result_field.setText(str(M_Res[row, col]))

        """ for i in range(lm_rows):         # Loop over rows of left matrix
            for j in range(rm_cols):     # Loop over columns of right matrix
                result_string = ''    
                for k in range(lm_cols): # Loop over columns of left matrix (or rows of right matrix)
                    left_item = self.left_matrix.itemAtPosition(i, k).widget()
                    right_item = self.right_matrix.itemAtPosition(k, j).widget()
                    if self.current_result_view == 'reduced':
                        if str(left_item.text()) == '0' or str(right_item.text()) == '0': 
                            continue
                        elif str(left_item.text()) == '1':
                            result_string +=  ('+' + str(right_item.text()))
                        elif str(right_item.text()) == '1':
                            result_string +=  ('+' + str(left_item.text()))
                        else:
                            result_string +=  ('+' + str(left_item.text()) + "*" + str(right_item.text()))
                    else:
                        result_string +=  ('+' + str(left_item.text()) + "*" + str(right_item.text()))

                result_field = self.result_matrix.itemAtPosition(i, j).widget()
                if result_field is not None:
                    print("updating field with: " + result_string + "with current_view: " + self.current_result_view)
                    result_field.setText(result_string[1:])
 """
    
    #***********************************
    # Function which resets all grids (matrices)
    #***********************************   
    def reset(self):
        print("Reset button pressed")
        self.error_label.setText("")
        for widget in self.findChildren(QLineEdit):
            widget.clear()
            widget.setStyleSheet("background-color: lightgrey; border: 1px solid black;")

if __name__ == "__main__":
    app = QApplication(sys.argv)

    window = MatrixMultiplicationApp()
    window.show()

    sys.exit(app.exec_())
