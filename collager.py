import os
import random
import string
from PyQt5.QtWidgets import QApplication, QMainWindow, QFileDialog, QLabel, QPushButton, QLineEdit, QVBoxLayout, QHBoxLayout, QWidget, QMessageBox
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QColor
from PIL import Image

class CollageGenerator(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("CollageIt")  # Updated window title

        # Create the main layout
        main_layout = QVBoxLayout()

        # Folder path input
        folder_layout = QHBoxLayout()
        self.folder_path_label = QLabel("Image Folder:")
        self.folder_path_label.setStyleSheet("color: white;")  # White text
        folder_layout.addWidget(self.folder_path_label)
        self.folder_path_entry = QLineEdit()
        self.folder_path_entry.setStyleSheet("background: white; color: black;")  # White background, black text
        folder_layout.addWidget(self.folder_path_entry)
        self.browse_button = QPushButton("Browse")
        self.browse_button.setStyleSheet("background: blue; color: white;")  # Blue button, white text
        self.browse_button.clicked.connect(self.browse_folder)
        folder_layout.addWidget(self.browse_button)
        main_layout.addLayout(folder_layout)

        # Canvas resolution input
        resolution_layout = QHBoxLayout()
        self.canvas_resolution_label = QLabel("Canvas Resolution:")
        self.canvas_resolution_label.setStyleSheet("color: white;")  # White text
        resolution_layout.addWidget(self.canvas_resolution_label)
        self.canvas_width_entry = QLineEdit()
        self.canvas_width_entry.setPlaceholderText("Width")
        self.canvas_width_entry.setStyleSheet("background: white; color: black;")  # White background, black text
        resolution_layout.addWidget(self.canvas_width_entry)
        self.canvas_height_entry = QLineEdit()
        self.canvas_height_entry.setPlaceholderText("Height")
        self.canvas_height_entry.setStyleSheet("background: white; color: black;")  # White background, black text
        resolution_layout.addWidget(self.canvas_height_entry)
        main_layout.addLayout(resolution_layout)

        # Generate button
        self.generate_button = QPushButton("Generate Collage")
        self.generate_button.setStyleSheet("background: blue; color: white;")  # Blue button, white text
        self.generate_button.clicked.connect(self.generate_collage)
        main_layout.addWidget(self.generate_button)

        # Status label
        self.status_label = QLabel("")
        self.status_label.setStyleSheet("color: white;")  # White text
        main_layout.addWidget(self.status_label)

        # Set the layout in a central widget
        central_widget = QWidget()
        central_widget.setLayout(main_layout)
        self.setCentralWidget(central_widget)

        # Set the background color of the main window
        self.setStyleSheet("background: black;")  # Black background

    def browse_folder(self):
        folder_selected = QFileDialog.getExistingDirectory(self, "Select Folder")
        self.folder_path_entry.setText(folder_selected)

    def generate_random_filename(self):
        return ''.join(random.choices(string.ascii_lowercase + string.digits, k=10)) + '.jpg'

    def generate_collage(self):
        image_folder = self.folder_path_entry.text()
        try:
            canvas_width = int(self.canvas_width_entry.text())
            canvas_height = int(self.canvas_height_entry.text())
        except ValueError:
            QMessageBox.warning(self, "Input Error", "Please enter valid integers for canvas width and height.")
            return

        if not image_folder or not canvas_width or not canvas_height:
            self.status_label.setText("Please specify the folder and canvas resolution.")
            return

        # Create the "collages" folder if it doesn't exist
        collages_folder = os.path.join(image_folder, "collages")
        if not os.path.exists(collages_folder):
            os.makedirs(collages_folder)

        output_file = os.path.join(collages_folder, self.generate_random_filename())

        if not os.access(image_folder, os.R_OK):
            QMessageBox.critical(self, "Error", "You do not have permission to read from this folder.")
            return

        try:
            self.status_label.setText("Starting collage generation...")
            images = self.load_images(image_folder)
            if not images:
                QMessageBox.warning(self, "No Images", "No valid images found in the specified folder.")
                return
            canvas = self.create_blank_canvas(canvas_width, canvas_height)
            final_collage = self.arrange_images_in_rows(canvas, images)
            self.save_collage_image(final_collage, output_file)
            self.status_label.setText(f"Collage generated and saved as {output_file}")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"An error occurred: {e}")
            print(f"Error: {e}")

    def load_images(self, image_folder):
        images = []
        for filename in os.listdir(image_folder):
            if filename.lower().endswith(('png', 'jpg', 'jpeg', 'gif')):
                try:
                    img = Image.open(os.path.join(image_folder, filename))
                    images.append(img)
                    print(f"Loaded image: {filename}")
                except IOError as e:
                    print(f"Error loading image {filename}: {e}")
        print(f"Total images loaded: {len(images)}")
        return images

    def resize_image_keep_aspect_ratio(self, img, max_width, max_height):
        original_width, original_height = img.size
        ratio = min(max_width / original_width, max_height / original_height)
        new_width = int(original_width * ratio)
        new_height = int(original_height * ratio)
        return img.resize((new_width, new_height), Image.LANCZOS)

    def arrange_images_in_rows(self, canvas, images):
        canvas_width, canvas_height = canvas.size
        x, y = 0, 0
        row_height = 0

        for img in images:
            img = self.resize_image_keep_aspect_ratio(img, canvas_width // 3, canvas_height // 3)
            img_width, img_height = img.size

            if x + img_width > canvas_width:
                x = 0
                y += row_height
                row_height = 0

            if y + img_height > canvas_height:
                break

            canvas.paste(img, (x, y))
            x += img_width
            row_height = max(row_height, img_height)

            print(f"Placed image at position ({x}, {y}) with size {img.size}")

        return canvas

    def save_collage_image(self, canvas, output_path):
        if os.path.exists(output_path):
            response = QMessageBox.question(self, "File Exists", "File already exists. Do you want to overwrite it?", QMessageBox.Yes | QMessageBox.No)
            if response == QMessageBox.No:
                return
        print(f"Saving collage to {output_path}")
        canvas.save(output_path, 'JPEG')
        print("Collage saved successfully!")

    def create_blank_canvas(self, width, height, color=(255, 255, 255)):
        print(f"Creating blank canvas of size {width}x{height}")
        return Image.new('RGB', (width, height), color)

if __name__ == "__main__":
    import sys
    app = QApplication(sys.argv)
    window = CollageGenerator()
    window.show()
    sys.exit(app.exec_())
