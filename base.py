import sys
import pandas as pd
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QTableWidget, QTableWidgetItem, QVBoxLayout, QPushButton,
    QHBoxLayout, QWidget, QFileDialog, QHeaderView, QMessageBox, QAbstractItemView, QLineEdit
)


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Database Management")
        self.resize(1200, 600)

        self.db_data = None  # Данные из загруженной базы
        self.table_widget = QTableWidget()
        self.table_widget.setColumnCount(8)
        self.table_widget.setHorizontalHeaderLabels([
            "Device ID", "Device Model ID (*)", "Container ID",
            "Place in Container", "MAC Address (*)", "IP Address",
            "Serial Number (*)", "Pool Profile ID"
        ])
        self.table_widget.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table_widget.setRowCount(10)

        # Разрешаем вставку данных через Ctrl+V
        self.table_widget.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self.table_widget.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectItems)
        self.table_widget.itemActivated.connect(self.handle_item_paste)

        # Кнопки
        load_db_button = QPushButton("Load Database")
        save_csv_button = QPushButton("Save CSV")
        clear_button = QPushButton("Clear")

        load_db_button.clicked.connect(self.load_database)
        save_csv_button.clicked.connect(self.save_csv)
        clear_button.clicked.connect(self.clear_table)

        # Кнопки заполнения
        fill_buttons_layout = QHBoxLayout()

        fill_device_id_button = QPushButton("Fill Device ID")
        fill_device_model_id_button = QPushButton("Fill Device Model ID (*)")
        fill_container_id_button = QPushButton("Fill Container ID")
        fill_place_in_container_button = QPushButton("Fill Place in Container")
        fill_mac_address_button = QPushButton("Fill MAC Address (*)")
        fill_ip_address_button = QPushButton("Fill IP Address")
        fill_serial_number_button = QPushButton("Fill Serial Number (*)")
        fill_pool_profile_id_button = QPushButton("Fill Pool Profile ID")

        fill_device_id_button.clicked.connect(self.fill_device_id)
        fill_device_model_id_button.clicked.connect(self.fill_device_model_id)
        fill_container_id_button.clicked.connect(self.fill_container_id)
        fill_place_in_container_button.clicked.connect(self.fill_place_in_container)
        fill_mac_address_button.clicked.connect(self.fill_mac_address)
        fill_ip_address_button.clicked.connect(self.fill_ip_address)
        fill_serial_number_button.clicked.connect(self.fill_serial_number)
        fill_pool_profile_id_button.clicked.connect(self.fill_pool_profile_id)

        fill_buttons_layout.addWidget(fill_device_id_button)
        fill_buttons_layout.addWidget(fill_device_model_id_button)
        fill_buttons_layout.addWidget(fill_container_id_button)
        fill_buttons_layout.addWidget(fill_place_in_container_button)
        fill_buttons_layout.addWidget(fill_mac_address_button)
        fill_buttons_layout.addWidget(fill_ip_address_button)
        fill_buttons_layout.addWidget(fill_serial_number_button)
        fill_buttons_layout.addWidget(fill_pool_profile_id_button)

        # Поле текста и кнопка для генерации запроса на удаление
        self.delete_query_text = QLineEdit()
        self.delete_query_text.setPlaceholderText("Delete query will be displayed here")
        generate_query_button = QPushButton("Generate Delete Query")
        generate_query_button.clicked.connect(self.generate_delete_query)

        # Основной макет
        main_layout = QVBoxLayout()
        main_layout.addWidget(self.table_widget)

        controls_layout = QHBoxLayout()
        controls_layout.addWidget(load_db_button)
        controls_layout.addWidget(save_csv_button)
        controls_layout.addWidget(clear_button)

        main_layout.addLayout(fill_buttons_layout)
        main_layout.addLayout(controls_layout)

        # Добавляем элементы для генерации запроса
        main_layout.addWidget(generate_query_button)
        main_layout.addWidget(self.delete_query_text)

        container = QWidget()
        container.setLayout(main_layout)
        self.setCentralWidget(container)

    def load_database(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Select CSV File", "", "CSV Files (*.csv)")
        if file_path:
            try:
                # Используем точку с запятой как разделитель и читаем все данные как строки
                self.db_data = pd.read_csv(file_path, sep=";", dtype=str)

                # Удаляем лишние символы (кавычки и пробелы) из названий столбцов
                self.db_data.columns = self.db_data.columns.str.replace('"', '').str.strip()

                # Выводим названия столбцов загруженной базы для отладки
                print("Columns in the database:", self.db_data.columns.tolist())

                QMessageBox.information(self, "Success", "Database loaded successfully!")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to load database: {str(e)}")

    def save_csv(self):
        file_path, _ = QFileDialog.getSaveFileName(self, "Save CSV File", "", "CSV Files (*.csv)")
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
                    "Device ID", "Device Model ID (*)", "Container ID",
                    "Place in Container", "MAC Address (*)", "IP Address",
                    "Serial Number (*)", "Pool Profile ID"
                ])
                df.to_csv(file_path, index=False)
                QMessageBox.information(self, "Success", "File saved successfully!")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to save file: {str(e)}")

    def clear_table(self):
        self.table_widget.setRowCount(0)
        self.table_widget.setRowCount(10)  # Добавляем 10 пустых строк

    def handle_item_paste(self):
        # Получаем текущую ячейку
        current_item = self.table_widget.currentItem()
        if current_item is None:
            return

        row, col = current_item.row(), current_item.column()

        # Вставляем данные из буфера обмена
        clipboard = QApplication.clipboard()
        data = clipboard.text()
        values_list = [v.strip() for v in data.splitlines() if v.strip()]

        # Вставляем данные в выбранный столбец
        for i, value in enumerate(values_list):
            target_row = row + i
            while target_row >= self.table_widget.rowCount():
                self.table_widget.insertRow(self.table_widget.rowCount())
            self.table_widget.setItem(target_row, col, QTableWidgetItem(value))

    def fill_device_id(self):
        self.fill_column_from_db(0)

    def fill_device_model_id(self):
        self.fill_column_from_db(1)

    def fill_container_id(self):
        self.fill_column_from_db(2)

    def fill_place_in_container(self):
        self.fill_column_from_db(3)

    def fill_mac_address(self):
        self.fill_column_from_db(4)

    def fill_ip_address(self):
        self.fill_column_from_db(5)

    def fill_serial_number(self):
        self.fill_column_from_db(6)

    def fill_pool_profile_id(self):
        self.fill_column_from_db(7)

    def fill_column_from_db(self, target_column):
        if self.db_data is None or self.db_data.empty:
            QMessageBox.warning(self, "Warning", "Please load the database first.")
            return

        column_name = self.table_widget.horizontalHeaderItem(target_column).text()

        # Получаем соответствующее название столбца в базе данных
        db_column_name = self.get_db_column_name(column_name)

        if db_column_name:
            # Заполняем данные из базы данных
            self.auto_fill_from_database(target_column, db_column_name)

    def get_db_column_name(self, column_name):
        column_mapping = {
            "Device ID": "id_device_clients_devices",
            "Device Model ID (*)": "id_directory_miners_clients_devices",
            "Container ID": "id_containers_clients_devices",
            "Place in Container": "id_place_clients_devices",
            "MAC Address (*)": "mac_addr_clients_devices",
            "IP Address": "ip_addr_clients_devices",
            "Serial Number (*)": "sn_clients_devices",
            "Pool Profile ID": "id_clients_pool_profile_clients_devices"
        }
        return column_mapping.get(column_name)

    def auto_fill_from_database(self, target_column, db_column_name):
        print(f"target_column: {target_column}, db_column_name: {db_column_name}")
        if db_column_name not in self.db_data.columns:
            QMessageBox.warning(self, "Error", f"Column '{db_column_name}' is missing in the database.")
            return

        for row in range(self.table_widget.rowCount()):
            # Собираем значения ключевых столбцов текущей строки
            key_values = {}
            for col in range(self.table_widget.columnCount()):
                item = self.table_widget.item(row, col)
                if item and item.text():
                    header = self.table_widget.horizontalHeaderItem(col).text()
                    db_key = self.get_db_column_name(header)
                    if db_key:
                        key_values[db_key] = item.text().strip()

            if not key_values:
                print("Нет ключей для поиска")
                continue  # Нет ключей для поиска

            print(f"Row {row} key_values: {key_values}")  # Отладочная информация

            # Формируем запрос на основе доступных ключей
            query = pd.Series([True] * len(self.db_data))
            for key, value in key_values.items():
                query &= (self.db_data[key].astype(str).str.strip() == value)

            matching_rows = self.db_data[query]

            print(f"Row {row} matching_rows count: {len(matching_rows)}")  # Отладочная информация

            if not matching_rows.empty:
                value_to_fill = matching_rows[db_column_name].iloc[0]
                self.table_widget.setItem(row, target_column, QTableWidgetItem(str(value_to_fill)))
                print(f"Row {row} filled with {db_column_name}: {value_to_fill}")  # Отладочная информация
            else:
                print(f"Row {row} no matching data found")

    def generate_delete_query(self):
        if self.db_data is None or self.db_data.empty:
            QMessageBox.warning(self, "Warning", "Please load the database first.")
            return

        # Получаем все уникальные Device IDs
        device_ids = self.db_data['id_device_clients_devices'].dropna().unique()

        # Формируем запрос
        ids_str = ", ".join(map(str, device_ids))
        query = f"DELETE FROM clients_devices\nWHERE id_device_clients_devices IN (\n{ids_str}\n);"

        # Отображаем запрос в текстовом поле
        self.delete_query_text.setText(query)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
