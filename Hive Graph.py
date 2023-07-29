import sys
from PyQt5.QtWidgets import QApplication, QWidget, QPushButton, QLineEdit, QListWidget, QLabel, QFormLayout, QVBoxLayout, QFileDialog, QCheckBox, QSpinBox, QComboBox
from PyQt5.QtGui import QPixmap, QIcon
import matplotlib.pyplot as plt
import pandas as pd
import requests
from PyQt5 import QtWidgets

class HiveStatsGUI(QWidget):

    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        # Widgets
        self.player_name_input = QLineEdit()
        
        self.game_input = QComboBox()
        self.game_input.addItems(['wars', 'dr', 'hide', 'sg', 'murder', 'sky', 'ctf', 'drop', 'ground', 'build', 'party', 'main', 'bridge', 'grav'])

        self.year_input = QLineEdit()

        self.kills_checkbox = QCheckBox('Kills')
        self.deaths_checkbox = QCheckBox('Deaths')
        self.assists_checkbox = QCheckBox('Assists')
        self.played_checkbox = QCheckBox('Games Played')
        self.victories_checkbox = QCheckBox('Victories')
        
        self.num_months_spinbox = QSpinBox()
        self.num_months_spinbox.setRange(1, 12)
        self.num_months_spinbox.setValue(6)

        self.graph_type_combo = QComboBox()
        self.graph_type_combo.addItems(['line', 'bar'])
        
        self.get_stats_button = QPushButton('Get Stats')
        self.download_button = QPushButton('Download Graph')
        
        self.stats_list = QListWidget()
        self.graph_label = QLabel()

        # Layout
        self.form_layout = QFormLayout()
        self.form_layout.addRow('Player Name', self.player_name_input)
        self.form_layout.addRow('Game', self.game_input)
        self.form_layout.addRow('Year', self.year_input)
        self.form_layout.addRow('Stats to Graph', self.kills_checkbox)
        self.form_layout.addRow('', self.deaths_checkbox)
        self.form_layout.addRow('', self.assists_checkbox)
        self.form_layout.addRow('', self.played_checkbox)
        self.form_layout.addRow('', self.victories_checkbox)
        self.form_layout.addRow('Num Months', self.num_months_spinbox)
        self.form_layout.addRow('Graph Type', self.graph_type_combo)
        
        vbox = QVBoxLayout()
        vbox.addLayout(self.form_layout)
        vbox.addWidget(self.get_stats_button)
        vbox.addWidget(self.download_button)
        vbox.addWidget(self.stats_list)
        vbox.addWidget(self.graph_label)
        
        self.setLayout(vbox)

        # Connect signals
        self.get_stats_button.clicked.connect(self.get_stats)
        self.download_button.clicked.connect(self.download_graph)

        # Set window icon
        icon = QIcon('HiveLogo.png')
        self.setWindowIcon(icon)

        # Window settings
        self.setGeometry(300, 300, 300, 500)
        self.setWindowTitle('Hive Graphs')
        self.show()

    def get_stats(self):
        # Validate input fields
        if not self.game_input.currentText():
            self.show_error("Game field is required")
            return
        if not self.year_input.text():
            self.show_error("Year field is required")
            return
        self.player_name = self.player_name_input.text()
        self.pixmap = QPixmap('graph.png')
        self.graph_label.setPixmap(self.pixmap)
            
        # Get common inputs
        game = self.game_input.currentText()
        year = self.year_input.text() 
        num_months = self.num_months_spinbox.value()

        # Get checked stats
        stats = []
        if self.kills_checkbox.isChecked():
            stats.append('kills')
        if self.deaths_checkbox.isChecked():
            stats.append('deaths')
        if self.assists_checkbox.isChecked():
            stats.append('assists')
        if self.played_checkbox.isChecked():
            stats.append('played')
        if self.victories_checkbox.isChecked():
            stats.append('victories')
            
        # Get player name
        player_name = self.player_name_input.text()
        
        # Get graph type
        graph_type = self.graph_type_combo.currentText()
        
        # Initialize data storage
        monthly_data = {stat: [] for stat in stats}
        
        # Get data for player
        months = range(1, num_months+1)
        for month in months:
            api_url = f'https://api.playhive.com/v0/game/monthly/player/{game}/{player_name}/{year}/{month}'

            try:
                response = requests.get(api_url)
                response.raise_for_status()
            except requests.exceptions.HTTPError as err:
                self.show_error(f"Error getting data for {player_name}: {err}")
                continue

            try:
                data = response.json()
            except JSONDecodeError:
                self.show_error(f"Error decoding JSON for {player_name} in {month}/{year}")
                continue
            
            if not data:
                self.show_error(f"{player_name} not found for {month}/{year}")
                continue

            for stat in stats:
                if stat in data:
                    monthly_data[stat].append(data[stat])
                    self.stats_list.addItem(f"{month}/{year} {player_name} {stat}: {data[stat]}")

        # Create DataFrame
        df = pd.DataFrame(monthly_data)
        
        # Generate graph based on graph type
        if graph_type == 'line':
            ax = df.plot(kind='line')
        elif graph_type == 'bar':
            ax = df.plot.bar()
        elif graph_type == 'scatter':
            ax = df.plot.scatter(x='Month', y='Count')
        elif graph_type == 'pie':
            ax = df.plot.pie(subplots=True)

        ax.set_xlabel('Month')
        ax.set_ylabel('Count')

        fig = ax.get_figure()

        # Add title 
        fig.suptitle(f"{self.player_name} - {game} {year}", y=0.92)

        # Save figure
        fig.savefig('graph.png')
        plt.close(fig)

        # Display graph
        pixmap = QPixmap('graph.png')
        self.graph_label.setPixmap(pixmap)

    def show_error(self, error_msg):
        error_dialog = QtWidgets.QErrorMessage()
        error_dialog.showMessage(error_msg)
        error_dialog.exec_()

    def download_graph(self):
        path = QFileDialog.getSaveFileName(self, 'Save Graph', 'graph.png', 'PNG(*.png)')[0]
        if path:
            self.pixmap.save(path)
            
if __name__ == '__main__':
    app = QApplication(sys.argv)
    gui = HiveStatsGUI()
    sys.exit(app.exec_())