"""
Sample PDF generator for testing
Creates a simple PDF with text and images for testing the accessibility tool
"""
import fitz
import os

def create_sample_pdf():
    """Create a sample PDF with various elements for testing"""
    
    # Create a new PDF document
    doc = fitz.open()
    
    # Page 1: Text content with different elements
    page1 = doc.new_page()
    
    # Add title
    page1.insert_text((50, 50), "Sample Document for Accessibility Testing", 
                     fontsize=20, color=(0, 0, 0))
    
    # Add heading
    page1.insert_text((50, 100), "Chapter 1: Introduction", 
                     fontsize=16, color=(0, 0, 0))
    
    # Add paragraph
    paragraph_text = """This is a sample paragraph that demonstrates various accessibility issues that need to be addressed. This text should be tagged as a paragraph element with appropriate structure."""
    
    page1.insert_text((50, 130), paragraph_text, 
                     fontsize=12, color=(0, 0, 0))
    
    # Add subheading
    page1.insert_text((50, 200), "1.1 Subheading Example", 
                     fontsize=14, color=(0, 0, 0))
    
    # Add more text
    more_text = """Here is additional content that follows the subheading. This content should also be properly structured for accessibility compliance."""
    
    page1.insert_text((50, 230), more_text, 
                     fontsize=12, color=(0, 0, 0))
    
    # Add a simple rectangle to simulate an image
    rect = fitz.Rect(50, 300, 200, 400)
    page1.draw_rect(rect, color=(0, 0, 1), fill=(0.8, 0.8, 1))
    page1.insert_text((60, 320), "Image Placeholder", 
                     fontsize=10, color=(0, 0, 0))
    
    # Page 2: More content
    page2 = doc.new_page()
    
    page2.insert_text((50, 50), "Chapter 2: Additional Content", 
                     fontsize=16, color=(0, 0, 0))
    
    # Add list-like content
    list_items = [
        "• First item in the list",
        "• Second item in the list", 
        "• Third item in the list"
    ]
    
    y_pos = 100
    for item in list_items:
        page2.insert_text((50, y_pos), item, fontsize=12, color=(0, 0, 0))
        y_pos += 25
    
    # Add table-like content
    page2.insert_text((50, 220), "Sample Table:", fontsize=14, color=(0, 0, 0))
    
    # Table headers
    page2.insert_text((50, 250), "Name", fontsize=12, color=(0, 0, 0))
    page2.insert_text((150, 250), "Age", fontsize=12, color=(0, 0, 0))
    page2.insert_text((200, 250), "City", fontsize=12, color=(0, 0, 0))
    
    # Table data
    page2.insert_text((50, 275), "John", fontsize=12, color=(0, 0, 0))
    page2.insert_text((150, 275), "25", fontsize=12, color=(0, 0, 0))
    page2.insert_text((200, 275), "New York", fontsize=12, color=(0, 0, 0))
    
    page2.insert_text((50, 300), "Jane", fontsize=12, color=(0, 0, 0))
    page2.insert_text((150, 300), "30", fontsize=12, color=(0, 0, 0))
    page2.insert_text((200, 300), "London", fontsize=12, color=(0, 0, 0))
    
    return doc

if __name__ == "__main__":
    # Create samples directory if it doesn't exist
    samples_dir = "samples"
    if not os.path.exists(samples_dir):
        os.makedirs(samples_dir)
    
    # Generate sample PDF
    doc = create_sample_pdf()
    output_path = os.path.join(samples_dir, "sample_document.pdf")
    doc.save(output_path)
    doc.close()
    
    print(f"Sample PDF created: {output_path}")
