import sys
import os
import json
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QHBoxLayout, QPushButton, QLabel, QFileDialog, 
                             QComboBox, QSpinBox, QTextEdit, QScrollArea, 
                             QGridLayout, QGroupBox, QFormLayout, QDialog, QDoubleSpinBox)
from PyQt6.QtCore import Qt, QProcess
from PyQt6.QtGui import QPixmap, QCursor

class DetailView(QDialog):
    def __init__(self, pixmap, name, parent=None):
        super().__init__(parent)
        self.setWindowTitle(f"Detailed Analysis - {name}")
        self.resize(1200, 900)
        layout = QVBoxLayout(self)
        lbl = QLabel()
        lbl.setPixmap(pixmap.scaled(1150, 850, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation))
        lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        scroll = QScrollArea()
        scroll.setWidget(lbl)
        layout.addWidget(scroll)
        btn = QPushButton("Close")
        btn.clicked.connect(self.close)
        layout.addWidget(btn)

class ClickableLabel(QLabel):
    def __init__(self, name, pixmap, parent=None):
        super().__init__(parent)
        self.name = name
        self.pix = pixmap
        self.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            dialog = DetailView(self.pix, self.name, self.window())
            dialog.exec()

class GRAVWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("GRAV Engine v2.0 - Galaxy Physics Discovery")
        self.resize(1600, 950)
        self.process = None
        self.current_results = None
        self.current_page = 0
        self.init_ui()

    def init_ui(self):
        main_widget = QWidget(); self.setCentralWidget(main_widget)
        main_layout = QHBoxLayout(main_widget)

        left_panel = QWidget(); left_layout = QVBoxLayout(left_panel); left_panel.setFixedWidth(380)
        
        config_group = QGroupBox("1. Configuration")
        config_form = QFormLayout()
        self.btn_select = QPushButton("📁 Select Data Folder")
        self.btn_select.clicked.connect(self.select_data)
        self.lbl_path = QLabel("None")
        self.combo_model = QComboBox(); self.combo_model.addItems(["DeepONet", "FNO"])
        self.spin_epochs = QSpinBox(); self.spin_epochs.setRange(1, 10000); self.spin_epochs.setValue(100)
        self.spin_pysr = QSpinBox(); self.spin_pysr.setRange(1, 1000); self.spin_pysr.setValue(50)
        self.spin_chi2 = QDoubleSpinBox(); self.spin_chi2.setRange(0.1, 1000.0); self.spin_chi2.setValue(30.0)
        config_form.addRow(self.btn_select); config_form.addRow(self.lbl_path)
        config_form.addRow("AI Model:", self.combo_model)
        config_form.addRow("Training Ep:", self.spin_epochs)
        config_form.addRow("Discovery Iter:", self.spin_pysr)
        config_form.addRow("Chi2 Cutoff:", self.spin_chi2)
        config_group.setLayout(config_form)

        view_group = QGroupBox("2. View Options")
        view_layout = QVBoxLayout()
        self.btn_prev = QPushButton("⬅️ Previous Page"); self.btn_prev.clicked.connect(lambda: self.change_page(-1))
        self.btn_next = QPushButton("Next Page ➡️"); self.btn_next.clicked.connect(lambda: self.change_page(1))
        view_layout.addWidget(self.btn_prev); view_layout.addWidget(self.btn_next)
        view_group.setLayout(view_layout)

        self.btn_run = QPushButton("🚀 LAUNCH ANALYSIS")
        self.btn_run.setFixedHeight(60)
        self.btn_run.setStyleSheet("background-color: #27ae60; color: white; font-weight: bold; font-size: 14px;")
        self.btn_run.clicked.connect(self.start_analysis)

        self.log_output = QTextEdit(); self.log_output.setReadOnly(True)
        self.log_output.setStyleSheet("background-color: #1e1e1e; color: #ecf0f1; font-family: 'Consolas';")
        
        left_layout.addWidget(config_group); left_layout.addWidget(view_group)
        left_layout.addWidget(self.btn_run); left_layout.addWidget(QLabel("Output Log:")); left_layout.addWidget(self.log_output)

        right_panel = QWidget(); right_layout = QVBoxLayout(right_panel)
        self.lbl_info = QLabel("Ready for exploration...")
        self.lbl_info.setStyleSheet("font-size: 18px; color: #2c3e50; font-weight: bold; background: #ecf0f1; padding: 15px; border-radius: 8px;")
        
        self.scroll = QScrollArea(); self.content = QWidget(); self.grid = QGridLayout(self.content)
        self.scroll.setWidgetResizable(True); self.scroll.setWidget(self.content)
        
        right_layout.addWidget(self.lbl_info); right_layout.addWidget(self.scroll)
        main_layout.addWidget(left_panel); main_layout.addWidget(right_panel)

    def select_data(self):
        path = QFileDialog.getExistingDirectory(self, "Select SPARC Data Directory")
        if path: self.data_path = path; self.lbl_path.setText(os.path.basename(path))

    def start_analysis(self):
        if not hasattr(self, 'data_path'): return
        self.btn_run.setEnabled(False); self.log_output.clear()
        self.process = QProcess()
        self.process.setProcessChannelMode(QProcess.ProcessChannelMode.MergedChannels)
        self.process.readyReadStandardOutput.connect(self.handle_output)
        self.process.finished.connect(self.analysis_finished)
        cmd = ["python", "-u", "main.py", "--data", self.data_path, "--model_type", self.combo_model.currentText(),
               "--epochs", str(self.spin_epochs.value()), "--pysr_iter", str(self.spin_pysr.value()), 
               "--chi2_cutoff", str(self.spin_chi2.value()), "--out", "results"]
        self.log_output.append(f"> Running: {' '.join(cmd)}\n")
        self.process.start("python", ["-u"] + cmd[2:])

    def handle_output(self):
        data = self.process.readAllStandardOutput().data().decode(errors='ignore')
        self.log_output.insertPlainText(data)
        self.log_output.verticalScrollBar().setValue(self.log_output.verticalScrollBar().maximum())

    def analysis_finished(self):
        self.btn_run.setEnabled(True)
        json_path = "results/results.json"
        if os.path.exists(json_path):
            with open(json_path, "r") as f: self.current_results = json.load(f)
            self.current_page = 0; self.refresh_display()

    def change_page(self, delta):
        if not self.current_results: return
        max_page = (len(self.current_results['galaxies'])-1) // 12
        self.current_page = max(0, min(self.current_page + delta, max_page))
        self.refresh_display()

    def refresh_display(self):
        if not self.current_results: return
        for i in reversed(range(self.grid.count())): 
            w = self.grid.itemAt(i).widget()
            if w: w.setParent(None)
        
        galaxies = self.current_results['galaxies']
        start = self.current_page * 12
        batch = galaxies[start:start+12]
        self.lbl_info.setText(f"Page {self.current_page+1} | Total Galaxies: {len(galaxies)} | Simplified: {self.current_results['simplified']}")
        
        for i, name in enumerate(batch):
            img_path = f"results/individuals/{name}.png"
            if os.path.exists(img_path):
                pix = QPixmap(img_path)
                lbl = ClickableLabel(name, pix)
                lbl.setPixmap(pix.scaled(400, 300, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation))
                self.grid.addWidget(lbl, i // 3, i % 3)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = GRAVWindow(); window.show()
    sys.exit(app.exec())
