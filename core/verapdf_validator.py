"""
veraPDF Integration Module
Handles running veraPDF validation and parsing results
"""
import subprocess
import json
import os
import sys
from typing import Dict, List, Any, Optional
from dataclasses import dataclass


@dataclass
class ValidationIssue:
    """Represents a single validation issue from veraPDF"""
    rule_id: str
    description: str
    severity: str  # "ERROR", "WARNING", "INFO"
    location: Optional[str] = None
    page_number: Optional[int] = None
    element_type: Optional[str] = None
    suggested_fix: Optional[str] = None


class VeraPDFValidator:
    """Handles veraPDF validation operations"""
    
    def __init__(self):
        self.verapdf_path = self._find_verapdf()
        self.is_available = self.verapdf_path is not None
        
    def _find_verapdf(self) -> Optional[str]:
        """Find veraPDF executable on the system"""
        # Check for bundled veraPDF first (when packaged with PyInstaller)
        if hasattr(sys, '_MEIPASS'):
            bundled_path = os.path.join(sys._MEIPASS, "verapdf", "veraPDF")
            if os.path.exists(bundled_path):
                return bundled_path
        
        # Check for veraPDF in the same directory as the application
        app_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        local_verapdf = os.path.join(app_dir, "verapdf", "veraPDF")
        if os.path.exists(local_verapdf):
            return local_verapdf
        
        # Common installation paths
        possible_paths = [
            "verapdf",  # In PATH (lowercase)
            "veraPDF",  # In PATH (camelCase)
            "/Users/brad/verapdf/verapdf",  # User installation
            "/usr/local/bin/veraPDF",
            "/usr/local/bin/verapdf",
            "/Applications/veraPDF.app/Contents/MacOS/veraPDF",  # macOS app
            "/Applications/veraPDF/veraPDF",
            "C:\\Program Files\\veraPDF\\veraPDF.exe",  # Windows
            os.path.expanduser("~/Applications/veraPDF/veraPDF"),  # User install
            os.path.expanduser("~/verapdf/verapdf"),  # User home install
        ]
        
        for path in possible_paths:
            try:
                result = subprocess.run([path, "--version"], 
                                      capture_output=True, 
                                      text=True, 
                                      timeout=10)
                if result.returncode == 0:
                    return path
            except (subprocess.TimeoutExpired, FileNotFoundError, OSError):
                continue
        
        return None
    
    def validate_pdf(self, pdf_path: str, profile: str = "ua1") -> List[ValidationIssue]:
        """
        Validate PDF with veraPDF and return issues
        
        Args:
            pdf_path: Path to PDF file
            profile: Validation profile (ua1, ua2, 1a, 1b, 2a, 2b, 3a, 3b)
        """
        if not self.is_available:
            return [ValidationIssue(
                rule_id="SETUP_ERROR",
                description="veraPDF is not installed or not found in PATH",
                severity="ERROR",
                suggested_fix="Please install veraPDF from https://verapdf.org/"
            )]
        
        if not os.path.exists(pdf_path):
            return [ValidationIssue(
                rule_id="FILE_ERROR",
                description=f"PDF file not found: {pdf_path}",
                severity="ERROR"
            )]
        
        try:
            # Set up environment with Java path
            env = os.environ.copy()
            java_home = "/opt/homebrew/opt/openjdk@11"
            if os.path.exists(java_home):
                env["JAVA_HOME"] = java_home
                env["PATH"] = f"{java_home}/bin:{env.get('PATH', '')}"
            
            # Run veraPDF with JSON output - fix flavour format
            cmd = [
                self.verapdf_path,
                "--format", "json",
                "--flavour", profile,  # Use profile directly, not "pdfa-{profile}"
                pdf_path
            ]
            
            print(f"DEBUG: Running veraPDF command: {' '.join(cmd)}")
            print(f"DEBUG: Java environment: JAVA_HOME={env.get('JAVA_HOME', 'Not set')}")
            
            result = subprocess.run(cmd, 
                                  capture_output=True, 
                                  text=True, 
                                  timeout=60,
                                  env=env)  # Pass the environment with Java
            
            print(f"DEBUG: veraPDF return code: {result.returncode}")
            print(f"DEBUG: veraPDF stdout: {result.stdout[:500]}...")
            print(f"DEBUG: veraPDF stderr: {result.stderr}")
            
            # veraPDF returns 0 for valid PDFs, 1 for invalid PDFs, >1 for errors
            if result.returncode > 1:
                error_msg = f"veraPDF validation failed with code {result.returncode}"
                if result.stderr:
                    error_msg += f": {result.stderr}"
                if result.stdout:
                    error_msg += f" (stdout: {result.stdout[:200]}...)"
                    
                return [ValidationIssue(
                    rule_id="VALIDATION_ERROR",
                    description=error_msg,
                    severity="ERROR"
                )]
            
            # Return code 0 or 1 means validation completed successfully
            # (0 = compliant, 1 = non-compliant)
            
            # Parse JSON output
            return self._parse_validation_results(result.stdout)
            
        except subprocess.TimeoutExpired:
            return [ValidationIssue(
                rule_id="TIMEOUT_ERROR",
                description="veraPDF validation timed out",
                severity="ERROR"
            )]
        except Exception as e:
            return [ValidationIssue(
                rule_id="UNKNOWN_ERROR",
                description=f"Unexpected error during validation: {str(e)}",
                severity="ERROR"
            )]
    
    def _parse_validation_results(self, json_output: str) -> List[ValidationIssue]:
        """Parse veraPDF JSON output into ValidationIssue objects"""
        try:
            data = json.loads(json_output)
            issues = []
            
            print(f"DEBUG: Parsing JSON structure...")
            
            # Navigate veraPDF JSON structure
            report = data.get("report", {})
            jobs = report.get("jobs", [])
            
            for job in jobs:
                # validationResult is a list, not a dict
                validation_results = job.get("validationResult", [])
                
                for validation_result in validation_results:
                    details = validation_result.get("details", {})
                    rule_summaries = details.get("ruleSummaries", [])
                    
                    print(f"DEBUG: Found {len(rule_summaries)} rule summaries")
                    
                    for rule_summary in rule_summaries:
                        # Extract rule information from the actual JSON structure
                        clause = rule_summary.get("clause", "Unknown")
                        test_number = rule_summary.get("testNumber", "")
                        rule_id = f"{clause}.{test_number}" if test_number else clause
                        
                        description = rule_summary.get("description", "No description")
                        rule_status = rule_summary.get("ruleStatus", "UNKNOWN")
                        
                        # Only add failed rules
                        if rule_status == "FAILED":
                            # Extract error details from checks
                            checks = rule_summary.get("checks", [])
                            error_details = []
                            
                            for check in checks:
                                if check.get("status") == "failed":
                                    error_msg = check.get("errorMessage", "")
                                    context = check.get("context", "")
                                    if error_msg:
                                        error_details.append(f"{error_msg} (Context: {context})")
                            
                            full_description = description
                            if error_details:
                                full_description += f" Details: {'; '.join(error_details[:2])}"  # Limit to 2 details
                            
                            issues.append(ValidationIssue(
                                rule_id=rule_id,
                                description=full_description,
                                severity="ERROR",
                                suggested_fix=self._get_suggested_fix(clause)
                            ))
                
                # Also check for processing errors
                processing_errors = job.get("processingErrors", [])
                for error in processing_errors:
                    issues.append(ValidationIssue(
                        rule_id="PROCESSING_ERROR",
                        description=error.get("message", "Processing error"),
                        severity="ERROR"
                    ))
            
            print(f"DEBUG: Parsed {len(issues)} validation issues")
            return issues
            
        except json.JSONDecodeError as e:
            return [ValidationIssue(
                rule_id="PARSE_ERROR",
                description=f"Failed to parse veraPDF output: {str(e)}",
                severity="ERROR"
            )]
    
    def _get_suggested_fix(self, rule_id: str) -> str:
        """Get suggested fix for common validation issues"""
        fixes = {
            "6.1.2-1": "Add document title in metadata",
            "6.1.2-2": "Set document language in metadata",
            "6.1.3-1": "Mark document as tagged for accessibility",
            "6.2.2-1": "Add structure tree root to document",
            "6.2.3-1": "Ensure all content is tagged with appropriate structure elements",
            "6.3.2-1": "Add alt text to images and figures",
            "6.4.2-1": "Use proper heading hierarchy (H1, H2, H3, etc.)",
            "6.4.3-1": "Add table headers and scope attributes",
            "6.5.1-1": "Ensure form fields have proper descriptions",
            "6.6.1-1": "Set logical reading order for content"
        }
        
        return fixes.get(rule_id, "Refer to PDF/UA specification for guidance")
    
    def get_installation_info(self) -> Dict[str, Any]:
        """Get information about veraPDF installation"""
        return {
            "is_available": self.is_available,
            "path": self.verapdf_path,
            "download_url": "https://verapdf.org/home/",
            "installation_guide": "https://docs.verapdf.org/install/"
        }
