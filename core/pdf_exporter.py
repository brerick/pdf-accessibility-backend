"""
PDF Exporter
Handles exporting PDFs with updated metadata and accessibility improvements
Phase 3 + Phase 4 Step 1 implementation with UX improvements
"""
import os
import json
from datetime import datetime
from typing import Dict, Any, Optional, Callable
import pikepdf
from pikepdf import Pdf, Dictionary, Name

from .structure_tree import StructureTreeCreator


class PDFExporter:
    """Handles PDF export with metadata and accessibility improvements"""
    
    def __init__(self):
        self.last_export_path = None
        self.structure_creator = StructureTreeCreator()  # Phase 4 Step 1
        self.progress_callback: Optional[Callable] = None
        
    def set_progress_callback(self, callback: Callable):
        """Set callback function for progress updates"""
        self.progress_callback = callback
        
    def _update_progress(self, step_name: str, step_description: str = "", progress: int = 0):
        """Internal helper to update progress"""
        if self.progress_callback:
            self.progress_callback(step_name, step_description, progress)
        
    def export_pdf_with_metadata(self, source_pdf_path: str, output_pdf_path: str, 
                                metadata: Dict[str, Any], sidecar_data: Optional[Dict[str, Any]] = None) -> bool:
        """
        Export PDF with updated metadata for accessibility compliance
        Phase 3 + Phase 4 Step 1: Now includes basic structure tree creation with progress tracking
        
        Args:
            source_pdf_path: Path to source PDF
            output_pdf_path: Path for output PDF
            metadata: Dictionary containing metadata updates
            sidecar_data: Optional sidecar data for future structure tree updates
            
        Returns:
            bool: True if export successful, False otherwise
        """
        try:
            # Step 1: Initialize
            self._update_progress("Initializing Export", "Opening source PDF file...", 0)
            
            # Open the PDF with pikepdf
            with Pdf.open(source_pdf_path) as pdf:
                
                # Step 2: Update metadata
                self._update_progress("Updating Metadata", "Setting document properties and accessibility flags...", 20)
                self._update_document_metadata(pdf, metadata)
                self._set_accessibility_flags(pdf, metadata)
                
                # Step 3: Create structure tree
                self._update_progress("Creating Structure Tree", "Building PDF accessibility structure...", 40)
                structure_success = self.structure_creator.create_basic_structure_tree(pdf)
                
                if not structure_success:
                    self._update_progress("Structure Tree Failed", "Failed to create basic structure tree", 40)
                    return False
                
                # Step 4: Create StructElems
                self._update_progress("Creating Elements", "Generating accessibility elements from content...", 60)
                elements_success = self.structure_creator.create_elements_from_pdf(pdf, source_pdf_path, sidecar_data)
                
                # Step 5: Marked Content Integration (Phase 4 Step 4)
                if elements_success and sidecar_data:
                    self._update_progress("Marked Content Integration", "Applying advanced accessibility features...", 80)
                    
                    # Create element mappings from sidecar data for marked content
                    element_mappings = self._create_element_mappings(sidecar_data)
                    
                    # Inject marked content operators
                    marked_content_success = self.structure_creator.inject_marked_content(
                        pdf, source_pdf_path, element_mappings
                    )
                    
                    # Update StructElems with marked content references
                    if marked_content_success:
                        try:
                            self.structure_creator.update_struct_elements_with_marked_content(pdf)
                            self._update_progress("Advanced Features Complete", "Marked content integration successful", 85)
                        except Exception as e:
                            self._update_progress("Advanced Features Warning", f"StructElem update failed ({e}), but structure tree still valid", 85)
                    else:
                        self._update_progress("Advanced Features Warning", "Marked content integration failed, but structure tree still valid", 85)
                else:
                    self._update_progress("Standard Processing", "Using standard accessibility features", 80)
                
                # Step 6: Generate status report
                self._update_progress("Generating Report", "Creating accessibility status report...", 90)
                try:
                    structure_status = self.structure_creator.get_status_report(pdf)
                    element_summary = self.structure_creator.get_element_summary()
                    print(f"\n📊 Structure Tree Status:\n{structure_status}")
                    print(f"\n{element_summary}")
                except Exception as e:
                    print(f"⚠️ Error getting status report: {e}")
                    # Continue with export even if status report fails
                
                # Step 7: Save PDF
                self._update_progress("Saving PDF", "Writing accessible PDF to disk...", 95)
                pdf.save(output_pdf_path)
                
                # Step 8: Complete
                self._update_progress("Export Complete", f"Successfully saved to {os.path.basename(output_pdf_path)}", 100)
                
            self.last_export_path = output_pdf_path
            return True
            
        except Exception as e:
            error_msg = f"Error exporting PDF: {e}"
            print(error_msg)
            self._update_progress("Export Failed", error_msg, 0)
            return False
    
    def _update_document_metadata(self, pdf: Pdf, metadata: Dict[str, Any]):
        """Update PDF document metadata"""
        
        # Ensure Info dictionary exists
        if '/Info' not in pdf.Root:
            pdf.Root['/Info'] = Dictionary()
        
        info = pdf.Root['/Info']
        
        # Set title
        if 'title' in metadata and metadata['title']:
            info['/Title'] = metadata['title']
        
        # Set language at document level
        if 'language' in metadata and metadata['language']:
            pdf.Root['/Lang'] = metadata['language']
        
        # Set creator and producer
        info['/Creator'] = 'PDF Accessibility Remediation Tool'
        info['/Producer'] = 'PDF Accessibility Remediation Tool'
        
        # Set modification date
        info['/ModDate'] = f"D:{datetime.now().strftime('%Y%m%d%H%M%S')}"
        
        # Set subject to indicate accessibility improvements
        info['/Subject'] = 'PDF with accessibility improvements'
        
    def _set_accessibility_flags(self, pdf: Pdf, metadata: Dict[str, Any]):
        """Set PDF accessibility flags"""
        
        # Ensure MarkInfo dictionary exists
        if '/MarkInfo' not in pdf.Root:
            pdf.Root['/MarkInfo'] = Dictionary()
        
        mark_info = pdf.Root['/MarkInfo']
        
        # Set Marked flag to True to indicate the document is tagged
        if metadata.get('marked', True):
            mark_info['/Marked'] = True
        
        # Set UserProperties flag (indicates structure elements have user properties)
        mark_info['/UserProperties'] = False
        
        # Set Suspects flag (indicates no suspicious content)
        mark_info['/Suspects'] = False
        
    def generate_remediation_report(self, source_pdf_path: str, output_path: str,
                                  metadata: Dict[str, Any], sidecar_data: Dict[str, Any],
                                  validation_issues: list, format: str = 'json') -> bool:
        """
        Generate a remediation report showing what changes were made
        
        Args:
            source_pdf_path: Original PDF path
            output_path: Report output path
            metadata: Metadata changes made
            sidecar_data: Element modifications
            validation_issues: Original validation issues
            format: 'json' or 'html'
            
        Returns:
            bool: True if report generated successfully
        """
        try:
            report_data = self._build_report_data(
                source_pdf_path, metadata, sidecar_data, validation_issues
            )
            
            if format.lower() == 'html':
                return self._generate_html_report(report_data, output_path)
            else:
                return self._generate_json_report(report_data, output_path)
                
        except Exception as e:
            print(f"Error generating remediation report: {e}")
            return False
    
    def _build_report_data(self, source_pdf_path: str, metadata: Dict[str, Any],
                          sidecar_data: Dict[str, Any], validation_issues: list) -> Dict[str, Any]:
        """Build the report data structure"""
        
        # Count changes made
        element_changes = 0
        if sidecar_data:
            for page_data in sidecar_data.get('pages', {}).values():
                element_changes += len(page_data.get('elements', {}))
        
        return {
            'report_info': {
                'generated_at': datetime.now().isoformat(),
                'tool_name': 'PDF Accessibility Remediation Tool',
                'source_file': os.path.basename(source_pdf_path),
                'export_file': os.path.basename(self.last_export_path) if self.last_export_path else 'N/A'
            },
            'metadata_changes': {
                'title': metadata.get('title', 'Not set'),
                'language': metadata.get('language', 'Not set'),
                'marked_flag': metadata.get('marked', True),
                'accessibility_flags_set': True
            },
            'element_modifications': {
                'total_elements_modified': element_changes,
                'pages_with_changes': len(sidecar_data.get('pages', {})) if sidecar_data else 0,
                'details': sidecar_data or {}
            },
            'validation_summary': {
                'total_issues_found': len(validation_issues),
                'errors': len([i for i in validation_issues if getattr(i, 'severity', '') == 'ERROR']),
                'warnings': len([i for i in validation_issues if getattr(i, 'severity', '') == 'WARNING']),
                'issues': [
                    {
                        'rule_id': getattr(issue, 'rule_id', 'Unknown'),
                        'severity': getattr(issue, 'severity', 'Unknown'),
                        'description': getattr(issue, 'description', 'No description'),
                        'page': getattr(issue, 'page_number', None)
                    } for issue in validation_issues
                ]
            }
        }
    
    def _generate_json_report(self, report_data: Dict[str, Any], output_path: str) -> bool:
        """Generate JSON format report"""
        try:
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(report_data, f, indent=2, ensure_ascii=False)
            return True
        except Exception as e:
            print(f"Error generating JSON report: {e}")
            return False
    
    def _generate_html_report(self, report_data: Dict[str, Any], output_path: str) -> bool:
        """Generate HTML format report"""
        try:
            html_content = self._build_html_report(report_data)
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(html_content)
            return True
        except Exception as e:
            print(f"Error generating HTML report: {e}")
            return False
    
    def _build_html_report(self, data: Dict[str, Any]) -> str:
        """Build HTML report content"""
        report_info = data['report_info']
        metadata_changes = data['metadata_changes']
        element_mods = data['element_modifications']
        validation = data['validation_summary']
        
        html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>PDF Accessibility Remediation Report</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 20px; line-height: 1.6; }}
        .header {{ background-color: #f4f4f4; padding: 20px; border-radius: 5px; }}
        .section {{ margin: 20px 0; padding: 15px; border: 1px solid #ddd; border-radius: 5px; }}
        .success {{ color: green; }}
        .warning {{ color: orange; }}
        .error {{ color: red; }}
        table {{ width: 100%; border-collapse: collapse; margin: 10px 0; }}
        th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
        th {{ background-color: #f2f2f2; }}
        .issue-error {{ background-color: #ffebee; }}
        .issue-warning {{ background-color: #fff3e0; }}
    </style>
</head>
<body>
    <div class="header">
        <h1>PDF Accessibility Remediation Report</h1>
        <p><strong>Generated:</strong> {report_info['generated_at']}</p>
        <p><strong>Tool:</strong> {report_info['tool_name']}</p>
        <p><strong>Source File:</strong> {report_info['source_file']}</p>
        <p><strong>Output File:</strong> {report_info['export_file']}</p>
    </div>
    
    <div class="section">
        <h2>Metadata Changes</h2>
        <table>
            <tr><th>Property</th><th>Value</th></tr>
            <tr><td>Document Title</td><td>{metadata_changes['title']}</td></tr>
            <tr><td>Document Language</td><td>{metadata_changes['language']}</td></tr>
            <tr><td>Marked as Tagged</td><td class="success">{'Yes' if metadata_changes['marked_flag'] else 'No'}</td></tr>
            <tr><td>Accessibility Flags Set</td><td class="success">{'Yes' if metadata_changes['accessibility_flags_set'] else 'No'}</td></tr>
        </table>
    </div>
    
    <div class="section">
        <h2>Element Modifications</h2>
        <p><strong>Total Elements Modified:</strong> {element_mods['total_elements_modified']}</p>
        <p><strong>Pages with Changes:</strong> {element_mods['pages_with_changes']}</p>
    </div>
    
    <div class="section">
        <h2>Validation Summary</h2>
        <p><strong>Total Issues Found:</strong> {validation['total_issues_found']}</p>
        <p><strong>Errors:</strong> <span class="error">{validation['errors']}</span></p>
        <p><strong>Warnings:</strong> <span class="warning">{validation['warnings']}</span></p>
        
        <h3>Issues Details</h3>
        <table>
            <tr><th>Rule ID</th><th>Severity</th><th>Description</th><th>Page</th></tr>"""
        
        for issue in validation['issues']:
            severity_class = f"issue-{issue['severity'].lower()}" if issue['severity'] != 'Unknown' else ""
            page_text = str(issue['page']) if issue['page'] else 'N/A'
            html += f"""
            <tr class="{severity_class}">
                <td>{issue['rule_id']}</td>
                <td>{issue['severity']}</td>
                <td>{issue['description']}</td>
                <td>{page_text}</td>
            </tr>"""
        
        html += """
        </table>
    </div>
    
    <div class="section">
        <h2>Next Steps</h2>
        <p>This report shows the accessibility improvements made to your PDF. Consider the following:</p>
        <ul>
            <li>Review any remaining validation errors and warnings</li>
            <li>Test the PDF with screen readers for usability</li>
            <li>Verify that all content has appropriate roles and structure</li>
            <li>Check that images have meaningful alternative text</li>
        </ul>
    </div>
</body>
</html>"""
        
        return html

    def _create_element_mappings(self, sidecar_data: Dict[str, Any]) -> Dict[str, Dict]:
        """
        Create element mappings for marked content integration
        
        Args:
            sidecar_data: Sidecar data with element information
            
        Returns:
            Dict mapping element IDs to their properties
        """
        element_mappings = {}
        
        try:
            if not sidecar_data or 'pages' not in sidecar_data:
                print("⚠️ No sidecar data or pages found for element mappings")
                return element_mappings
            
            for page_num, page_data in sidecar_data['pages'].items():
                if not isinstance(page_data, dict) or 'elements' not in page_data:
                    continue
                    
                elements = page_data['elements']
                
                # Handle both list and dict formats
                if isinstance(elements, list):
                    for element in elements:
                        if isinstance(element, dict) and 'id' in element:
                            element_mappings[element['id']] = {
                                'role': element.get('role', element.get('properties', {}).get('role', 'P')),
                                'title': element.get('title', f"Element {element['id']}"),
                                'page': int(page_num),
                                'properties': element.get('properties', {}),
                                'element_type': element.get('role', 'P')  # Add explicit type field
                            }
                elif isinstance(elements, dict):
                    for elem_id, element in elements.items():
                        if isinstance(element, dict):
                            # Get role from element or properties
                            role = element.get('role')
                            if not role and 'properties' in element:
                                role = element['properties'].get('role', 'P')
                            if not role:
                                role = 'P'
                                
                            element_mappings[elem_id] = {
                                'role': role,
                                'title': element.get('title', f"Element {elem_id}"),
                                'page': int(page_num),
                                'properties': element.get('properties', {}),
                                'element_type': role  # Add explicit type field
                            }
            
            print(f"📋 Created {len(element_mappings)} element mappings for marked content")
            return element_mappings
            
        except Exception as e:
            print(f"❌ Error creating element mappings: {e}")
            print(f"📋 Sidecar data structure: {type(sidecar_data)}")
            return {}
