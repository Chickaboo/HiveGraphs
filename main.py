import sys
from PyQt5.QtWidgets import QApplication, QWidget, QPushButton, QLineEdit, QListWidget, QLabel, QFormLayout, QVBoxLayout, QFileDialog, QCheckBox, QSpinBox, QComboBox
from PyQt5.QtGui import QIcon, QPixmap  
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
        self.game_input.addItems(['wars', 'dr', 'hide', 'sg', 'murder', 'sky', 'ctf', 'drop', 'ground', 'build', 'party', 'bridge', 'grav'])

        self.year_input = QLineEdit()

        self.stats_checkboxes = []

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
        
        vbox = QVBoxLayout()
        vbox.addLayout(self.form_layout)
        
        self.stats_vbox = QVBoxLayout() # Will hold checkboxes
        vbox.addLayout(self.stats_vbox)
        
        vbox.addWidget(self.num_months_spinbox)
        vbox.addWidget(self.graph_type_combo)
        vbox.addWidget(self.get_stats_button)
        vbox.addWidget(self.download_button)
        vbox.addWidget(self.stats_list)
        vbox.addWidget(self.graph_label)
        
        self.setLayout(vbox)

        # Connect signals
        self.game_input.currentTextChanged.connect(self.update_stats)
        self.get_stats_button.clicked.connect(self.get_stats)
        self.download_button.clicked.connect(self.download_graph)

        # Set window icon and settings
        icon = QIcon('HiveLogo.png')
        self.setWindowIcon(icon)
        self.setGeometry(300, 300, 300, 500) 
        self.setWindowTitle('Hive Graphs')
        self.show()

        # Initialize with default stats
        self.update_stats()

    def update_stats(self):
        # Remove old checkboxes
        for checkbox in self.stats_checkboxes:
            self.stats_vbox.removeWidget(checkbox)
            checkbox.deleteLater()
        self.stats_checkboxes.clear()
        
        # Add checkboxes based on game
        game = self.game_input.currentText()
        if game == 'wars':
            stats = ['kills', 'deaths', 'played', 'xp', 'victories', 'treasure_destroyed', 'final_kills', 'prestige', 'uncapped_xp']
        elif game == 'dr':
            stats = ['kills', 'deaths', 'played', 'xp', 'victories', 'activated', 'uncapped_xp'] 
        elif game == 'hide':
            stats = ['seeker_kills', 'hider_kills', 'deaths', 'played', 'xp', 'victories']
        elif game == 'sg':
            stats = ['kills', 'deaths', 'played', 'xp', 'victories', 'uncapped_xp']
        elif game == 'murder':
            stats = ['kills', 'deaths', 'played', 'xp', 'victories', 'prestige', 'uncapped_xp', 'murderer_eliminations', 'murders', 'coins']
        elif game == 'sky':
            stats = ['kills', 'deaths', 'played', 'xp', 'victories', 'mystery_chests_destroyed', 'uncapped_xp', 'spells_used', 'ores_mined']
        elif game == 'ctf':
            stats = ['kills', 'deaths', 'played', 'xp', 'victories', 'flags_returned', 'flags_captured', 'assists']
        elif game == 'drop':
            stats = ['vaults_used', 'deaths', 'played', 'xp', 'victories', 'powerups_collected', 'blocks_destroyed']
        elif game == 'ground':
            stats = ['kills', 'deaths', 'played', 'xp', 'victories', 'projectiles_fired', 'blocks_placed', 'blocks_destroyed']
        elif game == 'build':
            stats = ['rating_great_received', 'rating_okay_received', 'rating_meh_received', 'rating_love_received', 'rating_good_received', 'uncapped_xp', 'victories']
        elif game == 'party':
            stats = ['rounds_survived', 'played', 'xp', 'victories', 'powerups_collected']
        elif game == 'bridge':
            stats = ['kills', 'goals', 'deaths', 'played', 'xp', 'victories']
        elif game == 'grav':
            stats = ['maps_completed', 'maps_completed_without_dying', 'deaths', 'played', 'xp', 'victories']
            
        
        for stat in stats:
            checkbox = QCheckBox(stat)
            self.stats_checkboxes.append(checkbox)
            self.stats_vbox.addWidget(checkbox)

    def get_stats(self):
        # Validate input fields
        if not self.game_input.currentText():
            self.show_error("Game field is required")
            return
        if not self.year_input.text():
            self.show_error("Year field is required")
            return
            
        # Get inputs
        self.player_name = self.player_name_input.text()
        game = self.game_input.currentText()
        year = self.year_input.text()
        num_months = self.num_months_spinbox.value()
            
        # Get checked stats
        stats = [cb.text() for cb in self.stats_checkboxes if cb.isChecked()]
        
        # Get graph type
        graph_type = self.graph_type_combo.currentText()
        
        # Initialize data storage
        monthly_data = {stat: [] for stat in stats}
        
        # Get data for each month
        for month in range(1, num_months+1):
            url = f'https://api.playhive.com/v0/game/monthly/player/{game}/{self.player_name}/{year}/{month}'

            try:
                response = requests.get(url)
                response.raise_for_status()
            except requests.exceptions.HTTPError as err:
                self.show_error(f"Error getting data for {self.player_name}: {err}")
                continue

            try:
                data = response.json()
            except JSONDecodeError:
                self.show_error(f"Error decoding JSON for {self.player_name} in {month}/{year}")
                continue
            
            if not data:
                self.show_error(f"{self.player_name} not found for {month}/{year}")
                continue

            for stat in stats:
                if stat in data:
                    monthly_data[stat].append(data[stat])
                    self.stats_list.addItem(f"{month}/{year} {self.player_name} {stat}: {data[stat]}")

        # Create DataFrame
        df = pd.DataFrame(monthly_data)
        
        # Generate graph
        if graph_type == 'line':
            ax = df.plot.line()
        elif graph_type == 'bar': 
            ax = df.plot.bar()

        ax.set_xlabel('Month')
        ax.set_ylabel('Count')
        fig = ax.get_figure()
        fig.suptitle(f"{self.player_name} - {game} {year}", y=0.92)
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
        path, _ = QFileDialog.getSaveFileName(self, 'Save Graph', 'graph.png', 'PNG(*.png)')
        if path:
            self.pixmap.save(path)
            
if __name__ == '__main__':
    app = QApplication(sys.argv)
    gui = HiveStatsGUI()
    sys.exit(app.exec_())
