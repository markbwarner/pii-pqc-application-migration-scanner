from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional


@dataclass
class PiiMatch:
    line_number: int
    attribute: str
    category: str
    detector: str
    confidence: float
    impact_hint: str
    pattern_name: str | None = None


@dataclass
class FileClassification:
    layer: str
    context: str
    confidence: float
    reasons: List[str] = field(default_factory=list)


@dataclass
class ComplexityAssessment:
    score: float
    rating: str
    rationale: List[str] = field(default_factory=list)


@dataclass
class PqcFinding:
    line_number: int
    category: str
    algorithm: str
    matched_text: str
    finding_kind: str
    migration_class: str
    confidence: float
    severity: str


@dataclass
class DependencyReference:
    name: str
    ecosystem: str
    reference_type: str
    source: str
    line_number: int = 0
    version: str = ""
    related_categories: List[str] = field(default_factory=list)


@dataclass
class CbomComponent:
    name: str
    ecosystem: str
    version: str = ""
    component_type: str = "library"
    source_files: List[str] = field(default_factory=list)
    related_categories: List[str] = field(default_factory=list)
    origin: str = "observed"


@dataclass
class AiSummary:
    provider: str
    model: str
    summary_markdown: str
    prompt_version: str = "phase3-v1"
    generated_at_utc: str = ""
    advisory_only: bool = True


@dataclass
class AiFileRecommendation:
    path: str
    priority: str
    recommendation: str
    rationale: str


@dataclass
class AiWorkPackage:
    name: str
    rationale: str
    related_categories: List[str] = field(default_factory=list)
    target_paths: List[str] = field(default_factory=list)


@dataclass
class AiDependencyGuidance:
    name: str
    meaning: str
    why_it_matters: str


@dataclass
class AiRecommendations:
    provider: str
    model: str
    summary_markdown: str
    file_recommendations: List[AiFileRecommendation] = field(default_factory=list)
    work_packages: List[AiWorkPackage] = field(default_factory=list)
    dependency_guidance: List[AiDependencyGuidance] = field(default_factory=list)
    prompt_version: str = "phase3-rec-v1"
    generated_at_utc: str = ""
    advisory_only: bool = True


@dataclass
class OwnershipAssessment:
    likely_change_owner: str
    likely_change_target: bool
    recommended_change_action: str
    ownership_confidence: float
    role_in_flow: str
    frontend_reference_only: bool
    backend_owner_confidence: float
    jdbc_substitution_candidate: bool
    endpoint_correlation_score: float = 0.0
    matched_endpoints: List[str] = field(default_factory=list)
    matched_payload_fields: List[str] = field(default_factory=list)
    likely_system_of_record_path: List[str] = field(default_factory=list)
    related_files: List[str] = field(default_factory=list)
    rationale: List[str] = field(default_factory=list)


@dataclass
class FileReport:
    path: str
    lines_of_code: int
    classification: FileClassification
    pii_matches: List[PiiMatch] = field(default_factory=list)
    summary_by_category: Dict[str, int] = field(default_factory=dict)
    jdbc_candidate_count: int = 0
    code_change_candidate_count: int = 0
    rest_call_count: int = 0
    sql_statement_count: int = 0
    endpoint_count: int = 0
    service_call_hint_count: int = 0
    backend_hint_count: int = 0
    integration_hint_count: int = 0
    service_call_hint_breakdown: Dict[str, int] = field(default_factory=dict)
    backend_hint_breakdown: Dict[str, int] = field(default_factory=dict)
    integration_hint_breakdown: Dict[str, int] = field(default_factory=dict)
    sql_verbs: List[str] = field(default_factory=list)
    sql_data_action: str = ""
    sensitive_tables: Dict[str, List[str]] = field(default_factory=dict)
    ownership: Optional[OwnershipAssessment] = None
    complexity: Optional[ComplexityAssessment] = None
    pqc_findings: List[PqcFinding] = field(default_factory=list)
    pqc_summary_by_category: Dict[str, int] = field(default_factory=dict)
    pqc_migration_classes: Dict[str, int] = field(default_factory=dict)
    pqc_vulnerable_algorithms: List[str] = field(default_factory=list)
    pqc_implementation_finding_count: int = 0
    pqc_reference_finding_count: int = 0
    pqc_likely_change_target: bool = False
    pqc_recommended_change_action: str = ""
    pqc_complexity: Optional[ComplexityAssessment] = None
    dependency_references: List[DependencyReference] = field(default_factory=list)
    notes: List[str] = field(default_factory=list)


@dataclass
class ScanReport:
    root_path: str
    scan_domains: List[str]
    files_scanned: int
    files_with_findings: int
    files_with_pii: int
    total_pii_matches: int
    files_with_pqc: int
    total_pqc_findings: int
    file_reports: List[FileReport] = field(default_factory=list)
    totals_by_category: Dict[str, int] = field(default_factory=dict)
    tables_summary: Dict[str, Dict[str, List[str] | int]] = field(default_factory=dict)
    jdbc_candidate_total: int = 0
    code_change_candidate_total: int = 0
    pqc_totals_by_category: Dict[str, int] = field(default_factory=dict)
    pqc_migration_class_totals: Dict[str, int] = field(default_factory=dict)
    pqc_likely_change_target_total: int = 0
    dependency_reference_total: int = 0
    dependency_package_summary: Dict[str, int] = field(default_factory=dict)
    cbom_components: List[CbomComponent] = field(default_factory=list)
    imported_cbom_component_total: int = 0
    ai_summary: Optional[AiSummary] = None
    ai_recommendations: Optional[AiRecommendations] = None
