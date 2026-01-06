#!/usr/bin/env python3
"""
WATSON Process Diagrams Module

Provides Lean Six Sigma project diagram tools:
- SIPOC Diagram (Define Phase)
- Process Map (Define Phase)
- RACI Matrix (Define Phase)
- Swim Lane Diagram (Analyze Phase)
- Value Stream Map (Analyze Phase)
- Fishbone Diagram (Analyze Phase)

Copyright (c) 2025 A Step in the Right Direction LLC
All Rights Reserved.
"""

import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch, Polygon, Circle, Rectangle
from matplotlib.lines import Line2D
import numpy as np
from pathlib import Path
import tempfile


# Brand Colors
BRAND_BURGUNDY = '#6d132a'  # Primary brand color
BRAND_GOLD = '#dcad73'      # Secondary brand color

# Colorblind-Friendly Chart Colors (Modified Wong palette)
BLUE = '#0072B2'        # Primary data
TEAL = '#009E73'        # Control limits, targets
SKY_BLUE = '#56B4E9'    # Fills, confidence bands
PINK = '#CC79A7'        # Additional series
INDIGO = '#332288'      # Extended palette
CYAN = '#88CCEE'        # Extended palette
YELLOW = '#F0E442'      # Highlights (sparingly)
BLACK = '#000000'       # Center lines, fit curves
GRAY = '#999999'        # Zone lines, disabled
LIGHT_GRAY = '#f5f5f5'
WHITE = '#ffffff'

# Legacy aliases
BURGUNDY = BRAND_BURGUNDY
GOLD = BRAND_GOLD
GREEN = TEAL
PURPLE = PINK
ORANGE = BRAND_GOLD
VERMILLION = BRAND_BURGUNDY


class ProcessDiagramEngine:
    """Engine for generating Lean Six Sigma process diagrams."""
    
    def __init__(self):
        self.chart_dir = Path(tempfile.gettempdir()) / 'watson_charts'
        self.chart_dir.mkdir(exist_ok=True)
        
        # SIPOC column colors (light, accessible)
        self.sipoc_colors = {
            'S': '#cce5ff',  # Light blue
            'I': '#fff3cd',  # Light yellow
            'P': '#e8e8e8',  # Light gray
            'O': '#d4edda',  # Light green
            'C': '#e2d5f1'   # Light purple
        }
        
        # Swim lane colors (colorblind-safe light tints)
        self.lane_colors = [
            '#cce5ff',  # Light blue
            '#fff3cd',  # Light yellow/orange
            '#d4edda',  # Light green
            '#e2d5f1',  # Light purple
            '#ffecd2',  # Light peach
            '#d1ecf1',  # Light cyan
        ]
        
        # Fishbone category colors (colorblind-safe)
        self.fishbone_colors = {
            'Policy/Standards': BLUE,
            'Materials': TEAL,
            'Process/Procedures': SKY_BLUE,
            'Physical Environment': PINK,
            'People': INDIGO,
            'IT Systems/Equipment': CYAN
        }
    
    def generate_sipoc(self, suppliers, inputs, process_steps, outputs, customers, requirements=None, title="SIPOC Diagram"):
        """
        Generate a SIPOC diagram with optional CTQ/CTS requirements.
        
        Args:
            suppliers: List of supplier names
            inputs: List of input items
            process_steps: List of 3-5 high-level process steps
            outputs: List of output items
            customers: List of customer names
            requirements: List of CTQ/CTS requirements (displayed with outputs)
            title: Diagram title
            
        Returns:
            Path to the generated image
        """
        fig, ax = plt.subplots(figsize=(14, 8))
        ax.set_xlim(0, 14)
        ax.set_ylim(0, 8)
        ax.axis('off')
        ax.set_facecolor(WHITE)
        
        # Title
        ax.text(7, 7.5, title, ha='center', va='center', fontsize=16, fontweight='bold', color=BURGUNDY)
        
        # Column headers - add Requirements subheader to Outputs
        headers = ['Suppliers', 'Inputs', 'Process', 'Outputs', 'Customers']
        column_positions = [1.4, 4.2, 7, 9.8, 12.6]
        column_widths = 2.4
        
        for i, (header, x_pos) in enumerate(zip(headers, column_positions)):
            key = header[0]
            color = self.sipoc_colors.get(key, LIGHT_GRAY)
            
            # Header box
            header_box = FancyBboxPatch(
                (x_pos - column_widths/2, 6.5), column_widths, 0.7,
                boxstyle="round,pad=0.02,rounding_size=0.1",
                facecolor=BURGUNDY, edgecolor=BURGUNDY
            )
            ax.add_patch(header_box)
            
            # Add CTQ/CTS subheader for Outputs column
            if header == 'Outputs' and requirements:
                ax.text(x_pos, 6.95, header, ha='center', va='center', fontsize=11, fontweight='bold', color=WHITE)
                ax.text(x_pos, 6.7, '(with CTQ/CTS)', ha='center', va='center', fontsize=8, color=WHITE)
            else:
                ax.text(x_pos, 6.85, header, ha='center', va='center', fontsize=11, fontweight='bold', color=WHITE)
            
            # Column background
            col_box = FancyBboxPatch(
                (x_pos - column_widths/2, 0.5), column_widths, 6,
                boxstyle="round,pad=0.02,rounding_size=0.1",
                facecolor=color, edgecolor=GRAY, linewidth=1
            )
            ax.add_patch(col_box)
        
        # Add content to columns
        columns_data = [suppliers, inputs, process_steps, outputs, customers]
        
        for col_idx, (data, x_pos) in enumerate(zip(columns_data, column_positions)):
            if not data:
                continue
            
            # For outputs column, interleave with requirements
            if col_idx == 3 and requirements:  # Outputs column
                combined_items = []
                for i, output in enumerate(data):
                    combined_items.append(('output', output))
                    if i < len(requirements):
                        combined_items.append(('req', requirements[i]))
                # Add any remaining requirements
                for i in range(len(data), len(requirements)):
                    combined_items.append(('req', requirements[i]))
                
                n_items = len(combined_items)
                spacing = min(5.5 / max(n_items, 1), 0.6)
                start_y = 6.0 - (n_items - 1) * spacing / 2
                
                for i, (item_type, item) in enumerate(combined_items):
                    y_pos = start_y - i * spacing
                    if item_type == 'output':
                        ax.text(x_pos - 1.0, y_pos, f"• {item}", ha='left', va='center', fontsize=9, fontweight='bold')
                    else:  # requirement
                        ax.text(x_pos - 0.9, y_pos, f"  → {item}", ha='left', va='center', fontsize=8, color=BURGUNDY)
            else:
                n_items = len(data)
                spacing = min(5.5 / max(n_items, 1), 1.0)
                start_y = 6.0 - (n_items - 1) * spacing / 2
                
                for i, item in enumerate(data):
                    y_pos = start_y - i * spacing
                    
                    if col_idx == 2:  # Process column - numbered steps
                        text = f"{i+1}. {item}"
                        # Draw process box
                        proc_box = FancyBboxPatch(
                            (x_pos - 1.1, y_pos - 0.25), 2.2, 0.5,
                            boxstyle="round,pad=0.02,rounding_size=0.1",
                            facecolor=WHITE, edgecolor=BURGUNDY, linewidth=1.5
                        )
                        ax.add_patch(proc_box)
                        ax.text(x_pos, y_pos, text, ha='center', va='center', fontsize=9, wrap=True)
                        
                        # Arrow to next step
                        if i < n_items - 1:
                            ax.annotate('', xy=(x_pos, y_pos - spacing + 0.25),
                                       xytext=(x_pos, y_pos - 0.25),
                                       arrowprops=dict(arrowstyle='->', color=BURGUNDY, lw=1.5))
                    else:
                        # Regular bullet point
                        ax.text(x_pos - 1.0, y_pos, f"• {item}", ha='left', va='center', fontsize=9)
        
        # Add flow arrows between columns
        arrow_y = 3.5
        for i in range(4):
            x_start = column_positions[i] + column_widths/2 - 0.1
            x_end = column_positions[i+1] - column_widths/2 + 0.1
            ax.annotate('', xy=(x_end, arrow_y), xytext=(x_start, arrow_y),
                       arrowprops=dict(arrowstyle='->', color=GOLD, lw=2))
        
        # Footer
        ax.text(7, 0.2, "SIPOC Diagram - Define Phase", ha='center', va='center', 
                fontsize=9, color=GRAY)
        
        plt.tight_layout()
        
        filepath = self.chart_dir / 'sipoc_diagram.png'
        plt.savefig(filepath, dpi=150, bbox_inches='tight', facecolor=WHITE)
        plt.close()
        
        return filepath
    
    def generate_process_map(self, steps, title="Process Map"):
        """
        Generate a process flowchart.
        
        Args:
            steps: List of step strings. Prefixes:
                   [S] = Start/End oval
                   [D] = Decision diamond
                   No prefix = Process rectangle
            title: Diagram title
            
        Returns:
            Path to the generated image
        """
        fig, ax = plt.subplots(figsize=(12, max(8, len(steps) * 1.2)))
        
        n_steps = len(steps)
        ax.set_xlim(0, 12)
        ax.set_ylim(0, n_steps + 2)
        ax.axis('off')
        ax.set_facecolor(WHITE)
        
        # Title
        ax.text(6, n_steps + 1.5, title, ha='center', va='center', 
                fontsize=16, fontweight='bold', color=BURGUNDY)
        
        x_center = 6
        y_spacing = 1.0
        
        for i, step in enumerate(steps):
            y_pos = n_steps - i
            step_text = step.strip()
            
            if step_text.upper().startswith('[S]'):
                # Start/End oval
                step_text = step_text[3:].strip()
                ellipse = patches.Ellipse((x_center, y_pos), 4, 0.7, 
                                         facecolor='#e8d4d8', edgecolor=BURGUNDY, linewidth=2)
                ax.add_patch(ellipse)
                ax.text(x_center, y_pos, step_text, ha='center', va='center', fontsize=10, fontweight='bold')
                
            elif step_text.upper().startswith('[D]'):
                # Decision diamond
                step_text = step_text[3:].strip()
                diamond = patches.RegularPolygon((x_center, y_pos), numVertices=4, radius=0.6,
                                                orientation=np.pi/4,
                                                facecolor='#f5e6ce', edgecolor=GOLD, linewidth=2)
                ax.add_patch(diamond)
                ax.text(x_center, y_pos, step_text, ha='center', va='center', fontsize=9, wrap=True)
                
                # Yes/No labels
                ax.text(x_center + 1.5, y_pos, "Yes", ha='left', va='center', fontsize=8, color=BURGUNDY)
                ax.text(x_center - 1.5, y_pos, "No", ha='right', va='center', fontsize=8, color=BURGUNDY)
                
            else:
                # Process rectangle
                rect = FancyBboxPatch((x_center - 2, y_pos - 0.35), 4, 0.7,
                                     boxstyle="round,pad=0.02,rounding_size=0.1",
                                     facecolor=WHITE, edgecolor=BURGUNDY, linewidth=2)
                ax.add_patch(rect)
                ax.text(x_center, y_pos, step_text, ha='center', va='center', fontsize=10)
            
            # Arrow to next step
            if i < n_steps - 1:
                next_step = steps[i + 1].strip()
                y_arrow_start = y_pos - 0.4
                y_arrow_end = y_pos - y_spacing + 0.4
                
                if step_text.upper().startswith('[D]') or step.strip().upper().startswith('[D]'):
                    y_arrow_start = y_pos - 0.6
                
                ax.annotate('', xy=(x_center, y_arrow_end), xytext=(x_center, y_arrow_start),
                           arrowprops=dict(arrowstyle='->', color=BURGUNDY, lw=1.5))
        
        # Footer
        ax.text(6, 0.3, "Process Map - Define Phase", ha='center', va='center',
                fontsize=9, color=GRAY)
        
        plt.tight_layout()
        
        filepath = self.chart_dir / 'process_map.png'
        plt.savefig(filepath, dpi=150, bbox_inches='tight', facecolor=WHITE)
        plt.close()
        
        return filepath
    
    def generate_raci(self, tasks, roles, matrix, title="RACI Matrix"):
        """
        Generate a RACI matrix diagram.
        
        Args:
            tasks: List of task names
            roles: List of role names
            matrix: 2D list where matrix[task_idx][role_idx] = 'R', 'A', 'C', 'I', or ''
            title: Diagram title
            
        Returns:
            Path to the generated image
        """
        n_tasks = len(tasks)
        n_roles = len(roles)
        
        fig, ax = plt.subplots(figsize=(max(10, n_roles * 1.5 + 4), max(6, n_tasks * 0.6 + 2)))
        ax.axis('off')
        ax.set_facecolor(WHITE)
        
        # RACI colors
        raci_colors = {
            'R': '#6d132a',  # Burgundy - Responsible
            'A': '#1565c0',  # Blue - Accountable
            'C': '#dcad73',  # Gold - Consulted
            'I': '#b2b2b2',  # Gray - Informed
            '': WHITE
        }
        
        raci_text_colors = {
            'R': WHITE,
            'A': WHITE,
            'C': BLACK,
            'I': BLACK,
            '': BLACK
        }
        
        # Calculate dimensions
        task_col_width = 3.0
        cell_width = 1.2
        cell_height = 0.5
        header_height = 0.6
        
        total_width = task_col_width + n_roles * cell_width
        total_height = header_height + n_tasks * cell_height
        
        # Center the table
        x_offset = (12 - total_width) / 2
        y_offset = 1
        
        # Title
        ax.text(6, total_height + y_offset + 0.5, title, ha='center', va='center',
                fontsize=16, fontweight='bold', color=BURGUNDY)
        
        # Draw header row
        # Task header
        header_rect = FancyBboxPatch((x_offset, y_offset + n_tasks * cell_height), 
                                     task_col_width, header_height,
                                     boxstyle="square", facecolor=BURGUNDY, edgecolor=BURGUNDY)
        ax.add_patch(header_rect)
        ax.text(x_offset + task_col_width/2, y_offset + n_tasks * cell_height + header_height/2,
                "Task/Activity", ha='center', va='center', fontsize=10, fontweight='bold', color=WHITE)
        
        # Role headers
        for j, role in enumerate(roles):
            x = x_offset + task_col_width + j * cell_width
            y = y_offset + n_tasks * cell_height
            
            header_rect = FancyBboxPatch((x, y), cell_width, header_height,
                                        boxstyle="square", facecolor=BURGUNDY, edgecolor=WHITE, linewidth=1)
            ax.add_patch(header_rect)
            ax.text(x + cell_width/2, y + header_height/2, role, ha='center', va='center',
                   fontsize=9, fontweight='bold', color=WHITE, rotation=0)
        
        # Draw data rows
        for i, task in enumerate(tasks):
            y = y_offset + (n_tasks - 1 - i) * cell_height
            
            # Task cell
            bg_color = LIGHT_GRAY if i % 2 == 0 else WHITE
            task_rect = FancyBboxPatch((x_offset, y), task_col_width, cell_height,
                                      boxstyle="square", facecolor=bg_color, edgecolor=GRAY, linewidth=0.5)
            ax.add_patch(task_rect)
            ax.text(x_offset + 0.1, y + cell_height/2, task, ha='left', va='center', fontsize=9)
            
            # RACI cells
            for j in range(n_roles):
                x = x_offset + task_col_width + j * cell_width
                
                value = matrix[i][j] if i < len(matrix) and j < len(matrix[i]) else ''
                color = raci_colors.get(value.upper(), WHITE)
                text_color = raci_text_colors.get(value.upper(), BLACK)
                
                cell_rect = FancyBboxPatch((x, y), cell_width, cell_height,
                                          boxstyle="square", facecolor=color, edgecolor=GRAY, linewidth=0.5)
                ax.add_patch(cell_rect)
                
                if value:
                    ax.text(x + cell_width/2, y + cell_height/2, value.upper(),
                           ha='center', va='center', fontsize=12, fontweight='bold', color=text_color)
        
        # Legend
        legend_y = 0.3
        legend_items = [('R', 'Responsible'), ('A', 'Accountable'), ('C', 'Consulted'), ('I', 'Informed')]
        legend_x_start = x_offset
        
        for idx, (code, desc) in enumerate(legend_items):
            x = legend_x_start + idx * 2.5
            
            legend_box = FancyBboxPatch((x, legend_y), 0.4, 0.3,
                                       boxstyle="square", facecolor=raci_colors[code], edgecolor=GRAY)
            ax.add_patch(legend_box)
            ax.text(x + 0.2, legend_y + 0.15, code, ha='center', va='center',
                   fontsize=10, fontweight='bold', color=raci_text_colors[code])
            ax.text(x + 0.6, legend_y + 0.15, f"= {desc}", ha='left', va='center', fontsize=9)
        
        ax.set_xlim(0, 12)
        ax.set_ylim(0, total_height + y_offset + 1)
        
        plt.tight_layout()
        
        filepath = self.chart_dir / 'raci_matrix.png'
        plt.savefig(filepath, dpi=150, bbox_inches='tight', facecolor=WHITE)
        plt.close()
        
        return filepath
    
    def generate_swimlane(self, steps, title="Swim Lane Diagram"):
        """
        Generate a swim lane diagram.
        
        Args:
            steps: List of strings in format "Lane Name | Step Description"
                   Use [S] prefix for Start/End, [D] for Decision
            title: Diagram title
            
        Returns:
            Path to the generated image
        """
        # Parse steps into lanes
        lane_steps = {}
        step_sequence = []
        
        for step in steps:
            if '|' in step:
                parts = step.split('|', 1)
                lane = parts[0].strip()
                step_text = parts[1].strip()
            else:
                lane = "Process"
                step_text = step.strip()
            
            if lane not in lane_steps:
                lane_steps[lane] = []
            
            step_sequence.append((lane, step_text, len(lane_steps[lane])))
            lane_steps[lane].append(step_text)
        
        lanes = list(lane_steps.keys())
        n_lanes = len(lanes)
        n_steps = len(step_sequence)
        
        fig_height = max(8, n_steps * 1.0 + 2)
        fig_width = max(12, n_lanes * 3 + 2)
        
        fig, ax = plt.subplots(figsize=(fig_width, fig_height))
        ax.set_xlim(0, fig_width)
        ax.set_ylim(0, fig_height)
        ax.axis('off')
        ax.set_facecolor(WHITE)
        
        # Title
        ax.text(fig_width/2, fig_height - 0.5, title, ha='center', va='center',
                fontsize=16, fontweight='bold', color=BURGUNDY)
        
        # Draw lanes
        lane_width = (fig_width - 2) / n_lanes
        lane_height = fig_height - 2
        
        for i, lane in enumerate(lanes):
            x = 1 + i * lane_width
            color = self.lane_colors[i % len(self.lane_colors)]
            
            # Lane background
            lane_rect = FancyBboxPatch((x, 0.5), lane_width - 0.1, lane_height,
                                      boxstyle="square", facecolor=color, edgecolor=GRAY, linewidth=1)
            ax.add_patch(lane_rect)
            
            # Lane header
            header_rect = FancyBboxPatch((x, lane_height + 0.3), lane_width - 0.1, 0.5,
                                        boxstyle="square", facecolor=BURGUNDY, edgecolor=BURGUNDY)
            ax.add_patch(header_rect)
            ax.text(x + (lane_width - 0.1)/2, lane_height + 0.55, lane,
                   ha='center', va='center', fontsize=10, fontweight='bold', color=WHITE)
        
        # Draw steps
        step_height = 0.6
        y_spacing = (lane_height - 1) / max(n_steps, 1)
        
        step_positions = {}
        
        for idx, (lane, step_text, _) in enumerate(step_sequence):
            lane_idx = lanes.index(lane)
            x_center = 1 + lane_idx * lane_width + (lane_width - 0.1) / 2
            y_pos = lane_height - 0.5 - idx * y_spacing
            
            step_positions[idx] = (x_center, y_pos)
            
            if step_text.upper().startswith('[S]'):
                # Start/End oval
                text = step_text[3:].strip()
                ellipse = patches.Ellipse((x_center, y_pos), lane_width * 0.7, step_height,
                                         facecolor=WHITE, edgecolor=BURGUNDY, linewidth=2)
                ax.add_patch(ellipse)
                ax.text(x_center, y_pos, text, ha='center', va='center', fontsize=9, fontweight='bold')
                
            elif step_text.upper().startswith('[D]'):
                # Decision diamond
                text = step_text[3:].strip()
                diamond = patches.RegularPolygon((x_center, y_pos), numVertices=4, radius=0.4,
                                                orientation=np.pi/4,
                                                facecolor=WHITE, edgecolor=GOLD, linewidth=2)
                ax.add_patch(diamond)
                ax.text(x_center, y_pos, text, ha='center', va='center', fontsize=8)
            else:
                # Process rectangle
                rect = FancyBboxPatch((x_center - lane_width * 0.35, y_pos - step_height/2),
                                     lane_width * 0.7, step_height,
                                     boxstyle="round,pad=0.02,rounding_size=0.1",
                                     facecolor=WHITE, edgecolor=BURGUNDY, linewidth=1.5)
                ax.add_patch(rect)
                ax.text(x_center, y_pos, step_text, ha='center', va='center', fontsize=9)
            
            # Draw arrow to next step
            if idx < n_steps - 1:
                next_x, next_y = None, None
                for next_idx in range(idx + 1, n_steps):
                    if next_idx in step_positions or next_idx == idx + 1:
                        next_lane, _, _ = step_sequence[next_idx]
                        next_lane_idx = lanes.index(next_lane)
                        next_x = 1 + next_lane_idx * lane_width + (lane_width - 0.1) / 2
                        next_y = lane_height - 0.5 - (idx + 1) * y_spacing
                        break
                
                if next_x is not None:
                    ax.annotate('', xy=(next_x, next_y + step_height/2 + 0.1),
                               xytext=(x_center, y_pos - step_height/2 - 0.1),
                               arrowprops=dict(arrowstyle='->', color=BURGUNDY, lw=1.5,
                                             connectionstyle="arc3,rad=0"))
        
        # Footer
        ax.text(fig_width/2, 0.2, "Swim Lane Diagram - Analyze Phase", ha='center', va='center',
                fontsize=9, color=GRAY)
        
        plt.tight_layout()
        
        filepath = self.chart_dir / 'swimlane_diagram.png'
        plt.savefig(filepath, dpi=150, bbox_inches='tight', facecolor=WHITE)
        plt.close()
        
        return filepath
    
    def generate_vsm(self, steps, title="Value Stream Map"):
        """
        Generate a Value Stream Map.
        
        Args:
            steps: List of tuples (step_name, cycle_time, wait_time)
                   Times should be in same units (e.g., minutes, hours, days)
            title: Diagram title
            
        Returns:
            Path to the generated image
        """
        n_steps = len(steps)
        
        fig_width = max(14, n_steps * 2.5 + 2)
        fig, ax = plt.subplots(figsize=(fig_width, 8))
        ax.set_xlim(0, fig_width)
        ax.set_ylim(0, 8)
        ax.axis('off')
        ax.set_facecolor(WHITE)
        
        # Title
        ax.text(fig_width/2, 7.5, title, ha='center', va='center',
                fontsize=16, fontweight='bold', color=BURGUNDY)
        
        # Calculate totals
        total_cycle = sum(s[1] for s in steps)
        total_wait = sum(s[2] for s in steps)
        lead_time = total_cycle + total_wait
        efficiency = (total_cycle / lead_time * 100) if lead_time > 0 else 0
        
        # Draw process boxes and timeline
        box_width = 2.0
        box_height = 1.5
        x_spacing = (fig_width - 2) / (n_steps + 1)
        process_y = 4.5
        timeline_y = 2.0
        
        for i, (name, cycle_time, wait_time) in enumerate(steps):
            x = 1 + (i + 0.5) * x_spacing
            
            # Process box
            proc_box = FancyBboxPatch((x - box_width/2, process_y), box_width, box_height,
                                     boxstyle="square", facecolor=WHITE, edgecolor=BURGUNDY, linewidth=2)
            ax.add_patch(proc_box)
            
            # Process name
            ax.text(x, process_y + box_height - 0.3, name, ha='center', va='center',
                   fontsize=10, fontweight='bold')
            
            # Cycle time
            ax.text(x, process_y + 0.5, f"C/T: {cycle_time}", ha='center', va='center', fontsize=9)
            
            # Arrow to next step
            if i < n_steps - 1:
                ax.annotate('', xy=(x + box_width/2 + x_spacing - box_width/2 - 0.2, process_y + box_height/2),
                           xytext=(x + box_width/2 + 0.1, process_y + box_height/2),
                           arrowprops=dict(arrowstyle='->', color=GOLD, lw=2))
                
                # Wait time above arrow
                mid_x = x + box_width/2 + (x_spacing - box_width) / 2
                
                # Wait time indicator (triangle)
                triangle = patches.RegularPolygon((mid_x, process_y + box_height + 0.3),
                                                 numVertices=3, radius=0.25,
                                                 orientation=0, facecolor=GOLD, edgecolor=BURGUNDY)
                ax.add_patch(triangle)
                ax.text(mid_x, process_y + box_height + 0.8, f"W: {wait_time}",
                       ha='center', va='center', fontsize=8)
            
            # Timeline entry
            # Cycle time bar
            ct_bar = FancyBboxPatch((x - 0.4, timeline_y), 0.8, 0.5,
                                   boxstyle="square", facecolor=BURGUNDY, edgecolor=BURGUNDY)
            ax.add_patch(ct_bar)
            ax.text(x, timeline_y + 0.25, str(cycle_time), ha='center', va='center',
                   fontsize=9, color=WHITE, fontweight='bold')
            
            # Wait time bar (if not last step)
            if i < n_steps - 1:
                wt_x = x + x_spacing / 2
                wt_bar = FancyBboxPatch((wt_x - 0.4, timeline_y), 0.8, 0.5,
                                       boxstyle="square", facecolor=WHITE, edgecolor=GRAY)
                ax.add_patch(wt_bar)
                ax.text(wt_x, timeline_y + 0.25, str(wait_time), ha='center', va='center', fontsize=9)
        
        # Timeline labels
        ax.text(0.5, timeline_y + 0.25, "Timeline:", ha='right', va='center', fontsize=9, fontweight='bold')
        
        # Timeline legend
        ax.add_patch(FancyBboxPatch((1, timeline_y - 0.7), 0.4, 0.3, boxstyle="square",
                                   facecolor=BURGUNDY, edgecolor=BURGUNDY))
        ax.text(1.6, timeline_y - 0.55, "= Cycle Time (Value-Added)", ha='left', va='center', fontsize=8)
        
        ax.add_patch(FancyBboxPatch((5, timeline_y - 0.7), 0.4, 0.3, boxstyle="square",
                                   facecolor=WHITE, edgecolor=GRAY))
        ax.text(5.6, timeline_y - 0.55, "= Wait Time (Non-Value-Added)", ha='left', va='center', fontsize=8)
        
        # Summary box
        summary_x = fig_width - 3.5
        summary_box = FancyBboxPatch((summary_x, 0.5), 3, 1.2,
                                    boxstyle="round,pad=0.02,rounding_size=0.1",
                                    facecolor=LIGHT_GRAY, edgecolor=BURGUNDY, linewidth=2)
        ax.add_patch(summary_box)
        
        ax.text(summary_x + 1.5, 1.5, "Summary", ha='center', va='center',
               fontsize=10, fontweight='bold', color=BURGUNDY)
        ax.text(summary_x + 0.2, 1.15, f"Total Cycle Time: {total_cycle}", ha='left', va='center', fontsize=9)
        ax.text(summary_x + 0.2, 0.9, f"Total Wait Time: {total_wait}", ha='left', va='center', fontsize=9)
        ax.text(summary_x + 0.2, 0.65, f"Lead Time: {lead_time}", ha='left', va='center', fontsize=9)
        
        # Efficiency indicator
        eff_box = FancyBboxPatch((1, 0.5), 2.5, 1.2,
                                boxstyle="round,pad=0.02,rounding_size=0.1",
                                facecolor=BURGUNDY, edgecolor=BURGUNDY)
        ax.add_patch(eff_box)
        ax.text(2.25, 1.3, "Process Efficiency", ha='center', va='center',
               fontsize=9, fontweight='bold', color=WHITE)
        ax.text(2.25, 0.85, f"{efficiency:.1f}%", ha='center', va='center',
               fontsize=18, fontweight='bold', color=GOLD)
        
        # Footer
        ax.text(fig_width/2, 0.15, "Value Stream Map - Analyze Phase", ha='center', va='center',
                fontsize=9, color=GRAY)
        
        plt.tight_layout()
        
        filepath = self.chart_dir / 'value_stream_map.png'
        plt.savefig(filepath, dpi=150, bbox_inches='tight', facecolor=WHITE)
        plt.close()
        
        return filepath
    
    def generate_fishbone(self, effect, causes, title="Fishbone Diagram"):
        """
        Generate a Fishbone (Ishikawa/Cause-and-Effect) diagram.
        
        Args:
            effect: The problem/effect being analyzed
            causes: Dict mapping category to list of causes
                    Categories: Policy/Standards, Materials, Process/Procedures,
                               Physical Environment, People, IT Systems/Equipment
            title: Diagram title
            
        Returns:
            Path to the generated image
        """
        fig, ax = plt.subplots(figsize=(16, 10))
        ax.set_xlim(0, 16)
        ax.set_ylim(0, 10)
        ax.axis('off')
        ax.set_facecolor(WHITE)
        
        # Title
        ax.text(8, 9.5, title, ha='center', va='center',
                fontsize=16, fontweight='bold', color=BURGUNDY)
        
        # Fish spine (main horizontal line)
        spine_y = 5
        spine_start = 1
        spine_end = 13
        ax.plot([spine_start, spine_end], [spine_y, spine_y], color=BURGUNDY, linewidth=3)
        
        # Fish head (effect)
        head_x = 14
        head = FancyBboxPatch((head_x - 1, spine_y - 1), 2.5, 2,
                             boxstyle="round,pad=0.02,rounding_size=0.3",
                             facecolor='#e8d4d8', edgecolor=BURGUNDY, linewidth=2)
        ax.add_patch(head)
        
        # Effect text (wrapped)
        effect_lines = self._wrap_text(effect, 15)
        for i, line in enumerate(effect_lines):
            y_offset = (len(effect_lines) - 1) / 2 - i
            ax.text(head_x + 0.25, spine_y + y_offset * 0.3, line,
                   ha='center', va='center', fontsize=10, fontweight='bold')
        
        # Arrow to head
        ax.annotate('', xy=(head_x - 1, spine_y), xytext=(spine_end, spine_y),
                   arrowprops=dict(arrowstyle='->', color=BURGUNDY, lw=3))
        
        # Categories for Lean Six Sigma
        categories = [
            'Policy/Standards',
            'Materials', 
            'Process/Procedures',
            'Physical Environment',
            'People',
            'IT Systems/Equipment'
        ]
        
        # Position categories - 3 above, 3 below
        top_categories = categories[:3]
        bottom_categories = categories[3:]
        
        # Draw category bones
        x_positions = [3, 6.5, 10]
        
        # Top bones
        for i, cat in enumerate(top_categories):
            x = x_positions[i]
            color = self.fishbone_colors.get(cat, BURGUNDY)
            
            # Diagonal bone
            ax.plot([x, x + 1.5], [spine_y, spine_y + 2.5], color=color, linewidth=2)
            
            # Category label
            ax.text(x + 1.5, spine_y + 2.8, cat, ha='center', va='bottom',
                   fontsize=10, fontweight='bold', color=color)
            
            # Cause branches
            if cat in causes:
                for j, cause in enumerate(causes[cat][:5]):  # Max 5 causes per category
                    # Position along the bone
                    t = 0.2 + j * 0.15
                    bone_x = x + t * 1.5
                    bone_y = spine_y + t * 2.5
                    
                    # Small horizontal line for cause
                    ax.plot([bone_x - 0.8, bone_x], [bone_y, bone_y], color=color, linewidth=1)
                    ax.text(bone_x - 0.9, bone_y, cause, ha='right', va='center', fontsize=8)
        
        # Bottom bones
        for i, cat in enumerate(bottom_categories):
            x = x_positions[i]
            color = self.fishbone_colors.get(cat, BURGUNDY)
            
            # Diagonal bone
            ax.plot([x, x + 1.5], [spine_y, spine_y - 2.5], color=color, linewidth=2)
            
            # Category label
            ax.text(x + 1.5, spine_y - 2.8, cat, ha='center', va='top',
                   fontsize=10, fontweight='bold', color=color)
            
            # Cause branches
            if cat in causes:
                for j, cause in enumerate(causes[cat][:5]):
                    t = 0.2 + j * 0.15
                    bone_x = x + t * 1.5
                    bone_y = spine_y - t * 2.5
                    
                    ax.plot([bone_x - 0.8, bone_x], [bone_y, bone_y], color=color, linewidth=1)
                    ax.text(bone_x - 0.9, bone_y, cause, ha='right', va='center', fontsize=8)
        
        # Footer
        ax.text(8, 0.3, "Fishbone Diagram (Cause-and-Effect) - Analyze Phase", ha='center', va='center',
                fontsize=9, color=GRAY)
        
        plt.tight_layout()
        
        filepath = self.chart_dir / 'fishbone_diagram.png'
        plt.savefig(filepath, dpi=150, bbox_inches='tight', facecolor=WHITE)
        plt.close()
        
        return filepath
    
    def _wrap_text(self, text, max_chars):
        """Wrap text to multiple lines."""
        words = text.split()
        lines = []
        current_line = []
        current_length = 0
        
        for word in words:
            if current_length + len(word) + 1 <= max_chars:
                current_line.append(word)
                current_length += len(word) + 1
            else:
                if current_line:
                    lines.append(' '.join(current_line))
                current_line = [word]
                current_length = len(word)
        
        if current_line:
            lines.append(' '.join(current_line))
        
        return lines


# Test function
if __name__ == "__main__":
    engine = ProcessDiagramEngine()
    
    # Test SIPOC
    print("Generating SIPOC...")
    sipoc_path = engine.generate_sipoc(
        suppliers=["Attorneys", "Parties", "Lower Courts"],
        inputs=["Briefs", "Motions", "Records"],
        process_steps=["Receive Filing", "Review for Compliance", "Docket Entry", "Assign to Panel", "Issue Decision"],
        outputs=["Orders", "Opinions", "Mandates"],
        customers=["Litigants", "Attorneys", "Public"],
        title="Appeals Processing SIPOC"
    )
    print(f"  Saved to: {sipoc_path}")
    
    # Test Process Map
    print("Generating Process Map...")
    process_path = engine.generate_process_map(
        steps=[
            "[S] Start",
            "Receive Document",
            "[D] Complete?",
            "Request Additional Info",
            "Review Document",
            "Enter in System",
            "[S] End"
        ],
        title="Document Processing Flow"
    )
    print(f"  Saved to: {process_path}")
    
    # Test RACI
    print("Generating RACI...")
    raci_path = engine.generate_raci(
        tasks=["Define Problem", "Collect Data", "Analyze Results", "Implement Solution", "Monitor Performance"],
        roles=["Project Lead", "Team Member", "Sponsor", "SME"],
        matrix=[
            ['R', 'C', 'A', 'C'],
            ['A', 'R', 'I', 'C'],
            ['R', 'R', 'I', 'C'],
            ['A', 'R', 'I', 'C'],
            ['R', 'R', 'A', 'I']
        ],
        title="Project RACI Matrix"
    )
    print(f"  Saved to: {raci_path}")
    
    # Test Swim Lane
    print("Generating Swim Lane...")
    swimlane_path = engine.generate_swimlane(
        steps=[
            "Applicant | [S] Submit Application",
            "Front Desk | Receive Application",
            "Front Desk | [D] Complete?",
            "Applicant | Provide Missing Info",
            "Reviewer | Review Application",
            "Reviewer | [D] Approved?",
            "Supervisor | Final Approval",
            "Front Desk | [S] Issue Certificate"
        ],
        title="Application Processing Swim Lane"
    )
    print(f"  Saved to: {swimlane_path}")
    
    # Test VSM
    print("Generating Value Stream Map...")
    vsm_path = engine.generate_vsm(
        steps=[
            ("Receive", 5, 30),
            ("Review", 15, 60),
            ("Process", 20, 45),
            ("Approve", 10, 120),
            ("Complete", 5, 0)
        ],
        title="Case Processing Value Stream"
    )
    print(f"  Saved to: {vsm_path}")
    
    # Test Fishbone
    print("Generating Fishbone...")
    fishbone_path = engine.generate_fishbone(
        effect="Long Processing Time",
        causes={
            'Policy/Standards': ['Outdated procedures', 'Unclear guidelines'],
            'Materials': ['Missing documents', 'Poor quality copies'],
            'Process/Procedures': ['Multiple handoffs', 'Redundant steps', 'No standard work'],
            'Physical Environment': ['Poor workstation layout', 'Noise distractions'],
            'People': ['Training gaps', 'Staff shortages', 'Communication issues'],
            'IT Systems/Equipment': ['Slow system', 'Frequent downtime', 'Manual data entry']
        },
        title="Root Cause Analysis: Processing Delays"
    )
    print(f"  Saved to: {fishbone_path}")
    
    print("\nAll diagrams generated successfully!")
