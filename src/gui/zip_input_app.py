"""
ZIP Code Input GUI

This module provides a simple GUI interface for entering ZIP codes and
initiating the data collection process.

File: src/gui/zip_input_app.py
"""

import os
import sys
import logging
import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
from typing import List, Dict, Optional, Tuple
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(Path("logs") / "app.log"),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

# Ensure the logs directory exists
os.makedirs(Path("logs"), exist_ok=True)

# Import our custom modules
try:
    from src.vendor_intake.utils.zip_state_mapper import ZipCodeMapper
    # These will be imported later as we develop them
    # from src.scrapers.crawl4ai_integration.potadvisor_crawler import PotAdvisorCrawler
except ImportError as e:
    logger.critical(f"Failed to import required modules: {str(e)}")
    sys.exit(1)

class ZipCodeInputApp:
    """Main application class for the ZIP code input GUI."""
    
    def __init__(self, root: tk.Tk):
        """
        Initialize the application.
        
        Args:
            root: The tkinter root window
        """
        self.root = root
        self.root.title("Loot's Ganja Guide - Data Collection")
        self.root.geometry("800x600")
        
        # Set up the ZIP code mapper
        self.zip_mapper = ZipCodeMapper()
        
        # Create and set up widgets
        self.create_widgets()
        
        # Center the window
        self.center_window()
        
        # Job tracking
        self.current_jobs = {}
        
        logger.info("Application initialized")
    
    def center_window(self) -> None:
        """Center the application window on the screen."""
        self.root.update_idletasks()
        width = self.root.winfo_width()
        height = self.root.winfo_height()
        x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        y = (self.root.winfo_screenheight() // 2) - (height // 2)
        self.root.geometry(f'{width}x{height}+{x}+{y}')
    
    def create_widgets(self) -> None:
        """Create and configure all GUI widgets."""
        # Create main frame
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Create and place widgets
        
        # Title
        title_label = ttk.Label(
            main_frame, 
            text="Loot's Ganja Guide - Cannabis Data Collection",
            font=("Helvetica", 16, "bold")
        )
        title_label.pack(pady=10)
        
        # ZIP code input frame
        input_frame = ttk.LabelFrame(main_frame, text="Enter ZIP Codes", padding="10")
        input_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Instructions
        instructions = ttk.Label(
            input_frame,
            text="Enter ZIP codes below (separated by commas, spaces, or new lines):",
            wraplength=700
        )
        instructions.pack(anchor=tk.W, pady=(0, 5))
        
        # ZIP code input
        self.zip_input = scrolledtext.ScrolledText(
            input_frame,
            height=8,
            width=70,
            wrap=tk.WORD
        )
        self.zip_input.pack(fill=tk.BOTH, expand=True, pady=5)
        
        # Button frame
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X, pady=10)
        
        # Run button
        self.run_button = ttk.Button(
            button_frame,
            text="Run Data Collection",
            command=self.run_data_collection
        )
        self.run_button.pack(side=tk.RIGHT, padx=5)
        
        # Clear button
        self.clear_button = ttk.Button(
            button_frame,
            text="Clear",
            command=self.clear_input
        )
        self.clear_button.pack(side=tk.RIGHT, padx=5)
        
        # Output frame
        output_frame = ttk.LabelFrame(main_frame, text="Output Log", padding="10")
        output_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Output log
        self.output_log = scrolledtext.ScrolledText(
            output_frame,
            height=12,
            width=70,
            wrap=tk.WORD,
            state=tk.DISABLED
        )
        self.output_log.pack(fill=tk.BOTH, expand=True)
        
        # Status bar
        self.status_var = tk.StringVar()
        self.status_var.set("Ready")
        self.status_bar = ttk.Label(
            self.root,
            textvariable=self.status_var,
            relief=tk.SUNKEN,
            anchor=tk.W
        )
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)
    
    def clear_input(self) -> None:
        """Clear the ZIP code input field."""
        self.zip_input.delete(1.0, tk.END)
    
    def log_message(self, message: str) -> None:
        """
        Add a message to the output log.
        
        Args:
            message: The message to add to the log
        """
        self.output_log.config(state=tk.NORMAL)
        self.output_log.insert(tk.END, message + "\n")
        self.output_log.see(tk.END)
        self.output_log.config(state=tk.DISABLED)
        logger.info(message)
    
    def set_status(self, message: str) -> None:
        """
        Update the status bar text.
        
        Args:
            message: The new status message
        """
        self.status_var.set(message)
        self.root.update_idletasks()
    
    def run_data_collection(self) -> None:
        """Process the entered ZIP codes and initiate data collection."""
        # Get ZIP codes from input
        zip_codes = self.zip_input.get(1.0, tk.END).strip()
        
        if not zip_codes:
            messagebox.showwarning("No Input", "Please enter at least one ZIP code.")
            return
        
        self.set_status("Processing ZIP codes...")
        self.log_message("Starting ZIP code processing...")
        
        try:
            # Process ZIP codes to group by state
            state_groups = self.zip_mapper.process_zip_codes(zip_codes)
            
            if not state_groups:
                self.set_status("No valid ZIP codes found.")
                self.log_message("No valid ZIP codes found. Please check your input.")
                messagebox.showwarning("No Valid ZIPs", "No valid ZIP codes were found. Please check your input.")
                return
            
            # Log the results
            total_zips = sum(len(zips) for zips in state_groups.values())
            self.log_message(f"Successfully processed {total_zips} ZIP codes across {len(state_groups)} states.")
            
            for state, zips in state_groups.items():
                self.log_message(f"State {state}: {len(zips)} ZIP codes")
            
            # Generate PotAdvisor URLs
            urls = self.zip_mapper.states_to_urls(set(state_groups.keys()))
            
            for state, url in urls.items():
                self.log_message(f"Generated URL for {state}: {url}")
            
            # Here we would normally initiate the actual crawling
            # For now, we'll just simulate it with a log message
            self.log_message("\nInitiating data collection...")
            self.set_status("Data collection in progress...")
            
            # This is a placeholder for the actual crawler implementation
            self.simulate_crawling(urls, state_groups)
            
        except Exception as e:
            error_msg = f"Error processing ZIP codes: {str(e)}"
            self.log_message(error_msg)
            self.set_status("Error: See log for details")
            logger.exception("Failed to process ZIP codes")
            messagebox.showerror("Processing Error", error_msg)
    
    async def run_crawler(self, state_mapping: Dict[str, Tuple[str, str]], filter_zips_by_state: Dict[str, List[str]]) -> None:
        """
        Run the PotAdvisor crawler with the provided state and ZIP information.
        
        Args:
            state_mapping: Dictionary mapping state abbreviations to (url, state_name) tuples
            filter_zips_by_state: Dictionary mapping state abbreviations to lists of ZIP codes
        """
        from src.scrapers.crawl4ai_integration.potadvisor_crawler import PotAdvisorCrawler
        
        try:
            self.log_message("\nInitiating data collection process:")
            
            for state, (url, state_name) in state_mapping.items():
                zips = filter_zips_by_state.get(state, [])
                self.log_message(f"- Will crawl {url} for state {state} ({state_name})")
                self.log_message(f"  Filtering results for {len(zips)} ZIP codes")
            
            # Create output directory
            output_dir = Path("output") / "normalized"
            os.makedirs(output_dir, exist_ok=True)
            
            # Initialize crawler
            crawler = PotAdvisorCrawler(output_dir=str(output_dir))
            
            # Start the crawling process
            self.set_status("Crawling in progress...")
            output_files = await crawler.crawl_and_save(state_mapping, filter_zips_by_state)
            
            # Log results
            self.log_message("\nData collection complete. Results saved to:")
            for state, file_path in output_files.items():
                self.log_message(f"- {state}: {file_path}")
            
            self.set_status("Ready")
            self.log_message("\nAll tasks completed successfully.")
            
        except Exception as e:
            error_msg = f"Error running crawler: {str(e)}"
            self.log_message(error_msg)
            self.set_status("Error: See log for details")
            logger.exception("Failed to run crawler")
            
    def simulate_crawling(self, urls: Dict[str, Tuple[str, str]], state_groups: Dict[str, List[str]]) -> None:
        """
        Initiate the crawling process or simulate it if not yet implemented.
        
        Args:
            urls: Dictionary mapping state abbreviations to (url, state_name) tuples
            state_groups: Dictionary mapping state abbreviations to lists of ZIP codes
        """
        try:
            # Import crawler to check if it exists
            from src.scrapers.crawl4ai_integration.potadvisor_crawler import PotAdvisorCrawler
            
            # Run the async crawler in a non-blocking way
            import asyncio
            from threading import Thread
            
            def run_async_crawler():
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                loop.run_until_complete(self.run_crawler(urls, state_groups))
                loop.close()
            
            # Start crawler in a separate thread
            Thread(target=run_async_crawler, daemon=True).start()
            
        except ImportError:
            # Fall back to simulation if crawler not implemented
            self.log_message("\nCrawler module not found. Simulating the crawling process:")
            
            for state, (url, state_name) in urls.items():
                self.log_message(f"- Would crawl {url} for state {state} ({state_name})")
                self.log_message(f"  Filtering results for ZIP codes: {', '.join(state_groups[state])}")
                
                # Create a placeholder output directory
                output_dir = Path("output") / "normalized"
                os.makedirs(output_dir, exist_ok=True)
                
                output_file = output_dir / f"{state_name.lower()}_dispensaries.json"
                self.log_message(f"  Results would be saved to: {output_file}")
            
            self.log_message("\nSimulation complete. Please implement the crawler module.")
            self.set_status("Ready")

def main():
    """Main entry point for the application."""
    try:
        # Create logs directory
        os.makedirs("logs", exist_ok=True)
        
        # Set up the main window
        root = tk.Tk()
        app = ZipCodeInputApp(root)
        
        # Start the application
        root.mainloop()
    except Exception as e:
        logger.critical(f"Application failed to start: {str(e)}", exc_info=True)
        messagebox.showerror("Fatal Error", f"Application failed to start: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()