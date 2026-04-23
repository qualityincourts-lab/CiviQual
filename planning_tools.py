"""
CiviQual Stats Planning Tools

Provides quality planning tools:
- FMEA (Failure Mode and Effects Analysis) Worksheet
- Control Plan Template

Copyright (c) 2026 A Step in the Right Direction LLC
"""

from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
import json


@dataclass
class FMEAItem:
    """A single failure mode in an FMEA."""
    id: str
    process_step: str
    potential_failure_mode: str
    potential_effects: str
    severity: int  # 1-10
    potential_causes: str
    occurrence: int  # 1-10
    current_controls: str
    detection: int  # 1-10
    rpn: int = 0  # Calculated: S * O * D
    recommended_actions: str = ''
    responsibility: str = ''
    target_date: str = ''
    actions_taken: str = ''
    new_severity: Optional[int] = None
    new_occurrence: Optional[int] = None
    new_detection: Optional[int] = None
    new_rpn: Optional[int] = None
    
    def __post_init__(self):
        self.calculate_rpn()
    
    def calculate_rpn(self) -> int:
        """Calculate Risk Priority Number."""
        self.rpn = self.severity * self.occurrence * self.detection
        return self.rpn
    
    def calculate_new_rpn(self) -> Optional[int]:
        """Calculate new RPN after actions."""
        if all(v is not None for v in [self.new_severity, self.new_occurrence, self.new_detection]):
            self.new_rpn = self.new_severity * self.new_occurrence * self.new_detection
            return self.new_rpn
        return None
    
    def rpn_reduction(self) -> Optional[float]:
        """Calculate RPN reduction percentage."""
        if self.new_rpn is not None and self.rpn > 0:
            return ((self.rpn - self.new_rpn) / self.rpn) * 100
        return None
    
    def to_dict(self) -> Dict:
        return {
            'id': self.id,
            'process_step': self.process_step,
            'potential_failure_mode': self.potential_failure_mode,
            'potential_effects': self.potential_effects,
            'severity': self.severity,
            'potential_causes': self.potential_causes,
            'occurrence': self.occurrence,
            'current_controls': self.current_controls,
            'detection': self.detection,
            'rpn': self.rpn,
            'recommended_actions': self.recommended_actions,
            'responsibility': self.responsibility,
            'target_date': self.target_date,
            'actions_taken': self.actions_taken,
            'new_severity': self.new_severity,
            'new_occurrence': self.new_occurrence,
            'new_detection': self.new_detection,
            'new_rpn': self.new_rpn
        }


@dataclass
class FMEA:
    """Complete FMEA (Failure Mode and Effects Analysis) worksheet."""
    title: str
    process_name: str
    items: List[FMEAItem] = field(default_factory=list)
    team_members: List[str] = field(default_factory=list)
    fmea_date: str = ''
    revision: str = '1.0'
    created_date: str = ''
    modified_date: str = ''
    notes: str = ''
    
    # RPN thresholds for prioritization
    HIGH_RPN_THRESHOLD = 125
    MEDIUM_RPN_THRESHOLD = 80
    
    def __post_init__(self):
        if not self.created_date:
            self.created_date = datetime.now().isoformat()
        if not self.fmea_date:
            self.fmea_date = datetime.now().strftime('%Y-%m-%d')
        self.modified_date = datetime.now().isoformat()
    
    def add_item(
        self,
        process_step: str,
        potential_failure_mode: str,
        potential_effects: str,
        severity: int,
        potential_causes: str,
        occurrence: int,
        current_controls: str,
        detection: int,
        recommended_actions: str = '',
        responsibility: str = '',
        target_date: str = ''
    ) -> FMEAItem:
        """Add a failure mode item."""
        # Validate ratings
        for val, name in [(severity, 'Severity'), (occurrence, 'Occurrence'), (detection, 'Detection')]:
            if not 1 <= val <= 10:
                raise ValueError(f"{name} must be between 1 and 10")
        
        item_id = f"FM-{len(self.items) + 1:03d}"
        
        item = FMEAItem(
            id=item_id,
            process_step=process_step,
            potential_failure_mode=potential_failure_mode,
            potential_effects=potential_effects,
            severity=severity,
            potential_causes=potential_causes,
            occurrence=occurrence,
            current_controls=current_controls,
            detection=detection,
            recommended_actions=recommended_actions,
            responsibility=responsibility,
            target_date=target_date
        )
        
        self.items.append(item)
        self.modified_date = datetime.now().isoformat()
        return item
    
    def get_high_rpn_items(self) -> List[FMEAItem]:
        """Get items with high RPN (>= HIGH_RPN_THRESHOLD)."""
        return [item for item in self.items if item.rpn >= self.HIGH_RPN_THRESHOLD]
    
    def get_items_sorted_by_rpn(self, descending: bool = True) -> List[FMEAItem]:
        """Get items sorted by RPN."""
        return sorted(self.items, key=lambda x: x.rpn, reverse=descending)
    
    def get_statistics(self) -> Dict:
        """Get FMEA summary statistics."""
        if not self.items:
            return {}
        
        rpns = [item.rpn for item in self.items]
        severities = [item.severity for item in self.items]
        
        return {
            'total_items': len(self.items),
            'high_rpn_count': len([r for r in rpns if r >= self.HIGH_RPN_THRESHOLD]),
            'medium_rpn_count': len([r for r in rpns if self.MEDIUM_RPN_THRESHOLD <= r < self.HIGH_RPN_THRESHOLD]),
            'low_rpn_count': len([r for r in rpns if r < self.MEDIUM_RPN_THRESHOLD]),
            'max_rpn': max(rpns),
            'avg_rpn': sum(rpns) / len(rpns),
            'max_severity': max(severities),
            'critical_items': len([s for s in severities if s >= 9])
        }
    
    def to_dict(self) -> Dict:
        return {
            'title': self.title,
            'process_name': self.process_name,
            'items': [item.to_dict() for item in self.items],
            'team_members': self.team_members,
            'fmea_date': self.fmea_date,
            'revision': self.revision,
            'created_date': self.created_date,
            'modified_date': self.modified_date,
            'notes': self.notes
        }
    
    def to_json(self) -> str:
        """Export to JSON."""
        return json.dumps(self.to_dict(), indent=2)
    
    @classmethod
    def from_json(cls, json_str: str) -> 'FMEA':
        """Import from JSON."""
        data = json.loads(json_str)
        fmea = cls(
            title=data['title'],
            process_name=data['process_name'],
            team_members=data.get('team_members', []),
            fmea_date=data.get('fmea_date', ''),
            revision=data.get('revision', '1.0'),
            created_date=data.get('created_date', ''),
            notes=data.get('notes', '')
        )
        for item_data in data.get('items', []):
            item = FMEAItem(**item_data)
            fmea.items.append(item)
        return fmea
    
    def generate_text_report(self) -> str:
        """Generate a text report of the FMEA."""
        lines = []
        lines.append("=" * 80)
        lines.append("FAILURE MODE AND EFFECTS ANALYSIS (FMEA)")
        lines.append("=" * 80)
        lines.append("")
        lines.append(f"Title: {self.title}")
        lines.append(f"Process: {self.process_name}")
        lines.append(f"Date: {self.fmea_date}")
        lines.append(f"Revision: {self.revision}")
        if self.team_members:
            lines.append(f"Team: {', '.join(self.team_members)}")
        lines.append("")
        
        stats = self.get_statistics()
        if stats:
            lines.append("-" * 80)
            lines.append("SUMMARY")
            lines.append("-" * 80)
            lines.append(f"Total Failure Modes: {stats['total_items']}")
            lines.append(f"High Risk (RPN >= {self.HIGH_RPN_THRESHOLD}): {stats['high_rpn_count']}")
            lines.append(f"Medium Risk (RPN {self.MEDIUM_RPN_THRESHOLD}-{self.HIGH_RPN_THRESHOLD-1}): {stats['medium_rpn_count']}")
            lines.append(f"Low Risk (RPN < {self.MEDIUM_RPN_THRESHOLD}): {stats['low_rpn_count']}")
            lines.append(f"Maximum RPN: {stats['max_rpn']}")
            lines.append(f"Average RPN: {stats['avg_rpn']:.1f}")
            lines.append("")
        
        lines.append("-" * 80)
        lines.append("FAILURE MODES (sorted by RPN)")
        lines.append("-" * 80)
        
        for item in self.get_items_sorted_by_rpn():
            lines.append("")
            lines.append(f"[{item.id}] Process Step: {item.process_step}")
            lines.append(f"  Failure Mode: {item.potential_failure_mode}")
            lines.append(f"  Effects: {item.potential_effects}")
            lines.append(f"  Causes: {item.potential_causes}")
            lines.append(f"  Current Controls: {item.current_controls}")
            lines.append(f"  S={item.severity} O={item.occurrence} D={item.detection} → RPN={item.rpn}")
            
            if item.rpn >= self.HIGH_RPN_THRESHOLD:
                lines.append(f"  ⚠️ HIGH RISK - Action Required")
            
            if item.recommended_actions:
                lines.append(f"  Recommended Actions: {item.recommended_actions}")
            if item.responsibility:
                lines.append(f"  Responsibility: {item.responsibility}")
            if item.target_date:
                lines.append(f"  Target Date: {item.target_date}")
            
            if item.new_rpn is not None:
                reduction = item.rpn_reduction()
                lines.append(f"  NEW: S={item.new_severity} O={item.new_occurrence} D={item.new_detection} → RPN={item.new_rpn}")
                if reduction:
                    lines.append(f"  RPN Reduction: {reduction:.1f}%")
        
        lines.append("")
        lines.append("=" * 80)
        lines.append("Rating Scales:")
        lines.append("  Severity (S): 1=None, 5=Moderate, 10=Hazardous")
        lines.append("  Occurrence (O): 1=Remote, 5=Occasional, 10=Very High")
        lines.append("  Detection (D): 1=Almost Certain, 5=Moderate, 10=Absolute Uncertainty")
        lines.append("=" * 80)
        
        return "\n".join(lines)


class ControlType(Enum):
    """Types of process controls."""
    PREVENTION = "Prevention"
    DETECTION = "Detection"
    REACTION = "Reaction"


@dataclass
class ControlPlanItem:
    """A single item in a Control Plan."""
    id: str
    process_step: str
    process_description: str
    machine_device: str
    characteristic: str
    specification: str
    measurement_technique: str
    sample_size: str
    sample_frequency: str
    control_method: str
    control_type: str
    reaction_plan: str
    responsible: str
    
    def to_dict(self) -> Dict:
        return {
            'id': self.id,
            'process_step': self.process_step,
            'process_description': self.process_description,
            'machine_device': self.machine_device,
            'characteristic': self.characteristic,
            'specification': self.specification,
            'measurement_technique': self.measurement_technique,
            'sample_size': self.sample_size,
            'sample_frequency': self.sample_frequency,
            'control_method': self.control_method,
            'control_type': self.control_type,
            'reaction_plan': self.reaction_plan,
            'responsible': self.responsible
        }


@dataclass
class ControlPlan:
    """Complete Control Plan document."""
    title: str
    process_name: str
    items: List[ControlPlanItem] = field(default_factory=list)
    part_number: str = ''
    revision: str = '1.0'
    prepared_by: str = ''
    approved_by: str = ''
    effective_date: str = ''
    created_date: str = ''
    modified_date: str = ''
    notes: str = ''
    
    def __post_init__(self):
        if not self.created_date:
            self.created_date = datetime.now().isoformat()
        if not self.effective_date:
            self.effective_date = datetime.now().strftime('%Y-%m-%d')
        self.modified_date = datetime.now().isoformat()
    
    def add_item(
        self,
        process_step: str,
        process_description: str,
        machine_device: str,
        characteristic: str,
        specification: str,
        measurement_technique: str,
        sample_size: str,
        sample_frequency: str,
        control_method: str,
        control_type: str = 'Detection',
        reaction_plan: str = '',
        responsible: str = ''
    ) -> ControlPlanItem:
        """Add a control plan item."""
        item_id = f"CP-{len(self.items) + 1:03d}"
        
        item = ControlPlanItem(
            id=item_id,
            process_step=process_step,
            process_description=process_description,
            machine_device=machine_device,
            characteristic=characteristic,
            specification=specification,
            measurement_technique=measurement_technique,
            sample_size=sample_size,
            sample_frequency=sample_frequency,
            control_method=control_method,
            control_type=control_type,
            reaction_plan=reaction_plan,
            responsible=responsible
        )
        
        self.items.append(item)
        self.modified_date = datetime.now().isoformat()
        return item
    
    def get_by_process_step(self, step: str) -> List[ControlPlanItem]:
        """Get all items for a specific process step."""
        return [item for item in self.items if item.process_step == step]
    
    def get_unique_process_steps(self) -> List[str]:
        """Get list of unique process steps in order."""
        seen = set()
        steps = []
        for item in self.items:
            if item.process_step not in seen:
                seen.add(item.process_step)
                steps.append(item.process_step)
        return steps
    
    def to_dict(self) -> Dict:
        return {
            'title': self.title,
            'process_name': self.process_name,
            'items': [item.to_dict() for item in self.items],
            'part_number': self.part_number,
            'revision': self.revision,
            'prepared_by': self.prepared_by,
            'approved_by': self.approved_by,
            'effective_date': self.effective_date,
            'created_date': self.created_date,
            'modified_date': self.modified_date,
            'notes': self.notes
        }
    
    def to_json(self) -> str:
        """Export to JSON."""
        return json.dumps(self.to_dict(), indent=2)
    
    @classmethod
    def from_json(cls, json_str: str) -> 'ControlPlan':
        """Import from JSON."""
        data = json.loads(json_str)
        plan = cls(
            title=data['title'],
            process_name=data['process_name'],
            part_number=data.get('part_number', ''),
            revision=data.get('revision', '1.0'),
            prepared_by=data.get('prepared_by', ''),
            approved_by=data.get('approved_by', ''),
            effective_date=data.get('effective_date', ''),
            created_date=data.get('created_date', ''),
            notes=data.get('notes', '')
        )
        for item_data in data.get('items', []):
            item = ControlPlanItem(**item_data)
            plan.items.append(item)
        return plan
    
    def generate_text_report(self) -> str:
        """Generate a text report of the Control Plan."""
        lines = []
        lines.append("=" * 100)
        lines.append("CONTROL PLAN")
        lines.append("=" * 100)
        lines.append("")
        lines.append(f"Title: {self.title}")
        lines.append(f"Process: {self.process_name}")
        if self.part_number:
            lines.append(f"Part Number: {self.part_number}")
        lines.append(f"Revision: {self.revision}")
        lines.append(f"Effective Date: {self.effective_date}")
        if self.prepared_by:
            lines.append(f"Prepared By: {self.prepared_by}")
        if self.approved_by:
            lines.append(f"Approved By: {self.approved_by}")
        lines.append("")
        
        lines.append("-" * 100)
        
        current_step = ''
        for item in self.items:
            if item.process_step != current_step:
                current_step = item.process_step
                lines.append("")
                lines.append(f"PROCESS STEP: {current_step}")
                lines.append("-" * 50)
            
            lines.append(f"  [{item.id}] {item.process_description}")
            lines.append(f"    Machine/Device: {item.machine_device}")
            lines.append(f"    Characteristic: {item.characteristic}")
            lines.append(f"    Specification: {item.specification}")
            lines.append(f"    Measurement: {item.measurement_technique}")
            lines.append(f"    Sample: {item.sample_size} every {item.sample_frequency}")
            lines.append(f"    Control Method: {item.control_method} ({item.control_type})")
            if item.reaction_plan:
                lines.append(f"    Reaction Plan: {item.reaction_plan}")
            if item.responsible:
                lines.append(f"    Responsible: {item.responsible}")
            lines.append("")
        
        lines.append("=" * 100)
        
        return "\n".join(lines)
    
    @staticmethod
    def create_from_fmea(fmea: FMEA, high_rpn_only: bool = True) -> 'ControlPlan':
        """
        Create a Control Plan from an FMEA.
        
        Generates control items for failure modes, especially high-RPN items.
        """
        plan = ControlPlan(
            title=f"Control Plan - {fmea.title}",
            process_name=fmea.process_name
        )
        
        items_to_convert = fmea.get_high_rpn_items() if high_rpn_only else fmea.items
        
        for fm in items_to_convert:
            plan.add_item(
                process_step=fm.process_step,
                process_description=f"Control for: {fm.potential_failure_mode}",
                machine_device="[Specify]",
                characteristic=fm.potential_failure_mode,
                specification="[Define specification]",
                measurement_technique="[Define measurement]",
                sample_size="[Define sample size]",
                sample_frequency="[Define frequency]",
                control_method=fm.current_controls if fm.current_controls else "[Define controls]",
                control_type="Detection",
                reaction_plan=fm.recommended_actions if fm.recommended_actions else "[Define reaction]",
                responsible=fm.responsibility if fm.responsibility else "[Assign]"
            )
        
        return plan
