#!/usr/bin/env python3
"""
SuperInstance.AI Investor Pitch Deck Generator
Creates a world-class 12-slide pitch deck following Sequoia/YC patterns
"""

from reportlab.lib.pagesizes import letter, landscape
from reportlab.lib.units import inch
from reportlab.lib.colors import HexColor, white, black
from reportlab.pdfgen import canvas
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import Paragraph
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
import os

# Page dimensions
PAGE_WIDTH, PAGE_HEIGHT = landscape(letter)

# Color scheme - Professional tech startup colors
PRIMARY_DARK = HexColor('#1a1a2e')      # Deep navy
PRIMARY_BLUE = HexColor('#16213e')       # Dark blue
ACCENT_BLUE = HexColor('#0f3460')        # Medium blue
HIGHLIGHT = HexColor('#e94560')          # Vibrant coral/red
ACCENT_GOLD = HexColor('#f5a623')        # Gold for key metrics
LIGHT_GRAY = HexColor('#f8f9fa')         # Light background
DARK_GRAY = HexColor('#6c757d')          # Secondary text
WHITE = white
BLACK = black

class PitchDeckGenerator:
    def __init__(self, filename):
        self.filename = filename
        self.c = canvas.Canvas(filename, pagesize=landscape(letter))
        self.slide_num = 0
        
    def draw_background(self, color=PRIMARY_DARK):
        """Draw a full-page background"""
        self.c.setFillColor(color)
        self.c.rect(0, 0, PAGE_WIDTH, PAGE_HEIGHT, fill=1, stroke=0)
        
    def draw_gradient_background(self):
        """Draw a gradient-style background"""
        # Main dark background
        self.c.setFillColor(PRIMARY_DARK)
        self.c.rect(0, 0, PAGE_WIDTH, PAGE_HEIGHT, fill=1, stroke=0)
        
        # Add subtle accent shape
        self.c.setFillColor(PRIMARY_BLUE)
        self.c.rect(0, 0, PAGE_WIDTH * 0.3, PAGE_HEIGHT, fill=1, stroke=0)
        
    def draw_header_accent(self):
        """Draw a subtle header accent line"""
        self.c.setStrokeColor(HIGHLIGHT)
        self.c.setLineWidth(3)
        self.c.line(0.75*inch, PAGE_HEIGHT - 1.2*inch, PAGE_WIDTH - 0.75*inch, PAGE_HEIGHT - 1.2*inch)
        
    def draw_slide_number(self):
        """Draw slide number in corner"""
        self.c.setFillColor(DARK_GRAY)
        self.c.setFont("Helvetica", 10)
        self.c.drawRightString(PAGE_WIDTH - 0.75*inch, 0.5*inch, f"{self.slide_num} / 12")
        
    def draw_footer(self, text="SuperInstance.AI | Investor Pitch Deck"):
        """Draw footer text"""
        self.c.setFillColor(DARK_GRAY)
        self.c.setFont("Helvetica", 9)
        self.c.drawString(0.75*inch, 0.5*inch, text)
        
    def draw_title(self, title, subtitle=None, y_position=None):
        """Draw slide title"""
        if y_position is None:
            y_position = PAGE_HEIGHT - 0.9*inch
            
        self.c.setFillColor(WHITE)
        self.c.setFont("Helvetica-Bold", 36)
        self.c.drawString(0.75*inch, y_position, title)
        
        if subtitle:
            self.c.setFillColor(DARK_GRAY)
            self.c.setFont("Helvetica", 14)
            self.c.drawString(0.75*inch, y_position - 0.35*inch, subtitle)
            
    def draw_big_number(self, number, label, x, y, number_color=HIGHLIGHT):
        """Draw a big metric number with label"""
        self.c.setFillColor(number_color)
        self.c.setFont("Helvetica-Bold", 48)
        self.c.drawString(x, y, number)
        
        self.c.setFillColor(WHITE)
        self.c.setFont("Helvetica", 14)
        self.c.drawString(x, y - 0.35*inch, label)
        
    def draw_metric_box(self, number, label, x, y, width=2*inch, height=1.5*inch):
        """Draw a metric in a styled box"""
        # Box background
        self.c.setFillColor(ACCENT_BLUE)
        self.c.roundRect(x, y, width, height, 10, fill=1, stroke=0)
        
        # Number
        self.c.setFillColor(HIGHLIGHT)
        self.c.setFont("Helvetica-Bold", 32)
        text_width = self.c.stringWidth(number, "Helvetica-Bold", 32)
        self.c.drawString(x + (width - text_width)/2, y + height - 0.6*inch, number)
        
        # Label
        self.c.setFillColor(WHITE)
        self.c.setFont("Helvetica", 11)
        text_width = self.c.stringWidth(label, "Helvetica", 11)
        self.c.drawString(x + (width - text_width)/2, y + 0.25*inch, label)
        
    def draw_bullet_point(self, text, x, y, bullet_color=HIGHLIGHT):
        """Draw a bullet point with text"""
        # Bullet
        self.c.setFillColor(bullet_color)
        self.c.circle(x, y + 0.05*inch, 4, fill=1, stroke=0)
        
        # Text
        self.c.setFillColor(WHITE)
        self.c.setFont("Helvetica", 16)
        self.c.drawString(x + 0.25*inch, y, text)
        
    def draw_table(self, headers, data, x, y, col_widths, row_height=0.45*inch):
        """Draw a styled table"""
        # Header row
        self.c.setFillColor(ACCENT_BLUE)
        total_width = sum(col_widths)
        self.c.rect(x, y - row_height, total_width, row_height, fill=1, stroke=0)
        
        self.c.setFillColor(WHITE)
        self.c.setFont("Helvetica-Bold", 12)
        current_x = x
        for i, header in enumerate(headers):
            self.c.drawString(current_x + 0.1*inch, y - row_height + 0.15*inch, header)
            current_x += col_widths[i]
            
        # Data rows
        for row_idx, row in enumerate(data):
            row_y = y - (row_idx + 2) * row_height
            
            # Alternating background
            if row_idx % 2 == 0:
                self.c.setFillColor(PRIMARY_BLUE)
            else:
                self.c.setFillColor(PRIMARY_DARK)
            self.c.rect(x, row_y, total_width, row_height, fill=1, stroke=0)
            
            # Row data
            current_x = x
            self.c.setFillColor(WHITE)
            self.c.setFont("Helvetica", 11)
            for i, cell in enumerate(row):
                # Highlight first column
                if i == 0:
                    self.c.setFont("Helvetica-Bold", 11)
                    self.c.setFillColor(HIGHLIGHT)
                else:
                    self.c.setFont("Helvetica", 11)
                    self.c.setFillColor(WHITE)
                self.c.drawString(current_x + 0.1*inch, row_y + 0.15*inch, str(cell))
                current_x += col_widths[i]
                
    def new_slide(self):
        """Start a new slide"""
        if self.slide_num > 0:
            self.c.showPage()
        self.slide_num += 1
        
    def create_slide_1_title(self):
        """Slide 1: Title Slide"""
        self.new_slide()
        self.draw_background(PRIMARY_DARK)
        
        # Add accent bar on left
        self.c.setFillColor(HIGHLIGHT)
        self.c.rect(0, 0, 0.15*inch, PAGE_HEIGHT, fill=1, stroke=0)
        
        # Company name - huge
        self.c.setFillColor(WHITE)
        self.c.setFont("Helvetica-Bold", 72)
        self.c.drawString(1*inch, PAGE_HEIGHT - 2.5*inch, "SUPERINSTANCE.AI")
        
        # Tagline
        self.c.setFillColor(HIGHLIGHT)
        self.c.setFont("Helvetica-Bold", 28)
        self.c.drawString(1*inch, PAGE_HEIGHT - 3.3*inch, '"AI Inference in Your Pocket for $35"')
        
        # Divider line
        self.c.setStrokeColor(ACCENT_BLUE)
        self.c.setLineWidth(2)
        self.c.line(1*inch, PAGE_HEIGHT - 3.7*inch, PAGE_WIDTH - 1*inch, PAGE_HEIGHT - 3.7*inch)
        
        # Contact info
        self.c.setFillColor(WHITE)
        self.c.setFont("Helvetica", 18)
        self.c.drawString(1*inch, PAGE_HEIGHT - 4.3*inch, "Contact: david@superinstance.ai")
        
        # Bottom accent
        self.c.setFillColor(ACCENT_BLUE)
        self.c.rect(0, 0, PAGE_WIDTH, 0.8*inch, fill=1, stroke=0)
        
        self.c.setFillColor(WHITE)
        self.c.setFont("Helvetica", 12)
        self.c.drawCentredString(PAGE_WIDTH/2, 0.35*inch, "Investor Pitch Deck | Confidential")
        
        self.draw_slide_number()
        
    def create_slide_2_problem(self):
        """Slide 2: The Problem"""
        self.new_slide()
        self.draw_background(PRIMARY_DARK)
        self.draw_header_accent()
        
        self.draw_title("THE PROBLEM", "Why Edge AI deployments keep failing")
        
        # Big stat
        self.c.setFillColor(HIGHLIGHT)
        self.c.setFont("Helvetica-Bold", 56)
        self.c.drawString(0.75*inch, PAGE_HEIGHT - 2.5*inch, "73%")
        
        self.c.setFillColor(WHITE)
        self.c.setFont("Helvetica-Bold", 24)
        self.c.drawString(0.75*inch, PAGE_HEIGHT - 3.1*inch, "of Edge AI Projects Fail at Prototype")
        
        # Problem bullets
        y_start = PAGE_HEIGHT - 4.2*inch
        problems = [
            ("$127,000", "Average cost of failed deployment"),
            ("340 hours", "Wasted on SDK integration per project"),
            ("Weeks", "Lost to drivers, not AI development"),
        ]
        
        x_positions = [0.75*inch, 3.5*inch, 6.25*inch]
        for i, (num, desc) in enumerate(problems):
            self.c.setFillColor(HIGHLIGHT)
            self.c.setFont("Helvetica-Bold", 32)
            self.c.drawString(x_positions[i], y_start, num)
            
            self.c.setFillColor(WHITE)
            self.c.setFont("Helvetica", 13)
            self.c.drawString(x_positions[i], y_start - 0.4*inch, desc)
            
        # Bottom insight
        self.c.setFillColor(ACCENT_BLUE)
        self.c.roundRect(0.75*inch, 1.2*inch, PAGE_WIDTH - 1.5*inch, 1*inch, 8, fill=1, stroke=0)
        
        self.c.setFillColor(WHITE)
        self.c.setFont("Helvetica-Bold", 14)
        self.c.drawString(1*inch, 1.85*inch, "The Gap:")
        self.c.setFont("Helvetica", 14)
        self.c.drawString(1.9*inch, 1.85*inch, "Developers want to build AI, not fight with hardware drivers")
        
        self.draw_footer()
        self.draw_slide_number()
        
    def create_slide_3_solution(self):
        """Slide 3: The Solution"""
        self.new_slide()
        self.draw_background(PRIMARY_DARK)
        self.draw_header_accent()
        
        self.draw_title("THE SOLUTION", "Plug-and-Play AI Inference")
        
        # Product name
        self.c.setFillColor(HIGHLIGHT)
        self.c.setFont("Helvetica-Bold", 42)
        self.c.drawString(0.75*inch, PAGE_HEIGHT - 2.3*inch, "SuperInstance")
        
        # Key metrics in boxes
        metrics = [
            ("$35", "Base Unit Price", HIGHLIGHT),
            ("$19", "Model Cartridges", ACCENT_GOLD),
            ("30 sec", "To First Inference", HIGHLIGHT),
            ("80-150 tok/s", "3B Model @ 3W", ACCENT_GOLD),
        ]
        
        box_width = 1.7*inch
        box_height = 1.3*inch
        x_start = 0.75*inch
        y_pos = PAGE_HEIGHT - 4.5*inch
        spacing = 0.15*inch
        
        for i, (num, label, color) in enumerate(metrics):
            x = x_start + i * (box_width + spacing)
            
            # Box
            self.c.setFillColor(ACCENT_BLUE)
            self.c.roundRect(x, y_pos, box_width, box_height, 8, fill=1, stroke=0)
            
            # Number
            self.c.setFillColor(color)
            self.c.setFont("Helvetica-Bold", 28)
            text_w = self.c.stringWidth(num, "Helvetica-Bold", 28)
            self.c.drawString(x + (box_width - text_w)/2, y_pos + box_height - 0.5*inch, num)
            
            # Label
            self.c.setFillColor(WHITE)
            self.c.setFont("Helvetica", 11)
            text_w = self.c.stringWidth(label, "Helvetica", 11)
            self.c.drawString(x + (box_width - text_w)/2, y_pos + 0.2*inch, label)
            
        # Value proposition
        self.c.setFillColor(WHITE)
        self.c.setFont("Helvetica-Bold", 18)
        self.c.drawString(0.75*inch, 2.3*inch, "Zero Software Setup  •  Instant AI Inference  •  Developer-First")
        
        self.draw_footer()
        self.draw_slide_number()
        
    def create_slide_4_how_it_works(self):
        """Slide 4: How It Works"""
        self.new_slide()
        self.draw_background(PRIMARY_DARK)
        self.draw_header_accent()
        
        self.draw_title("HOW IT WORKS", "Mask-Locked Architecture")
        
        # Architecture diagram concept
        # Left side - Traditional approach
        self.c.setFillColor(ACCENT_BLUE)
        self.c.roundRect(0.75*inch, PAGE_HEIGHT - 5*inch, 3.5*inch, 2.8*inch, 10, fill=1, stroke=0)
        
        self.c.setFillColor(WHITE)
        self.c.setFont("Helvetica-Bold", 14)
        self.c.drawString(1*inch, PAGE_HEIGHT - 2.5*inch, "Traditional Approach")
        
        self.c.setFont("Helvetica", 11)
        self.c.setFillColor(DARK_GRAY)
        self.c.drawString(1*inch, PAGE_HEIGHT - 3.1*inch, "• External DRAM required")
        self.c.drawString(1*inch, PAGE_HEIGHT - 3.5*inch, "• Memory bandwidth bottleneck")
        self.c.drawString(1*inch, PAGE_HEIGHT - 3.9*inch, "• High power consumption")
        self.c.drawString(1*inch, PAGE_HEIGHT - 4.3*inch, "• Complex SDK setup")
        
        # Arrow
        self.c.setStrokeColor(HIGHLIGHT)
        self.c.setLineWidth(3)
        self.c.line(4.5*inch, PAGE_HEIGHT - 3.6*inch, 5.2*inch, PAGE_HEIGHT - 3.6*inch)
        
        # Right side - Our approach
        self.c.setFillColor(HIGHLIGHT)
        self.c.roundRect(5.5*inch, PAGE_HEIGHT - 5*inch, 3.5*inch, 2.8*inch, 10, fill=1, stroke=0)
        
        self.c.setFillColor(WHITE)
        self.c.setFont("Helvetica-Bold", 14)
        self.c.drawString(5.8*inch, PAGE_HEIGHT - 2.5*inch, "SuperInstance")
        
        self.c.setFont("Helvetica", 11)
        self.c.drawString(5.8*inch, PAGE_HEIGHT - 3.1*inch, "• Weights in silicon metal layers")
        self.c.drawString(5.8*inch, PAGE_HEIGHT - 3.5*inch, "• Zero memory bandwidth")
        self.c.drawString(5.8*inch, PAGE_HEIGHT - 3.9*inch, "• 95% energy reduction")
        self.c.drawString(5.8*inch, PAGE_HEIGHT - 4.3*inch, "• Instant deployment")
        
        # Key stat
        self.c.setFillColor(ACCENT_GOLD)
        self.c.setFont("Helvetica-Bold", 48)
        self.c.drawString(0.75*inch, 1.5*inch, "95%")
        
        self.c.setFillColor(WHITE)
        self.c.setFont("Helvetica-Bold", 18)
        self.c.drawString(0.75*inch, 1*inch, "Reduction in Inference Energy")
        
        self.draw_footer()
        self.draw_slide_number()
        
    def create_slide_5_market(self):
        """Slide 5: Market Opportunity"""
        self.new_slide()
        self.draw_background(PRIMARY_DARK)
        self.draw_header_accent()
        
        self.draw_title("MARKET OPPORTUNITY", "$76.8B Edge AI Chip Market by 2029")
        
        # Market sizing visualization
        # TAM
        self.c.setFillColor(ACCENT_BLUE)
        self.c.roundRect(0.75*inch, PAGE_HEIGHT - 4.8*inch, 2.2*inch, 2.4*inch, 8, fill=1, stroke=0)
        
        self.c.setFillColor(HIGHLIGHT)
        self.c.setFont("Helvetica-Bold", 28)
        self.c.drawString(1*inch, PAGE_HEIGHT - 3*inch, "$76.8B")
        
        self.c.setFillColor(WHITE)
        self.c.setFont("Helvetica-Bold", 12)
        self.c.drawString(1*inch, PAGE_HEIGHT - 3.5*inch, "TAM")
        self.c.setFont("Helvetica", 10)
        self.c.drawString(1*inch, PAGE_HEIGHT - 3.8*inch, "Total Edge AI Chips")
        
        # SAM
        self.c.setFillColor(PRIMARY_BLUE)
        self.c.roundRect(3.2*inch, PAGE_HEIGHT - 4.8*inch, 2.2*inch, 2.4*inch, 8, fill=1, stroke=0)
        
        self.c.setFillColor(ACCENT_GOLD)
        self.c.setFont("Helvetica-Bold", 28)
        self.c.drawString(3.5*inch, PAGE_HEIGHT - 3*inch, "$18.5B")
        
        self.c.setFillColor(WHITE)
        self.c.setFont("Helvetica-Bold", 12)
        self.c.drawString(3.5*inch, PAGE_HEIGHT - 3.5*inch, "SAM")
        self.c.setFont("Helvetica", 10)
        self.c.drawString(3.5*inch, PAGE_HEIGHT - 3.8*inch, "LLM-capable, <10W")
        
        # SOM
        self.c.setFillColor(ACCENT_BLUE)
        self.c.roundRect(5.65*inch, PAGE_HEIGHT - 4.8*inch, 2.2*inch, 2.4*inch, 8, fill=1, stroke=0)
        
        self.c.setFillColor(HIGHLIGHT)
        self.c.setFont("Helvetica-Bold", 28)
        self.c.drawString(6*inch, PAGE_HEIGHT - 3*inch, "$1.85B")
        
        self.c.setFillColor(WHITE)
        self.c.setFont("Helvetica-Bold", 12)
        self.c.drawString(6*inch, PAGE_HEIGHT - 3.5*inch, "SOM")
        self.c.setFont("Helvetica", 10)
        self.c.drawString(6*inch, PAGE_HEIGHT - 3.8*inch, "Fixed-model Segment")
        
        # Target
        self.c.setFillColor(ACCENT_GOLD)
        self.c.setFont("Helvetica-Bold", 24)
        self.c.drawString(0.75*inch, 1.8*inch, "Target: 1.3% Market Share by Year 5 = $24M Revenue")
        
        self.draw_footer()
        self.draw_slide_number()
        
    def create_slide_6_product_line(self):
        """Slide 6: Product Line"""
        self.new_slide()
        self.draw_background(PRIMARY_DARK)
        self.draw_header_accent()
        
        self.draw_title("PRODUCT LINE", "Four tiers for every use case")
        
        # Product table
        headers = ["Product", "Model", "Price", "Speed", "Power"]
        data = [
            ["Nano", "1B", "$35", "100 tok/s", "<1W"],
            ["Micro", "3B", "$49", "80-150 tok/s", "3W"],
            ["Standard", "7B", "$79", "50-80 tok/s", "5W"],
            ["Pro", "13B", "$149", "30-50 tok/s", "10W"],
        ]
        
        col_widths = [1.5*inch, 1.2*inch, 1.2*inch, 1.5*inch, 1.2*inch]
        self.draw_table(headers, data, 0.75*inch, PAGE_HEIGHT - 2.5*inch, col_widths)
        
        # Highlight Micro as hero product
        self.c.setFillColor(HIGHLIGHT)
        self.c.setFont("Helvetica-Bold", 14)
        self.c.drawString(0.75*inch, 2.5*inch, "★ Micro (3B): Our flagship product")
        
        self.c.setFillColor(WHITE)
        self.c.setFont("Helvetica", 13)
        self.c.drawString(0.75*inch, 2*inch, "Best price/performance ratio in the industry")
        
        self.draw_footer()
        self.draw_slide_number()
        
    def create_slide_7_competitive(self):
        """Slide 7: Competitive Positioning"""
        self.new_slide()
        self.draw_background(PRIMARY_DARK)
        self.draw_header_accent()
        
        self.draw_title("COMPETITIVE POSITIONING", "We're the only sub-$50 LLM inference chip")
        
        # Competitive comparison
        y_start = PAGE_HEIGHT - 2.5*inch
        
        # Headers
        self.c.setFillColor(DARK_GRAY)
        self.c.setFont("Helvetica-Bold", 11)
        self.c.drawString(0.75*inch, y_start, "Product")
        self.c.drawString(3*inch, y_start, "Price")
        self.c.drawString(4.5*inch, y_start, "Speed")
        self.c.drawString(6.5*inch, y_start, "Power")
        
        # Divider
        self.c.setStrokeColor(ACCENT_BLUE)
        self.c.setLineWidth(1)
        self.c.line(0.75*inch, y_start - 0.15*inch, 8*inch, y_start - 0.15*inch)
        
        # Competitors
        competitors = [
            ("Jetson Orin Nano", "$249", "45 tok/s", "15W", DARK_GRAY),
            ("Hailo-10H", "$88", "12 tok/s", "5W", DARK_GRAY),
        ]
        
        y_pos = y_start - 0.6*inch
        self.c.setFont("Helvetica", 13)
        for name, price, speed, power, color in competitors:
            self.c.setFillColor(color)
            self.c.drawString(0.75*inch, y_pos, name)
            self.c.drawString(3*inch, y_pos, price)
            self.c.drawString(4.5*inch, y_pos, speed)
            self.c.drawString(6.5*inch, y_pos, power)
            y_pos -= 0.5*inch
            
        # Highlight box for SuperInstance
        self.c.setFillColor(HIGHLIGHT)
        self.c.roundRect(0.6*inch, y_pos - 0.15*inch, 7.6*inch, 0.5*inch, 5, fill=1, stroke=0)
        
        self.c.setFillColor(WHITE)
        self.c.setFont("Helvetica-Bold", 13)
        self.c.drawString(0.75*inch, y_pos, "SuperInstance")
        self.c.setFont("Helvetica", 13)
        self.c.drawString(3*inch, y_pos, "$35")
        self.c.drawString(4.5*inch, y_pos, "80-150 tok/s")
        self.c.drawString(6.5*inch, y_pos, "3W")
        
        # Win summary
        self.c.setFillColor(ACCENT_GOLD)
        self.c.setFont("Helvetica-Bold", 20)
        self.c.drawString(0.75*inch, 1.8*inch, "3x faster • 7x cheaper • 5x more efficient")
        
        self.draw_footer()
        self.draw_slide_number()
        
    def create_slide_8_business_model(self):
        """Slide 8: Business Model"""
        self.new_slide()
        self.draw_background(PRIMARY_DARK)
        self.draw_header_accent()
        
        self.draw_title("BUSINESS MODEL", "Multiple revenue streams")
        
        # Revenue breakdown - visual bars
        y_start = PAGE_HEIGHT - 3*inch
        revenue_streams = [
            ("Hardware", "55%", "Base units at 60-75% margin", 5.5),
            ("Subscriptions", "28%", "Discovery/Premium/Enterprise tiers", 2.8),
            ("Cartridges", "12%", "80-85% margin model cartridges", 1.2),
            ("Platform", "5%", "Custom model development", 0.5),
        ]
        
        bar_max_width = 5*inch
        
        for i, (name, pct, desc, bar_val) in enumerate(revenue_streams):
            y = y_start - i * 0.85*inch
            
            # Bar background
            self.c.setFillColor(ACCENT_BLUE)
            self.c.roundRect(3*inch, y - 0.2*inch, bar_max_width, 0.4*inch, 4, fill=1, stroke=0)
            
            # Bar fill
            self.c.setFillColor(HIGHLIGHT)
            bar_width = (bar_val / 5.5) * bar_max_width
            self.c.roundRect(3*inch, y - 0.2*inch, bar_width, 0.4*inch, 4, fill=1, stroke=0)
            
            # Labels
            self.c.setFillColor(WHITE)
            self.c.setFont("Helvetica-Bold", 14)
            self.c.drawString(0.75*inch, y, name)
            
            self.c.setFillColor(HIGHLIGHT)
            self.c.setFont("Helvetica-Bold", 16)
            self.c.drawString(1.8*inch, y, pct)
            
            self.c.setFillColor(DARK_GRAY)
            self.c.setFont("Helvetica", 11)
            self.c.drawString(3.1*inch, y, desc)
            
        self.draw_footer()
        self.draw_slide_number()
        
    def create_slide_9_traction(self):
        """Slide 9: Traction"""
        self.new_slide()
        self.draw_background(PRIMARY_DARK)
        self.draw_header_accent()
        
        self.draw_title("TRACTION", "Building momentum")
        
        # Traction metrics
        metrics = [
            ("94 tok/s", "FPGA prototype demonstrated", HIGHLIGHT),
            ("847", "Developers on waitlist", ACCENT_GOLD),
            ("$62K", "LOI pipeline committed", HIGHLIGHT),
            ("Patent Filed", "Mask-locked architecture", ACCENT_GOLD),
        ]
        
        x_positions = [0.75*inch, 3.25*inch, 5.75*inch, 8.25*inch]
        
        for i, (num, label, color) in enumerate(metrics):
            x = x_positions[i]
            
            # Number
            self.c.setFillColor(color)
            self.c.setFont("Helvetica-Bold", 36)
            self.c.drawString(x, PAGE_HEIGHT - 3*inch, num)
            
            # Label
            self.c.setFillColor(WHITE)
            self.c.setFont("Helvetica", 12)
            # Split label if needed
            words = label.split()
            if len(words) > 2:
                self.c.drawString(x, PAGE_HEIGHT - 3.5*inch, ' '.join(words[:2]))
                self.c.drawString(x, PAGE_HEIGHT - 3.75*inch, ' '.join(words[2:]))
            else:
                self.c.drawString(x, PAGE_HEIGHT - 3.5*inch, label)
                
        # Progress bar
        self.c.setFillColor(ACCENT_BLUE)
        self.c.roundRect(0.75*inch, 1.5*inch, PAGE_WIDTH - 1.5*inch, 0.8*inch, 8, fill=1, stroke=0)
        
        self.c.setFillColor(WHITE)
        self.c.setFont("Helvetica-Bold", 14)
        self.c.drawString(1*inch, 1.85*inch, "Current Status: ")
        self.c.setFont("Helvetica", 14)
        self.c.drawString(2.4*inch, 1.85*inch, "FPGA prototype validated • Pre-silicon • Actively fundraising")
        
        self.draw_footer()
        self.draw_slide_number()
        
    def create_slide_10_team(self):
        """Slide 10: Team"""
        self.new_slide()
        self.draw_background(PRIMARY_DARK)
        self.draw_header_accent()
        
        self.draw_title("TEAM", "Deep hardware & AI expertise")
        
        # Team members
        team = [
            ("David Park", "CEO", "Apple A12 Neural Engine • EdgeNeural exit"),
            ("Dr. Sarah Chen", "CTO", "NVIDIA Jetson TX2 • Stanford PhD"),
            ("Marcus Johnson", "VP Engineering", "TSMC • 50+ tape-outs"),
        ]
        
        y_start = PAGE_HEIGHT - 2.8*inch
        
        for i, (name, title, creds) in enumerate(team):
            y = y_start - i * 1*inch
            
            # Name
            self.c.setFillColor(WHITE)
            self.c.setFont("Helvetica-Bold", 18)
            self.c.drawString(0.75*inch, y, name)
            
            # Title
            self.c.setFillColor(HIGHLIGHT)
            self.c.setFont("Helvetica-Bold", 12)
            self.c.drawString(2.8*inch, y, title)
            
            # Credentials
            self.c.setFillColor(DARK_GRAY)
            self.c.setFont("Helvetica", 12)
            self.c.drawString(0.75*inch, y - 0.35*inch, creds)
            
        # Advisors
        self.c.setFillColor(ACCENT_GOLD)
        self.c.setFont("Helvetica-Bold", 14)
        self.c.drawString(0.75*inch, 2*inch, "Advisors:")
        
        self.c.setFillColor(WHITE)
        self.c.setFont("Helvetica", 13)
        self.c.drawString(1.8*inch, 2*inch, "Stanford EE Professor • Former NVIDIA VP • YC Partner")
        
        self.draw_footer()
        self.draw_slide_number()
        
    def create_slide_11_financials(self):
        """Slide 11: Financial Projections"""
        self.new_slide()
        self.draw_background(PRIMARY_DARK)
        self.draw_header_accent()
        
        self.draw_title("FINANCIAL PROJECTIONS", "Path to $70M ARR")
        
        # Financial table
        headers = ["Year", "Revenue", "Growth", "Burn"]
        data = [
            ["Y1", "$240K", "-", "$150K/mo"],
            ["Y2", "$2.9M", "12x", "$250K/mo"],
            ["Y3", "$11.2M", "3.9x", "Profitable"],
            ["Y4", "$28.9M", "2.6x", "-"],
            ["Y5", "$70M", "2.4x", "-"],
        ]
        
        col_widths = [1*inch, 1.5*inch, 1.2*inch, 1.5*inch]
        self.draw_table(headers, data, 0.75*inch, PAGE_HEIGHT - 2.5*inch, col_widths)
        
        # Key milestone
        self.c.setFillColor(ACCENT_GOLD)
        self.c.setFont("Helvetica-Bold", 16)
        self.c.drawString(0.75*inch, 2*inch, "Y3: Profitable  •  Y5: $70M ARR")
        
        self.draw_footer()
        self.draw_slide_number()
        
    def create_slide_12_ask(self):
        """Slide 12: The Ask"""
        self.new_slide()
        self.draw_background(PRIMARY_DARK)
        
        # Accent bar
        self.c.setFillColor(HIGHLIGHT)
        self.c.rect(0, 0, 0.15*inch, PAGE_HEIGHT, fill=1, stroke=0)
        
        self.draw_title("THE ASK")
        
        # Main ask
        self.c.setFillColor(HIGHLIGHT)
        self.c.setFont("Helvetica-Bold", 48)
        self.c.drawString(0.75*inch, PAGE_HEIGHT - 2.3*inch, "$500K SAFE")
        
        self.c.setFillColor(WHITE)
        self.c.setFont("Helvetica", 18)
        self.c.drawString(0.75*inch, PAGE_HEIGHT - 2.85*inch, "MFN Clause • $4M Cap")
        
        # Use of funds
        self.c.setFillColor(ACCENT_GOLD)
        self.c.setFont("Helvetica-Bold", 16)
        self.c.drawString(0.75*inch, PAGE_HEIGHT - 3.7*inch, "Use of Funds:")
        
        funds = [
            ("Engineering (2 FTE)", "$280K", "Gate 0 prototype"),
            ("FPGA Prototyping", "$75K", "25+ tok/s demo"),
            ("Silicon IP License", "$60K", "Architecture rights"),
            ("Legal/Patents", "$35K", "IP protection"),
            ("GTM", "$30K", "5 LOIs"),
            ("Buffer", "$20K", ""),
        ]
        
        y_start = PAGE_HEIGHT - 4.3*inch
        for i, (item, amount, note) in enumerate(funds):
            y = y_start - i * 0.35*inch
            
            self.c.setFillColor(WHITE)
            self.c.setFont("Helvetica", 12)
            self.c.drawString(1*inch, y, item)
            
            self.c.setFillColor(HIGHLIGHT)
            self.c.setFont("Helvetica-Bold", 12)
            self.c.drawString(3.5*inch, y, amount)
            
            if note:
                self.c.setFillColor(DARK_GRAY)
                self.c.setFont("Helvetica", 10)
                self.c.drawString(4.5*inch, y, note)
                
        # Runway and trigger
        self.c.setFillColor(ACCENT_BLUE)
        self.c.roundRect(6.5*inch, PAGE_HEIGHT - 4*inch, 2.5*inch, 1.5*inch, 8, fill=1, stroke=0)
        
        self.c.setFillColor(WHITE)
        self.c.setFont("Helvetica-Bold", 14)
        self.c.drawString(6.7*inch, PAGE_HEIGHT - 2.8*inch, "18-month")
        self.c.setFont("Helvetica", 12)
        self.c.drawString(6.7*inch, PAGE_HEIGHT - 3.1*inch, "runway")
        
        self.c.setFillColor(ACCENT_GOLD)
        self.c.setFont("Helvetica-Bold", 11)
        self.c.drawString(6.7*inch, PAGE_HEIGHT - 3.5*inch, "Series A Trigger:")
        self.c.setFillColor(WHITE)
        self.c.setFont("Helvetica", 10)
        self.c.drawString(6.7*inch, PAGE_HEIGHT - 3.8*inch, "50 tok/s + $200K LOV")
        
        # Bottom CTA
        self.c.setFillColor(HIGHLIGHT)
        self.c.roundRect(0.75*inch, 0.8*inch, PAGE_WIDTH - 1.5*inch, 0.6*inch, 8, fill=1, stroke=0)
        
        self.c.setFillColor(WHITE)
        self.c.setFont("Helvetica-Bold", 16)
        self.c.drawCentredString(PAGE_WIDTH/2, 1*inch, "Let's build the future of edge AI together")
        
        self.draw_slide_number()
        
    def generate(self):
        """Generate all slides"""
        self.create_slide_1_title()
        self.create_slide_2_problem()
        self.create_slide_3_solution()
        self.create_slide_4_how_it_works()
        self.create_slide_5_market()
        self.create_slide_6_product_line()
        self.create_slide_7_competitive()
        self.create_slide_8_business_model()
        self.create_slide_9_traction()
        self.create_slide_10_team()
        self.create_slide_11_financials()
        self.create_slide_12_ask()
        
        self.c.save()
        print(f"✅ Generated: {self.filename}")
        return self.filename


if __name__ == "__main__":
    output_path = "/home/z/my-project/download/SuperInstance_Investor_Pitch_Deck_10out10.pdf"
    generator = PitchDeckGenerator(output_path)
    generator.generate()
