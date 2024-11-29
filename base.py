import sys
import pandas as pd
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QTableWidget, QTableWidgetItem, QVBoxLayout, QPushButton, 
    QHBoxLayout, QWidget, QFileDialog, QHeaderView, QMessageBox, QAbstractItemView, QLineEdit
)
from PyQt6.QtCore import Qt


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Управление базой данных")
        self.resize(1200, 600)
        
        self.db_data = None  # Данные из загруженной базы данных
        self.table_widget = QTableWidget()
        self.table_widget.setColumnCount(8)
        self.table_widget.setHorizontalHeaderLabels([ 
            "ID Устройства", "ID модели устройства (*)", "ID контейнера", 
            "Место в контейнере", "MAC адрес (*)", "IP адрес", 
            "Серийный номер (*)", "ID профиля пула"
        ])
        self.table_widget.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table_widget.setRowCount(10)

        # Включаем возможность вставки данных через Ctrl+V
        self.table_widget.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self.table_widget.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectItems)
        self.table_widget.itemActivated.connect(self.handle_item_paste)

        # Кнопки
        load_db_button = QPushButton("Загрузить БД")
        save_csv_button = QPushButton("Сохранить CSV")
        clear_button = QPushButton("Очистить")
        
        load_db_button.clicked.connect(self.load_database)
        save_csv_button.clicked.connect(self.save_csv)
        clear_button.clicked.connect(self.clear_table)

        # Кнопки заполнения
        fill_buttons_layout = QHBoxLayout()
        self.fill_buttons = []
        for i in range(self.table_widget.columnCount()):
            fill_button = QPushButton(f"Заполнить {self.table_widget.horizontalHeaderItem(i).text()}")
            fill_button.clicked.connect(lambda _, col=i: self.fill_column_from_db(col))
            self.fill_buttons.append(fill_button)
            fill_buttons_layout.addWidget(fill_button)
        
        # Текстовое поле и кнопка для генерации запроса на удаление
        self.delete_query_text = QLineEdit()
        self.delete_query_text.setPlaceholderText("Здесь будет запрос на удаление")
        generate_query_button = QPushButton("Генерация запроса на удаление")
        generate_query_button.clicked.connect(self.generate_delete_query)

        # Основной макет
        layout = QVBoxLayout()
        layout.addWidget(self.table_widget)
        
        controls_layout = QHBoxLayout()
        controls_layout.addWidget(load_db_button)
        controls_layout.addWidget(save_csv_button)
        controls_layout.addWidget(clear_button)
        
        layout.addLayout(fill_buttons_layout)
        layout.addLayout(controls_layout)
        
        # Добавляем элементы для генерации запроса
        layout.addWidget(generate_query_button)
        layout.addWidget(self.delete_query_text)
        
        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)
    
    def load_database(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Выбрать CSV файл", "", "CSV Files (*.csv)")
        if file_path:
            try:
                # Используем точку с запятой как разделитель
                self.db_data = pd.read_csv(file_path, sep=";")
                
                # Убираем лишние символы (кавычки и пробелы) из имен столбцов
                self.db_data.columns = self.db_data.columns.str.replace('"', '').str.strip()

                # Выводим столбцы загруженной БД для отладки
                print("Столбцы в базе данных:", self.db_data.columns.tolist())

                QMessageBox.information(self, "Успех", "База данных успешно загружена!")
            except Exception as e:
                QMessageBox.critical(self, "Ошибка", f"Не удалось загрузить базу данных: {str(e)}")
    
    def save_csv(self):
        file_path, _ = QFileDialog.getSaveFileName(self, "Сохранить CSV файл", "", "CSV Files (*.csv)")
        if file_path:
            try:
                data = []
                for row in range(self.table_widget.rowCount()):
                    row_data = []
                    for col in range(self.table_widget.columnCount()):
                        item = self.table_widget.item(row, col)
                        row_data.append(item.text() if item else "")
                    data.append(row_data)
                df = pd.DataFrame(data, columns=[ 
                    "ID Устройства", "ID модели устройства (*)", "ID контейнера", 
                    "Место в контейнере", "MAC адрес (*)", "IP адрес", 
                    "Серийный номер (*)", "ID профиля пула"
                ])
                df.to_csv(file_path, index=False)
                QMessageBox.information(self, "Успех", "Файл успешно сохранен!")
            except Exception as e:
                QMessageBox.critical(self, "Ошибка", f"Не удалось сохранить файл: {str(e)}")
    
    def clear_table(self):
        self.table_widget.setRowCount(0)
        self.table_widget.setRowCount(10)  # Добавляем 10 пустых строк

    def handle_item_paste(self):
        # Получаем текущую ячейку
        current_item = self.table_widget.currentItem()
        if current_item is None:
            return

        row, col = current_item.row(), current_item.column()
        
        # Вставка данных из буфера обмена
        clipboard = QApplication.clipboard()
        data = clipboard.text()
        values_list = [v.strip() for v in data.splitlines() if v.strip()]

        # Вставляем данные в выбранный столбец
        for i, value in enumerate(values_list):
            target_row = row + i
            while target_row >= self.table_widget.rowCount():
                self.table_widget.insertRow(self.table_widget.rowCount())
            self.table_widget.setItem(target_row, col, QTableWidgetItem(value))

    def fill_column_from_db(self, column_index):
        if self.db_data is None or self.db_data.empty:
            QMessageBox.warning(self, "Предупреждение", "Сначала загрузите базу данных.")
            return

        column_name = self.table_widget.horizontalHeaderItem(column_index).text()

        # Исправленное сопоставление столбцов с данными из базы
        db_column_name = self.get_db_column_name(column_name)

        if db_column_name:
            # Теперь заполняем данные из базы данных
            self.auto_fill_from_database(column_index, db_column_name)
    
    def get_db_column_name(self, column_name):
        column_mapping = {
            "ID Устройства": "id_device_clients_devices",
            "ID модели устройства (*)": "id_directory_miners_clients_devices",
            "ID контейнера": "id_containers_clients_devices",
            "Место в контейнере": "id_place_clients_devices",
            "MAC адрес (*)": "mac_addr_clients_devices",
            "IP адрес": "ip_addr_clients_devices",
            "Серийный номер (*)": "sn_clients_devices",
            "ID профиля пула": "id_clients_pool_profile_clients_devices"
        }
        return column_mapping.get(column_name)

    def auto_fill_from_database(self, target_column, db_column_name):
        if db_column_name not in self.db_data.columns:
            QMessageBox.warning(self, "Ошибка", f"Колонка '{db_column_name}' отсутствует в базе данных.")
            return
        
        for row in range(self.table_widget.rowCount()):
            source_item = self.table_widget.item(row, 0)  # Используем ID устройства как основной
            if source_item:
                source_value = source_item.text()
                matching_rows = self.db_data[self.db_data['id_device_clients_devices'] == int(source_value)]
                if not matching_rows.empty:
                    value = matching_rows[db_column_name].iloc[0]
                    self.table_widget.setItem(row, target_column, QTableWidgetItem(str(value)))

    def generate_delete_query(self):
        if self.db_data is None or self.db_data.empty:
            QMessageBox.warning(self, "Предупреждение", "Сначала загрузите базу данных.")
            return

        # Получаем все ID устройств
        device_ids = self.db_data['id_device_clients_devices'].dropna().unique()

        # Формируем запрос
        ids_str = ", ".join(map(str, device_ids))
        query = f"DELETE FROM clients_devices\nWHERE id_device_clients_devices IN (\n{ids_str}\n);"

        # Выводим запрос в текстовое поле
        self.delete_query_text.setText(query)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
