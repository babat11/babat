"""Rule-based legal mapper for the Nigerian context.

This module provides deterministic enrichment for analysis results. Given a
classified ``category`` (and, as a fallback, raw complaint text), it returns
the rights, constitutional sections, laws, and agencies that may potentially be
relevant.

IMPORTANT: This mapping provides LEGAL INFORMATION ONLY. It is a starter
reference set and is NOT exhaustive or authoritative. It must never be presented
as legal advice.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class LegalMapping:
    """A single rule-based mapping for an incident category."""

    category: str
    rights: list[str] = field(default_factory=list)
    constitution: list[str] = field(default_factory=list)
    laws: list[str] = field(default_factory=list)
    agencies: list[str] = field(default_factory=list)
    keywords: list[str] = field(default_factory=list)
    risk_level: str = "Medium"


# Starter mappings (>= 20). Constitution references are to the Constitution of
# the Federal Republic of Nigeria 1999 (as amended) unless otherwise noted.
LEGAL_MAPPINGS: dict[str, LegalMapping] = {
    "Illegal Detention": LegalMapping(
        category="Illegal Detention",
        rights=["Right to Personal Liberty", "Right to Fair Hearing"],
        constitution=["Section 35 Constitution", "Section 36 Constitution"],
        laws=["Administration of Criminal Justice Act 2015"],
        agencies=[
            "National Human Rights Commission",
            "Legal Aid Council of Nigeria",
        ],
        keywords=["detained", "detention", "arrest", "arrested", "locked up", "cell"],
        risk_level="High",
    ),
    "Police Brutality": LegalMapping(
        category="Police Brutality",
        rights=["Right to Dignity of Human Person", "Right to Life"],
        constitution=["Section 34 Constitution", "Section 33 Constitution"],
        laws=["Anti-Torture Act 2017", "Police Act 2020"],
        agencies=[
            "National Human Rights Commission",
            "Police Service Commission",
            "Public Complaint Rapid Response Unit",
        ],
        keywords=["beaten", "tortured", "brutality", "assault by police", "slapped"],
        risk_level="High",
    ),
    "Unlawful Killing": LegalMapping(
        category="Unlawful Killing",
        rights=["Right to Life"],
        constitution=["Section 33 Constitution"],
        laws=["Criminal Code Act", "Penal Code (Northern States)"],
        agencies=[
            "National Human Rights Commission",
            "Nigeria Police Force",
        ],
        keywords=["killed", "shot dead", "extrajudicial", "death in custody"],
        risk_level="High",
    ),
    "Unlawful Search and Seizure": LegalMapping(
        category="Unlawful Search and Seizure",
        rights=["Right to Privacy of Home and Property"],
        constitution=["Section 37 Constitution"],
        laws=["Administration of Criminal Justice Act 2015"],
        agencies=["National Human Rights Commission"],
        keywords=["searched my house", "seized", "raided", "phone search", "checkpoint"],
        risk_level="Medium",
    ),
    "Freedom of Expression Violation": LegalMapping(
        category="Freedom of Expression Violation",
        rights=["Right to Freedom of Expression and the Press"],
        constitution=["Section 39 Constitution"],
        laws=["Cybercrimes (Prohibition, Prevention etc.) Act 2015"],
        agencies=["National Human Rights Commission"],
        keywords=["arrested for posting", "censored", "tweet", "social media", "journalist"],
        risk_level="Medium",
    ),
    "Freedom of Assembly Violation": LegalMapping(
        category="Freedom of Assembly Violation",
        rights=["Right to Peaceful Assembly and Association"],
        constitution=["Section 40 Constitution"],
        laws=["Public Order Act"],
        agencies=["National Human Rights Commission"],
        keywords=["protest", "rally", "dispersed", "demonstration", "assembly"],
        risk_level="Medium",
    ),
    "Religious Discrimination": LegalMapping(
        category="Religious Discrimination",
        rights=[
            "Right to Freedom of Thought, Conscience and Religion",
            "Right to Freedom from Discrimination",
        ],
        constitution=["Section 38 Constitution", "Section 42 Constitution"],
        laws=[],
        agencies=["National Human Rights Commission"],
        keywords=["religion", "religious", "church", "mosque", "faith", "worship"],
        risk_level="Medium",
    ),
    "Gender or Sex Discrimination": LegalMapping(
        category="Gender or Sex Discrimination",
        rights=["Right to Freedom from Discrimination"],
        constitution=["Section 42 Constitution"],
        laws=["Violence Against Persons (Prohibition) Act 2015"],
        agencies=[
            "National Human Rights Commission",
            "Ministry of Women Affairs and Social Development",
        ],
        keywords=["because i am a woman", "gender", "sex discrimination", "denied because"],
        risk_level="Medium",
    ),
    "Domestic Violence": LegalMapping(
        category="Domestic Violence",
        rights=["Right to Dignity of Human Person", "Right to Life"],
        constitution=["Section 34 Constitution"],
        laws=["Violence Against Persons (Prohibition) Act 2015"],
        agencies=[
            "Nigeria Police Force",
            "Ministry of Women Affairs and Social Development",
            "National Human Rights Commission",
        ],
        keywords=["husband beat", "wife beat", "domestic", "spouse", "partner abuse"],
        risk_level="High",
    ),
    "Sexual Assault": LegalMapping(
        category="Sexual Assault",
        rights=["Right to Dignity of Human Person"],
        constitution=["Section 34 Constitution"],
        laws=[
            "Violence Against Persons (Prohibition) Act 2015",
            "Criminal Code Act",
        ],
        agencies=[
            "Nigeria Police Force",
            "National Agency for the Prohibition of Trafficking in Persons",
            "National Human Rights Commission",
        ],
        keywords=["rape", "raped", "sexual assault", "molested", "defiled"],
        risk_level="High",
    ),
    "Human Trafficking": LegalMapping(
        category="Human Trafficking",
        rights=["Right to Personal Liberty", "Right to Dignity of Human Person"],
        constitution=["Section 34 Constitution", "Section 35 Constitution"],
        laws=[
            "Trafficking in Persons (Prohibition) Enforcement and "
            "Administration Act 2015",
        ],
        agencies=[
            "National Agency for the Prohibition of Trafficking in Persons",
            "Nigeria Police Force",
        ],
        keywords=["trafficked", "trafficking", "smuggled", "forced labour", "sold"],
        risk_level="High",
    ),
    "Child Rights Violation": LegalMapping(
        category="Child Rights Violation",
        rights=["Rights of the Child", "Right to Dignity of Human Person"],
        constitution=["Section 34 Constitution"],
        laws=["Child Rights Act 2003"],
        agencies=[
            "Ministry of Women Affairs and Social Development",
            "National Human Rights Commission",
        ],
        keywords=["child", "minor", "underage", "school dropout", "child labour"],
        risk_level="High",
    ),
    "Employment Dispute": LegalMapping(
        category="Employment Dispute",
        rights=["Labour protections", "Right to Fair Hearing"],
        constitution=["Section 36 Constitution"],
        laws=["Labour Act", "Employee's Compensation Act 2010"],
        agencies=[
            "Federal Ministry of Labour and Employment",
            "National Industrial Court of Nigeria",
        ],
        keywords=["sacked", "fired", "salary", "wages", "employer", "dismissed", "unpaid"],
        risk_level="Medium",
    ),
    "Workplace Harassment": LegalMapping(
        category="Workplace Harassment",
        rights=["Right to Dignity of Human Person", "Labour protections"],
        constitution=["Section 34 Constitution"],
        laws=["Labour Act", "Violence Against Persons (Prohibition) Act 2015"],
        agencies=[
            "Federal Ministry of Labour and Employment",
            "National Human Rights Commission",
        ],
        keywords=["harassed at work", "boss", "supervisor", "workplace", "hostile"],
        risk_level="Medium",
    ),
    "Consumer Protection": LegalMapping(
        category="Consumer Protection",
        rights=["Consumer rights"],
        constitution=[],
        laws=["Federal Competition and Consumer Protection Act 2018"],
        agencies=["Federal Competition and Consumer Protection Commission"],
        keywords=["faulty product", "refund", "overcharged", "scammed", "defective"],
        risk_level="Low",
    ),
    "Banking and Financial Dispute": LegalMapping(
        category="Banking and Financial Dispute",
        rights=["Consumer rights", "Right to Property"],
        constitution=["Section 44 Constitution"],
        laws=[
            "Banks and Other Financial Institutions Act 2020",
            "Federal Competition and Consumer Protection Act 2018",
        ],
        agencies=[
            "Central Bank of Nigeria (Consumer Protection Department)",
            "Federal Competition and Consumer Protection Commission",
        ],
        keywords=["bank", "debited", "fraud", "atm", "transfer", "account blocked"],
        risk_level="Medium",
    ),
    "Land or Property Dispute": LegalMapping(
        category="Land or Property Dispute",
        rights=["Right to Property", "Right to Fair Hearing"],
        constitution=["Section 43 Constitution", "Section 44 Constitution"],
        laws=["Land Use Act 1978"],
        agencies=["State Ministry of Lands", "High Court of the State"],
        keywords=["land", "property", "eviction", "landlord", "tenant", "title", "demolish"],
        risk_level="Medium",
    ),
    "Unlawful Eviction": LegalMapping(
        category="Unlawful Eviction",
        rights=["Right to Property", "Right to Fair Hearing"],
        constitution=["Section 43 Constitution"],
        laws=["Recovery of Premises laws (State Tenancy Laws)"],
        agencies=["State Ministry of Lands", "Legal Aid Council of Nigeria"],
        keywords=["evicted", "thrown out", "locked out", "landlord removed"],
        risk_level="Medium",
    ),
    "Data Privacy Violation": LegalMapping(
        category="Data Privacy Violation",
        rights=["Right to Privacy"],
        constitution=["Section 37 Constitution"],
        laws=[
            "Nigeria Data Protection Act 2023",
            "Cybercrimes (Prohibition, Prevention etc.) Act 2015",
        ],
        agencies=["Nigeria Data Protection Commission"],
        keywords=["data", "privacy", "leaked", "personal information", "tracked"],
        risk_level="Medium",
    ),
    "Cybercrime or Online Fraud": LegalMapping(
        category="Cybercrime or Online Fraud",
        rights=["Right to Property"],
        constitution=["Section 44 Constitution"],
        laws=["Cybercrimes (Prohibition, Prevention etc.) Act 2015"],
        agencies=[
            "Economic and Financial Crimes Commission",
            "Nigeria Police Force (NPF-NCCC)",
        ],
        keywords=["online fraud", "hacked", "phishing", "scammed online", "cyber"],
        risk_level="Medium",
    ),
    "Corruption or Bribery": LegalMapping(
        category="Corruption or Bribery",
        rights=["Right to Fair Hearing"],
        constitution=["Section 36 Constitution"],
        laws=[
            "Corrupt Practices and Other Related Offences Act 2000",
            "Economic and Financial Crimes Commission (Establishment) Act 2004",
        ],
        agencies=[
            "Independent Corrupt Practices and Other Related Offences Commission",
            "Economic and Financial Crimes Commission",
        ],
        keywords=["bribe", "bribery", "corruption", "extortion", "kickback", "demanded money"],
        risk_level="Medium",
    ),
    "Discrimination (Disability)": LegalMapping(
        category="Discrimination (Disability)",
        rights=["Right to Freedom from Discrimination"],
        constitution=["Section 42 Constitution"],
        laws=[
            "Discrimination Against Persons with Disabilities "
            "(Prohibition) Act 2018",
        ],
        agencies=[
            "National Commission for Persons with Disabilities",
            "National Human Rights Commission",
        ],
        keywords=["disability", "disabled", "wheelchair", "denied access", "impairment"],
        risk_level="Medium",
    ),
    "Denial of Fair Hearing": LegalMapping(
        category="Denial of Fair Hearing",
        rights=["Right to Fair Hearing"],
        constitution=["Section 36 Constitution"],
        laws=["Administration of Criminal Justice Act 2015"],
        agencies=[
            "Legal Aid Council of Nigeria",
            "National Human Rights Commission",
        ],
        keywords=["no lawyer", "denied hearing", "not allowed to speak", "trial without"],
        risk_level="Medium",
    ),
}

# A safe fallback applied when no category matches.
FALLBACK_MAPPING = LegalMapping(
    category="General Inquiry",
    rights=["Right to Fair Hearing"],
    constitution=["Section 36 Constitution"],
    laws=[],
    agencies=[
        "National Human Rights Commission",
        "Legal Aid Council of Nigeria",
    ],
    keywords=[],
    risk_level="Low",
)


def _normalise(text: str) -> str:
    return text.strip().lower()


def get_mapping(category: str | None, complaint: str | None = None) -> LegalMapping:
    """Resolve a :class:`LegalMapping` from a category or complaint text.

    Resolution order:
        1. Exact (case-insensitive) category match.
        2. Substring match against complaint keywords.
        3. Fallback mapping.

    Args:
        category: The classified category (may be ``None`` or empty).
        complaint: Optional raw complaint text for keyword fallback.

    Returns:
        The best-matching :class:`LegalMapping`.
    """
    if category:
        norm = _normalise(category)
        for key, mapping in LEGAL_MAPPINGS.items():
            if _normalise(key) == norm:
                return mapping

    if complaint:
        norm_complaint = _normalise(complaint)
        for mapping in LEGAL_MAPPINGS.values():
            if any(kw in norm_complaint for kw in mapping.keywords):
                return mapping

    logger.debug("No legal mapping matched; using fallback.")
    return FALLBACK_MAPPING


def _merge_unique(*lists: list[str]) -> list[str]:
    """Merge multiple lists preserving order and removing duplicates."""
    seen: set[str] = set()
    out: list[str] = []
    for lst in lists:
        for item in lst:
            if item and item not in seen:
                seen.add(item)
                out.append(item)
    return out


def enrich_analysis(analysis: dict[str, object], complaint: str) -> dict[str, object]:
    """Enrich an LLM analysis dict with rule-based legal mappings.

    The LLM output is treated as authoritative for facts/summary, while the
    deterministic mapper guarantees that recognised categories always include a
    baseline set of rights, laws, and agencies.

    Args:
        analysis: The (already validated/normalised) analysis dictionary.
        complaint: The original complaint text, used for keyword fallback.

    Returns:
        The enriched analysis dictionary.
    """
    category = str(analysis.get("category") or "")
    mapping = get_mapping(category, complaint)

    if not category:
        analysis["category"] = mapping.category

    analysis["possible_rights"] = _merge_unique(
        _as_str_list(analysis.get("possible_rights")), mapping.rights
    )
    analysis["relevant_laws"] = _merge_unique(
        _as_str_list(analysis.get("relevant_laws")),
        mapping.constitution,
        mapping.laws,
    )
    analysis["agencies"] = _merge_unique(
        _as_str_list(analysis.get("agencies")), mapping.agencies
    )

    if not analysis.get("risk_level") or analysis.get("risk_level") == "Unknown":
        analysis["risk_level"] = mapping.risk_level

    return analysis


def _as_str_list(value: object) -> list[str]:
    """Coerce an arbitrary value into a list of strings."""
    if isinstance(value, list):
        return [str(v) for v in value if v is not None]
    if value is None:
        return []
    return [str(value)]
