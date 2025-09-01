"""
PDF Viewer Widget
Handles PDF page rendering, zoom, and element selection
"""
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QScrollArea, 
                             QLabel, QPushButton, QSpinBox, QSlider, QMenu)
from PyQt6.QtCore import Qt, pyqtSignal, QPoint
from PyQt6.QtGui import QPixmap, QImage, QPainter, QPen, QBrush, QColor, QAction, QCursor
import fitz
from typing import List, Dict, Any, Optional


class PDFPageWidget(QLabel):
    """Widget for displaying a single PDF page with element selection"""
    element_selected = pyqtSignal(dict)
    element_created = pyqtSignal(dict)  # New element created
    element_deleted = pyqtSignal(str)   # Element deleted (ID)
    element_resized = pyqtSignal(str, list)  # Element resized (ID, new bbox)
    
    def __init__(self):
        super().__init__()
        self.page_pixmap = None
        self.elements = []
        self.selected_element = None
        self.zoom_factor = 1.0
        
        # Element manipulation state
        self.creating_element = False
        self.creation_start = None
        self.creation_current = None
        self.resizing_element = None
        self.resize_handle = None  # Which handle is being dragged
        
        self.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignLeft)
        self.setMinimumSize(400, 400)
        self.setStyleSheet("border: 1px solid gray;")
        
        # Enable context menu
        self.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.customContextMenuRequested.connect(self.show_context_menu)
    
    def show_context_menu(self, position):
        """Show context menu for element operations"""
        menu = QMenu(self)
        
        # Add actions
        create_text_action = QAction("Create Text Element", self)
        create_text_action.triggered.connect(lambda: self.start_element_creation("text"))
        menu.addAction(create_text_action)
        
        create_image_action = QAction("Create Image Element", self)
        create_image_action.triggered.connect(lambda: self.start_element_creation("image"))
        menu.addAction(create_image_action)
        
        # If an element is selected, add delete option
        if self.selected_element:
            menu.addSeparator()
            delete_action = QAction(f"Delete Element ({self.selected_element['id']})", self)
            delete_action.triggered.connect(self.delete_selected_element)
            menu.addAction(delete_action)
        
        menu.exec(self.mapToGlobal(position))
    
    def start_element_creation(self, element_type):
        """Start creating a new element"""
        self.creating_element = True
        self.creation_type = element_type
        self.setCursor(QCursor(Qt.CursorShape.CrossCursor))
    
    def delete_selected_element(self):
        """Delete the currently selected element"""
        if self.selected_element:
            element_id = self.selected_element['id']
            # Remove from elements list
            self.elements = [e for e in self.elements if e['id'] != element_id]
            self.selected_element = None
            self.update_display()
            self.element_deleted.emit(element_id)
        
    def set_page_data(self, pixmap: QPixmap, elements: List[Dict]):
        """Set page pixmap and element data"""
        self.page_pixmap = pixmap
        self.elements = elements
        self.selected_element = None
        
        # Set the widget size to match the pixmap
        if pixmap:
            self.resize(pixmap.size())
            self.setMinimumSize(pixmap.size())
        
        self.update_display()
        
    def update_display(self):
        """Update the displayed page with element overlays"""
        if not self.page_pixmap:
            return
            
        # Scale the pixmap according to zoom factor
        scaled_pixmap = self.page_pixmap.scaled(
            self.page_pixmap.size() * self.zoom_factor,
            Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.SmoothTransformation
        )
        
        # Create a copy to draw on
        display_pixmap = scaled_pixmap.copy()
        painter = QPainter(display_pixmap)
        
        # Draw element boundaries
        for element in self.elements:
            bbox = element.get('bbox', [])
            if len(bbox) == 4:
                x0, y0, x1, y1 = bbox
                
                # Scale coordinates by zoom factor
                x0 *= self.zoom_factor
                y0 *= self.zoom_factor
                x1 *= self.zoom_factor
                y1 *= self.zoom_factor
                
                # Choose color based on element type and selection
                if element == self.selected_element:
                    pen = QPen(QColor(255, 0, 0), 2)  # Red for selected
                    brush = QBrush(QColor(255, 0, 0, 50))  # Semi-transparent red
                elif element.get('type') == 'text':
                    pen = QPen(QColor(0, 0, 255), 1)  # Blue for text
                    brush = QBrush(QColor(0, 0, 255, 30))
                else:  # image
                    pen = QPen(QColor(0, 255, 0), 1)  # Green for images
                    brush = QBrush(QColor(0, 255, 0, 30))
                
                painter.setPen(pen)
                painter.setBrush(brush)
                painter.drawRect(int(x0), int(y0), int(x1-x0), int(y1-y0))
                
                # Draw resize handles for selected element
                if element == self.selected_element:
                    self.draw_resize_handles(painter, x0, y0, x1, y1)
        
        # Draw creation preview
        if self.creating_element and self.creation_start and self.creation_current:
            x0 = min(self.creation_start.x(), self.creation_current.x()) * self.zoom_factor
            y0 = min(self.creation_start.y(), self.creation_current.y()) * self.zoom_factor
            x1 = max(self.creation_start.x(), self.creation_current.x()) * self.zoom_factor
            y1 = max(self.creation_start.y(), self.creation_current.y()) * self.zoom_factor
            
            pen = QPen(QColor(255, 165, 0), 2, Qt.PenStyle.DashLine)  # Orange dashed
            painter.setPen(pen)
            painter.setBrush(QBrush())  # No fill
            painter.drawRect(int(x0), int(y0), int(x1-x0), int(y1-y0))
        
        painter.end()
        self.setPixmap(display_pixmap)
    
    def draw_resize_handles(self, painter, x0, y0, x1, y1):
        """Draw resize handles around selected element"""
        handle_size = 8
        handle_brush = QBrush(QColor(255, 255, 255))
        handle_pen = QPen(QColor(0, 0, 0), 1)
        
        painter.setBrush(handle_brush)
        painter.setPen(handle_pen)
        
        # Corner handles
        positions = [
            (x0 - handle_size//2, y0 - handle_size//2),  # top-left
            (x1 - handle_size//2, y0 - handle_size//2),  # top-right
            (x0 - handle_size//2, y1 - handle_size//2),  # bottom-left
            (x1 - handle_size//2, y1 - handle_size//2),  # bottom-right
            # Edge handles
            ((x0 + x1) / 2 - handle_size//2, y0 - handle_size//2),  # top
            ((x0 + x1) / 2 - handle_size//2, y1 - handle_size//2),  # bottom
            (x0 - handle_size//2, (y0 + y1) / 2 - handle_size//2),  # left
            (x1 - handle_size//2, (y0 + y1) / 2 - handle_size//2),  # right
        ]
        
        for x, y in positions:
            painter.drawRect(int(x), int(y), handle_size, handle_size)
        
    def mousePressEvent(self, ev):
        """Handle mouse clicks for element selection, creation, and resizing"""
        if not self.page_pixmap or ev.button() != Qt.MouseButton.LeftButton:
            return
            
        click_pos = ev.pos()
        page_x = click_pos.x() / self.zoom_factor
        page_y = click_pos.y() / self.zoom_factor
        
        # Handle element creation
        if self.creating_element:
            self.creation_start = QPoint(int(page_x), int(page_y))
            self.creation_current = self.creation_start
            return
        
        # Check for resize handles on selected element
        if self.selected_element:
            handle = self.get_resize_handle(page_x, page_y, self.selected_element)
            if handle:
                self.resizing_element = self.selected_element
                self.resize_handle = handle
                self.setCursor(self.get_resize_cursor(handle))
                return
        
        # Find clicked element
        clicked_element = None
        for element in self.elements:
            bbox = element.get('bbox', [])
            if len(bbox) == 4:
                x0, y0, x1, y1 = bbox
                if x0 <= page_x <= x1 and y0 <= page_y <= y1:
                    clicked_element = element
                    break
        
        # Update selection
        if clicked_element != self.selected_element:
            self.selected_element = clicked_element
            self.update_display()
            
            if clicked_element:
                self.element_selected.emit(clicked_element)
    
    def mouseMoveEvent(self, ev):
        """Handle mouse movement for element creation and resizing"""
        if not self.page_pixmap:
            return
            
        page_x = ev.pos().x() / self.zoom_factor
        page_y = ev.pos().y() / self.zoom_factor
        
        # Handle element creation
        if self.creating_element and self.creation_start:
            self.creation_current = QPoint(int(page_x), int(page_y))
            self.update_display()
            return
        
        # Handle element resizing
        if self.resizing_element and self.resize_handle:
            self.resize_element(page_x, page_y)
            self.update_display()
            return
        
        # Update cursor for resize handles
        if self.selected_element:
            handle = self.get_resize_handle(page_x, page_y, self.selected_element)
            if handle:
                self.setCursor(self.get_resize_cursor(handle))
            else:
                self.setCursor(QCursor(Qt.CursorShape.ArrowCursor))
    
    def mouseReleaseEvent(self, ev):
        """Handle mouse release for completing operations"""
        if ev.button() != Qt.MouseButton.LeftButton:
            return
        
        # Complete element creation
        if self.creating_element and self.creation_start and self.creation_current:
            self.complete_element_creation()
            
        # Complete element resizing
        if self.resizing_element:
            # Emit signal to save the resize
            element_id = self.resizing_element['id']
            new_bbox = self.resizing_element['bbox']
            self.element_resized.emit(element_id, new_bbox)
            
            self.resizing_element = None
            self.resize_handle = None
            self.setCursor(QCursor(Qt.CursorShape.ArrowCursor))
    
    def get_resize_handle(self, x, y, element):
        """Check if click is on a resize handle"""
        bbox = element.get('bbox', [])
        if len(bbox) != 4:
            return None
            
        x0, y0, x1, y1 = bbox
        handle_size = 8  # pixels
        
        # Check corners and edges
        if abs(x - x0) <= handle_size and abs(y - y0) <= handle_size:
            return "top-left"
        elif abs(x - x1) <= handle_size and abs(y - y0) <= handle_size:
            return "top-right"
        elif abs(x - x0) <= handle_size and abs(y - y1) <= handle_size:
            return "bottom-left"
        elif abs(x - x1) <= handle_size and abs(y - y1) <= handle_size:
            return "bottom-right"
        elif abs(x - (x0 + x1) / 2) <= handle_size and abs(y - y0) <= handle_size:
            return "top"
        elif abs(x - (x0 + x1) / 2) <= handle_size and abs(y - y1) <= handle_size:
            return "bottom"
        elif abs(x - x0) <= handle_size and abs(y - (y0 + y1) / 2) <= handle_size:
            return "left"
        elif abs(x - x1) <= handle_size and abs(y - (y0 + y1) / 2) <= handle_size:
            return "right"
        
        return None
    
    def get_resize_cursor(self, handle):
        """Get appropriate cursor for resize handle"""
        cursor_map = {
            "top-left": Qt.CursorShape.SizeFDiagCursor,
            "top-right": Qt.CursorShape.SizeBDiagCursor,
            "bottom-left": Qt.CursorShape.SizeBDiagCursor,
            "bottom-right": Qt.CursorShape.SizeFDiagCursor,
            "top": Qt.CursorShape.SizeVerCursor,
            "bottom": Qt.CursorShape.SizeVerCursor,
            "left": Qt.CursorShape.SizeHorCursor,
            "right": Qt.CursorShape.SizeHorCursor,
        }
        return QCursor(cursor_map.get(handle, Qt.CursorShape.ArrowCursor))
    
    def resize_element(self, x, y):
        """Resize the selected element based on handle being dragged"""
        if not self.resizing_element or not self.resize_handle:
            return
            
        bbox = self.resizing_element.get('bbox', [])
        if len(bbox) != 4:
            return
            
        x0, y0, x1, y1 = bbox
        
        # Update bbox based on handle
        if "left" in self.resize_handle:
            x0 = min(x, x1 - 10)  # Minimum width
        if "right" in self.resize_handle:
            x1 = max(x, x0 + 10)
        if "top" in self.resize_handle:
            y0 = min(y, y1 - 10)  # Minimum height
        if "bottom" in self.resize_handle:
            y1 = max(y, y0 + 10)
            
        # Update element bbox
        self.resizing_element['bbox'] = [x0, y0, x1, y1]
    
    def complete_element_creation(self):
        """Complete creating a new element"""
        if not self.creation_start or not self.creation_current:
            return
            
        # Calculate bounding box
        x0 = min(self.creation_start.x(), self.creation_current.x())
        y0 = min(self.creation_start.y(), self.creation_current.y())
        x1 = max(self.creation_start.x(), self.creation_current.x())
        y1 = max(self.creation_start.y(), self.creation_current.y())
        
        # Ensure minimum size
        if x1 - x0 < 20 or y1 - y0 < 10:
            self.reset_creation_state()
            return
            
        # Create new element
        element_id = f"{self.creation_type}_{len(self.elements)}"
        new_element = {
            "id": element_id,
            "type": self.creation_type,
            "bbox": [x0, y0, x1, y1],
            "text": "New Element" if self.creation_type == "text" else "",
            "role": "P" if self.creation_type == "text" else "Figure",
            "properties": {}
        }
        
        # Add to elements and select
        self.elements.append(new_element)
        self.selected_element = new_element
        
        # Emit signal
        self.element_created.emit(new_element)
        
        # Reset state
        self.reset_creation_state()
        self.update_display()
    
    def reset_creation_state(self):
        """Reset element creation state"""
        self.creating_element = False
        self.creation_start = None
        self.creation_current = None
        self.setCursor(QCursor(Qt.CursorShape.ArrowCursor))
                
    def set_zoom(self, zoom_factor: float):
        """Set zoom factor and update display"""
        self.zoom_factor = zoom_factor
        if self.page_pixmap:
            # Scale the pixmap and resize the widget
            scaled_size = self.page_pixmap.size() * zoom_factor
            self.resize(scaled_size)
            self.setMinimumSize(scaled_size)
            self.update_display()


class PDFViewer(QWidget):
    """PDF Viewer with navigation and zoom controls"""
    element_selected = pyqtSignal(dict)
    element_created = pyqtSignal(dict)
    element_deleted = pyqtSignal(str)
    element_resized = pyqtSignal(str, list)
    
    def __init__(self):
        super().__init__()
        self.pdf_document = None
        self.current_page = 0
        self.zoom_factor = 1.0
        
        self.setup_ui()
        
    def setup_ui(self):
        """Setup viewer UI"""
        layout = QVBoxLayout(self)
        
        # Navigation controls
        nav_layout = QHBoxLayout()
        
        self.prev_button = QPushButton("◀ Previous")
        self.prev_button.clicked.connect(self.prev_page)
        nav_layout.addWidget(self.prev_button)
        
        self.page_spinbox = QSpinBox()
        self.page_spinbox.setMinimum(1)
        self.page_spinbox.valueChanged.connect(self.goto_page)
        nav_layout.addWidget(self.page_spinbox)
        
        self.page_label = QLabel("/ 0")
        nav_layout.addWidget(self.page_label)
        
        self.next_button = QPushButton("Next ▶")
        self.next_button.clicked.connect(self.next_page)
        nav_layout.addWidget(self.next_button)
        
        nav_layout.addStretch()
        
        # Zoom controls
        zoom_layout = QHBoxLayout()
        
        self.zoom_out_button = QPushButton("−")
        self.zoom_out_button.clicked.connect(self.zoom_out)
        zoom_layout.addWidget(self.zoom_out_button)
        
        self.zoom_slider = QSlider(Qt.Orientation.Horizontal)
        self.zoom_slider.setMinimum(25)
        self.zoom_slider.setMaximum(300)
        self.zoom_slider.setValue(100)
        self.zoom_slider.valueChanged.connect(self.set_zoom_percentage)
        zoom_layout.addWidget(self.zoom_slider)
        
        self.zoom_in_button = QPushButton("+")
        self.zoom_in_button.clicked.connect(self.zoom_in)
        zoom_layout.addWidget(self.zoom_in_button)
        
        self.zoom_label = QLabel("100%")
        zoom_layout.addWidget(self.zoom_label)
        
        nav_layout.addLayout(zoom_layout)
        layout.addLayout(nav_layout)
        
        # PDF page display
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignLeft)
        self.scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self.scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        
        self.page_widget = PDFPageWidget()
        self.page_widget.element_selected.connect(self.element_selected.emit)
        self.page_widget.element_created.connect(self.element_created.emit)
        self.page_widget.element_deleted.connect(self.element_deleted.emit)
        self.page_widget.element_resized.connect(self.element_resized.emit)
        
        self.scroll_area.setWidget(self.page_widget)
        layout.addWidget(self.scroll_area)
        
    def set_document(self, pdf_document):
        """Set the PDF document to display"""
        self.pdf_document = pdf_document
        if pdf_document and pdf_document.total_pages > 0:
            self.page_spinbox.setMaximum(pdf_document.total_pages)
            self.page_label.setText(f"/ {pdf_document.total_pages}")
            self.current_page = 0
            self.show_page(0)
        else:
            self.page_spinbox.setMaximum(0)
            self.page_label.setText("/ 0")
            
    def show_page(self, page_num: int):
        """Display a specific page"""
        if not self.pdf_document or page_num >= self.pdf_document.total_pages:
            return
            
        self.current_page = page_num
        self.page_spinbox.setValue(page_num + 1)
        
        # Get page pixmap
        pix = self.pdf_document.get_page_pixmap(page_num, self.zoom_factor)
        if pix:
            # Convert to QPixmap
            img_data = pix.tobytes("ppm")
            qimage = QImage.fromData(img_data)
            pixmap = QPixmap.fromImage(qimage)
            
            # Get page elements with merged properties from sidecar
            elements = self.pdf_document.get_page_elements_with_properties(page_num)
            
            # Update page display
            self.page_widget.set_page_data(pixmap, elements)
            
        self.update_navigation_state()
        
    def update_navigation_state(self):
        """Update navigation button states"""
        self.prev_button.setEnabled(self.current_page > 0)
        self.next_button.setEnabled(
            self.pdf_document and 
            self.current_page < self.pdf_document.total_pages - 1
        )
        
    def prev_page(self):
        """Go to previous page"""
        if self.current_page > 0:
            self.show_page(self.current_page - 1)
            
    def next_page(self):
        """Go to next page"""
        if (self.pdf_document and 
            self.current_page < self.pdf_document.total_pages - 1):
            self.show_page(self.current_page + 1)
            
    def goto_page(self, page_num: int):
        """Go to specific page (1-based)"""
        self.show_page(page_num - 1)
        
    def zoom_in(self):
        """Zoom in"""
        new_zoom = min(self.zoom_factor * 1.25, 3.0)
        self.set_zoom(new_zoom)
        
    def zoom_out(self):
        """Zoom out"""
        new_zoom = max(self.zoom_factor / 1.25, 0.25)
        self.set_zoom(new_zoom)
        
    def fit_width(self):
        """Fit page to viewer width"""
        # This is a simplified implementation
        self.set_zoom(1.0)
        
    def set_zoom_percentage(self, percentage: int):
        """Set zoom from percentage slider"""
        self.set_zoom(percentage / 100.0)
        
    def set_zoom(self, zoom_factor: float):
        """Set zoom factor"""
        self.zoom_factor = zoom_factor
        self.zoom_slider.setValue(int(zoom_factor * 100))
        self.zoom_label.setText(f"{int(zoom_factor * 100)}%")
        
        self.page_widget.set_zoom(zoom_factor)
        self.show_page(self.current_page)
