"""
CiviQual Stats Root Cause Analysis Tools

Provides root cause analysis tools:
- Fishbone (Ishikawa) Diagram Builder
- 5 Whys Template

Copyright (c) 2026 A Step in the Right Direction LLC
"""

from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass, field
from datetime import datetime
import json


@dataclass
class Cause:
    """A cause in a fishbone diagram."""
    text: str
    sub_causes: List['Cause'] = field(default_factory=list)
    
    def to_dict(self) -> Dict:
        return {
            'text': self.text,
            'sub_causes': [sc.to_dict() for sc in self.sub_causes]
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'Cause':
        return cls(
            text=data['text'],
            sub_causes=[cls.from_dict(sc) for sc in data.get('sub_causes', [])]
        )


@dataclass
class FishboneBranch:
    """A branch (category) in a fishbone diagram."""
    category: str
    causes: List[Cause] = field(default_factory=list)
    
    def add_cause(self, text: str) -> Cause:
        """Add a primary cause to this branch."""
        cause = Cause(text=text)
        self.causes.append(cause)
        return cause
    
    def to_dict(self) -> Dict:
        return {
            'category': self.category,
            'causes': [c.to_dict() for c in self.causes]
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'FishboneBranch':
        branch = cls(category=data['category'])
        branch.causes = [Cause.from_dict(c) for c in data.get('causes', [])]
        return branch


@dataclass
class FishboneDiagram:
    """Complete fishbone (Ishikawa) diagram."""
    problem_statement: str
    branches: List[FishboneBranch] = field(default_factory=list)
    created_date: str = ''
    modified_date: str = ''
    notes: str = ''
    
    def __post_init__(self):
        if not self.created_date:
            self.created_date = datetime.now().isoformat()
        self.modified_date = datetime.now().isoformat()
    
    def add_branch(self, category: str) -> FishboneBranch:
        """Add a new category branch."""
        branch = FishboneBranch(category=category)
        self.branches.append(branch)
        self.modified_date = datetime.now().isoformat()
        return branch
    
    def to_dict(self) -> Dict:
        return {
            'problem_statement': self.problem_statement,
            'branches': [b.to_dict() for b in self.branches],
            'created_date': self.created_date,
            'modified_date': self.modified_date,
            'notes': self.notes
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'FishboneDiagram':
        diagram = cls(
            problem_statement=data['problem_statement'],
            created_date=data.get('created_date', ''),
            notes=data.get('notes', '')
        )
        diagram.branches = [FishboneBranch.from_dict(b) for b in data.get('branches', [])]
        diagram.modified_date = data.get('modified_date', datetime.now().isoformat())
        return diagram
    
    def to_json(self) -> str:
        """Export diagram to JSON."""
        return json.dumps(self.to_dict(), indent=2)
    
    @classmethod
    def from_json(cls, json_str: str) -> 'FishboneDiagram':
        """Import diagram from JSON."""
        return cls.from_dict(json.loads(json_str))
    
    def get_all_causes(self) -> List[Tuple[str, str]]:
        """Get all causes as list of (category, cause_text) tuples."""
        causes = []
        for branch in self.branches:
            for cause in branch.causes:
                causes.append((branch.category, cause.text))
                for sub in cause.sub_causes:
                    causes.append((branch.category, f"  → {sub.text}"))
        return causes


class FishboneBuilder:
    """
    Builder for creating fishbone (Ishikawa) diagrams.
    
    Supports the 6M framework:
    - Man (People)
    - Machine (Equipment)
    - Method (Process)
    - Material (Inputs)
    - Measurement (Data)
    - Mother Nature (Environment)
    """
    
    # Standard category frameworks
    SIX_M = ['Man', 'Machine', 'Method', 'Material', 'Measurement', 'Mother Nature']
    FOUR_P = ['Policies', 'Procedures', 'People', 'Plant/Technology']
    FOUR_S = ['Surroundings', 'Suppliers', 'Systems', 'Skills']
    EIGHT_P_SERVICE = ['Price', 'Promotion', 'People', 'Processes', 
                       'Place', 'Policies', 'Procedures', 'Product']
    
    # Public sector / court-specific categories
    COURT_CATEGORIES = [
        'People',           # Staff, judges, litigants, counsel
        'Process',          # Procedures, workflows, case management
        'Technology',       # Systems, CM/ECF, hardware
        'Policy',           # Rules, statutes, administrative orders
        'Resources',        # Budget, facilities, materials
        'Environment'       # External factors, stakeholders
    ]
    
    @staticmethod
    def create_6m(problem_statement: str) -> FishboneDiagram:
        """Create a fishbone diagram with 6M categories."""
        diagram = FishboneDiagram(problem_statement=problem_statement)
        for category in FishboneBuilder.SIX_M:
            diagram.add_branch(category)
        return diagram
    
    @staticmethod
    def create_4p(problem_statement: str) -> FishboneDiagram:
        """Create a fishbone diagram with 4P categories."""
        diagram = FishboneDiagram(problem_statement=problem_statement)
        for category in FishboneBuilder.FOUR_P:
            diagram.add_branch(category)
        return diagram
    
    @staticmethod
    def create_court(problem_statement: str) -> FishboneDiagram:
        """Create a fishbone diagram with court-specific categories."""
        diagram = FishboneDiagram(problem_statement=problem_statement)
        for category in FishboneBuilder.COURT_CATEGORIES:
            diagram.add_branch(category)
        return diagram
    
    @staticmethod
    def create_custom(problem_statement: str, categories: List[str]) -> FishboneDiagram:
        """Create a fishbone diagram with custom categories."""
        diagram = FishboneDiagram(problem_statement=problem_statement)
        for category in categories:
            diagram.add_branch(category)
        return diagram
    
    @staticmethod
    def generate_text_diagram(diagram: FishboneDiagram) -> str:
        """Generate a text representation of the fishbone diagram."""
        lines = []
        lines.append("=" * 60)
        lines.append("FISHBONE DIAGRAM")
        lines.append("=" * 60)
        lines.append("")
        lines.append(f"Problem: {diagram.problem_statement}")
        lines.append("")
        
        for branch in diagram.branches:
            lines.append(f"┌─ {branch.category.upper()} {'─' * (50 - len(branch.category))}")
            for cause in branch.causes:
                lines.append(f"│   ├── {cause.text}")
                for sub in cause.sub_causes:
                    lines.append(f"│   │     └── {sub.text}")
            lines.append("│")
        
        lines.append("└" + "─" * 59 + "► EFFECT")
        lines.append(f"                      {diagram.problem_statement}")
        lines.append("")
        
        if diagram.notes:
            lines.append("Notes:")
            lines.append(diagram.notes)
        
        return "\n".join(lines)


@dataclass
class WhyStep:
    """A step in the 5 Whys analysis."""
    why_number: int
    question: str
    answer: str
    notes: str = ''
    
    def to_dict(self) -> Dict:
        return {
            'why_number': self.why_number,
            'question': self.question,
            'answer': self.answer,
            'notes': self.notes
        }


@dataclass
class FiveWhysAnalysis:
    """Complete 5 Whys analysis."""
    problem_statement: str
    steps: List[WhyStep] = field(default_factory=list)
    root_cause: str = ''
    countermeasure: str = ''
    created_date: str = ''
    modified_date: str = ''
    analyst: str = ''
    
    def __post_init__(self):
        if not self.created_date:
            self.created_date = datetime.now().isoformat()
        self.modified_date = datetime.now().isoformat()
    
    def add_why(self, question: str, answer: str, notes: str = '') -> WhyStep:
        """Add a why step."""
        why_number = len(self.steps) + 1
        step = WhyStep(why_number=why_number, question=question, answer=answer, notes=notes)
        self.steps.append(step)
        self.modified_date = datetime.now().isoformat()
        return step
    
    def set_root_cause(self, root_cause: str) -> None:
        """Set the identified root cause."""
        self.root_cause = root_cause
        self.modified_date = datetime.now().isoformat()
    
    def set_countermeasure(self, countermeasure: str) -> None:
        """Set the proposed countermeasure."""
        self.countermeasure = countermeasure
        self.modified_date = datetime.now().isoformat()
    
    def to_dict(self) -> Dict:
        return {
            'problem_statement': self.problem_statement,
            'steps': [s.to_dict() for s in self.steps],
            'root_cause': self.root_cause,
            'countermeasure': self.countermeasure,
            'created_date': self.created_date,
            'modified_date': self.modified_date,
            'analyst': self.analyst
        }
    
    def to_json(self) -> str:
        """Export to JSON."""
        return json.dumps(self.to_dict(), indent=2)
    
    @classmethod
    def from_json(cls, json_str: str) -> 'FiveWhysAnalysis':
        """Import from JSON."""
        data = json.loads(json_str)
        analysis = cls(
            problem_statement=data['problem_statement'],
            root_cause=data.get('root_cause', ''),
            countermeasure=data.get('countermeasure', ''),
            created_date=data.get('created_date', ''),
            analyst=data.get('analyst', '')
        )
        for step_data in data.get('steps', []):
            step = WhyStep(**step_data)
            analysis.steps.append(step)
        return analysis


class FiveWhysBuilder:
    """
    Builder for 5 Whys root cause analysis.
    
    The 5 Whys is an iterative interrogation technique to explore
    cause-and-effect relationships underlying a problem.
    """
    
    @staticmethod
    def create(problem_statement: str, analyst: str = '') -> FiveWhysAnalysis:
        """Create a new 5 Whys analysis."""
        return FiveWhysAnalysis(problem_statement=problem_statement, analyst=analyst)
    
    @staticmethod
    def generate_prompts(previous_answer: str) -> List[str]:
        """
        Generate suggested follow-up questions based on previous answer.
        
        Args:
            previous_answer: The previous answer in the chain
            
        Returns:
            List of suggested "Why" questions
        """
        # Generic templates
        templates = [
            f"Why did {previous_answer.lower().rstrip('.')}?",
            f"What caused {previous_answer.lower().rstrip('.')}?",
            f"Why does this happen?",
            f"What is the underlying reason?",
            f"Why is that a problem?"
        ]
        return templates[:3]  # Return top 3 suggestions
    
    @staticmethod
    def generate_text_report(analysis: FiveWhysAnalysis) -> str:
        """Generate a text report of the 5 Whys analysis."""
        lines = []
        lines.append("=" * 60)
        lines.append("5 WHYS ROOT CAUSE ANALYSIS")
        lines.append("=" * 60)
        lines.append("")
        lines.append(f"Problem Statement: {analysis.problem_statement}")
        if analysis.analyst:
            lines.append(f"Analyst: {analysis.analyst}")
        lines.append(f"Date: {analysis.created_date[:10]}")
        lines.append("")
        lines.append("-" * 60)
        
        for step in analysis.steps:
            lines.append(f"\nWHY #{step.why_number}")
            lines.append(f"Q: {step.question}")
            lines.append(f"A: {step.answer}")
            if step.notes:
                lines.append(f"Notes: {step.notes}")
        
        lines.append("")
        lines.append("-" * 60)
        
        if analysis.root_cause:
            lines.append(f"\nROOT CAUSE:")
            lines.append(f"  {analysis.root_cause}")
        
        if analysis.countermeasure:
            lines.append(f"\nCOUNTERMEASURE:")
            lines.append(f"  {analysis.countermeasure}")
        
        lines.append("")
        lines.append("=" * 60)
        
        return "\n".join(lines)
    
    @staticmethod
    def validate_analysis(analysis: FiveWhysAnalysis) -> Tuple[bool, List[str]]:
        """
        Validate that the 5 Whys analysis is complete and logical.
        
        Returns:
            Tuple of (is_valid, list_of_issues)
        """
        issues = []
        
        if not analysis.problem_statement:
            issues.append("Problem statement is missing")
        
        if len(analysis.steps) < 3:
            issues.append(f"Only {len(analysis.steps)} why(s) documented. Consider going deeper.")
        
        if len(analysis.steps) > 7:
            issues.append(f"{len(analysis.steps)} whys documented. This may indicate the problem is too broad.")
        
        for step in analysis.steps:
            if not step.answer:
                issues.append(f"Why #{step.why_number} has no answer")
        
        if not analysis.root_cause:
            issues.append("Root cause not identified")
        
        if not analysis.countermeasure:
            issues.append("Countermeasure not defined")
        
        return len(issues) == 0, issues
