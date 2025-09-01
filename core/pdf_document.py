"""
PDF Document Handler
Manages PDF loading, page rendering, and basic operations using PyMuPDF
"""
import fitz
import json
from typing import List, Dict, Any, Optional


class PDFDocument:
    def __init__(self, file_path: str = None):
        self.file_path = file_path
        self.doc = None
        self.sidecar_data = {}
        self.total_pages = 0
        
        if file_path:
            self.load(file_path)
    
    def load(self, file_path: str) -> bool:
        """Load a PDF document"""
        try:
            self.file_path = file_path
            self.doc = fitz.open(file_path)
            self.total_pages = len(self.doc)
            self._init_sidecar()
            return True
        except Exception as e:
            print(f"Error loading PDF: {e}")
            return False
    
    def _init_sidecar(self):
        """Initialize sidecar JSON structure for tracking edits"""
        self.sidecar_data = {
            "document": {
                "title": "",
                "language": "en-US",
                "tagged": False
            },
            "pages": {}
        }
        
        # Initialize page data
        for page_num in range(self.total_pages):
            self.sidecar_data["pages"][str(page_num)] = {
                "elements": []
            }
    
    def get_page_pixmap(self, page_num: int, zoom: float = 1.0):
        """Get rendered pixmap for a page"""
        if not self.doc or page_num >= self.total_pages:
            return None
        
        try:
            page = self.doc.load_page(page_num)
            matrix = fitz.Matrix(zoom, zoom)
            return page.get_pixmap(matrix=matrix)
        except Exception as e:
            print(f"Error rendering page {page_num}: {e}")
            return None
    
    def get_text_blocks(self, page_num: int) -> List[Dict]:
        """Extract text blocks from a page"""
        if not self.doc or page_num >= self.total_pages:
            return []
        
        try:
            page = self.doc.load_page(page_num)
            blocks = page.get_text("blocks")
            
            # Convert to our format
            text_blocks = []
            for i, block in enumerate(blocks):
                if len(block) >= 5:  # Valid text block
                    text_blocks.append({
                        "id": f"text_{page_num}_{i}",
                        "type": "text",
                        "bbox": [block[0], block[1], block[2], block[3]],
                        "text": block[4].strip(),
                        "role": "P",  # Default role
                        "properties": {}
                    })
            return text_blocks
        except Exception as e:
            print(f"Error extracting text blocks from page {page_num}: {e}")
            return []
    
    def get_image_blocks(self, page_num: int) -> List[Dict]:
        """Extract image rectangles from a page"""
        if not self.doc or page_num >= self.total_pages:
            return []
        
        try:
            page = self.doc.load_page(page_num)
            image_list = page.get_images()
            
            image_blocks = []
            for i, img in enumerate(image_list):
                # Get image rectangle
                xref = img[0]
                bbox = page.get_image_rects(xref)
                if bbox:
                    for j, rect in enumerate(bbox):
                        image_blocks.append({
                            "id": f"image_{page_num}_{i}_{j}",
                            "type": "image",
                            "bbox": [rect.x0, rect.y0, rect.x1, rect.y1],
                            "role": "Figure",
                            "properties": {
                                "alt_text": ""
                            }
                        })
            return image_blocks
        except Exception as e:
            print(f"Error extracting images from page {page_num}: {e}")
            return []
    
    def update_element_properties(self, page_num: int, element_id: str, properties: Dict):
        """Update properties for an element in the sidecar"""
        print(f"DEBUG PDFDocument: Updating page {page_num}, element {element_id}, properties {properties}")
        
        page_key = str(page_num)
        if page_key not in self.sidecar_data["pages"]:
            print(f"DEBUG PDFDocument: Page {page_key} not found in sidecar")
            return False

        # Find and update element
        for element in self.sidecar_data["pages"][page_key]["elements"]:
            if element["id"] == element_id:
                print(f"DEBUG PDFDocument: Found element {element_id}, updating...")
                element["properties"].update(properties)
                if "role" in properties:
                    element["role"] = properties["role"]
                if "bbox" in properties:
                    element["bbox"] = properties["bbox"]
                print(f"DEBUG PDFDocument: Element updated: {element}")
                return True

        # Element not found, add it
        print(f"DEBUG PDFDocument: Element {element_id} not found, creating new...")
        new_element = {
            "id": element_id,
            "properties": properties,
            "role": properties.get("role", "P")
        }
        self.sidecar_data["pages"][page_key]["elements"].append(new_element)
        print(f"DEBUG PDFDocument: Created new element: {new_element}")
        return True

    def get_page_elements_with_properties(self, page_num: int) -> List[Dict]:
        """Get page elements merged with saved properties from sidecar"""
        # Get raw elements from PDF
        text_blocks = self.get_text_blocks(page_num)
        image_blocks = self.get_image_blocks(page_num)
        elements = text_blocks + image_blocks
        
        # Get saved properties from sidecar
        page_key = str(page_num)
        saved_elements = {}
        sidecar_only_elements = []
        
        if page_key in self.sidecar_data["pages"]:
            for saved_element in self.sidecar_data["pages"][page_key]["elements"]:
                element_id = saved_element["id"]
                saved_elements[element_id] = saved_element
                
                # Check if this element exists in PDF (has bbox from PDF extraction)
                found_in_pdf = any(e["id"] == element_id for e in elements)
                if not found_in_pdf:
                    # This is a newly created element, reconstruct it
                    reconstructed_element = {
                        "id": element_id,
                        "type": "text" if "text_" in element_id else "image",
                        "bbox": saved_element.get("bbox", [0, 0, 100, 20]),
                        "text": saved_element.get("text", ""),
                        "role": saved_element.get("role", "P"),
                        "properties": saved_element.get("properties", {})
                    }
                    sidecar_only_elements.append(reconstructed_element)
        
        # Add sidecar-only elements to the list
        elements.extend(sidecar_only_elements)
        
        # Merge properties for PDF-extracted elements
        for element in elements:
            element_id = element["id"]
            if element_id in saved_elements:
                saved_data = saved_elements[element_id]
                # Update role if saved
                if "role" in saved_data:
                    element["role"] = saved_data["role"]
                # Update bbox if saved (for resized elements)
                if "bbox" in saved_data:
                    element["bbox"] = saved_data["bbox"]
                # Merge properties
                if "properties" in saved_data:
                    if "properties" not in element:
                        element["properties"] = {}
                    element["properties"].update(saved_data["properties"])
        
        return elements
    
    def save_sidecar(self, output_path: str = None) -> bool:
        """Save sidecar JSON file"""
        if not output_path and self.file_path:
            output_path = self.file_path.replace('.pdf', '_sidecar.json')
        
        try:
            with open(output_path, 'w') as f:
                json.dump(self.sidecar_data, f, indent=2)
            return True
        except Exception as e:
            print(f"Error saving sidecar: {e}")
            return False
    
    def load_sidecar(self, sidecar_path: str) -> bool:
        """Load existing sidecar JSON file"""
        try:
            with open(sidecar_path, 'r') as f:
                self.sidecar_data = json.load(f)
            return True
        except Exception as e:
            print(f"Error loading sidecar: {e}")
            return False
    
    def close(self):
        """Close the PDF document"""
        if self.doc:
            self.doc.close()
            self.doc = None
