"""Synthetic, non-confidential corpus used to make the reference demo runnable."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class DemoDocument:
    document_id: str
    title: str
    source_type: str
    content: str
    metadata: dict[str, str]


DEMO_DOCUMENTS: list[DemoDocument] = [
    DemoDocument(
        document_id="internal_security_requirements_v1",
        title="Internal Security and Procurement Requirements v1",
        source_type="internal",
        metadata={"owner": "Information Security", "classification": "internal"},
        content="""
# Mandatory vendor requirements

## Security baseline
The preferred vendor must provide encryption at rest using an industry-standard encryption mechanism and encryption in transit using TLS 1.2 or later. The vendor must support SAML or OpenID Connect single sign-on, maintain a documented incident response process, and provide a current independent assurance report such as SOC 2 Type II or ISO 27001 certification.

## Data governance
Customer data for the European business unit must be processed in the European Economic Area unless a documented legal transfer assessment and executive approval are completed. The procurement team must be able to configure retention periods and export an audit log covering administrative actions.

## Commercial requirements
The standard business case assumes 180 named users, a three-year decision horizon, implementation cost, recurring annual licence cost, and a 10 percent contingency on the first-year subtotal. A recommendation must identify costs that are excluded or uncertain.

## Approval policy
A recommendation may proceed only when material conclusions are supported by approved sources. Conflicting source statements, missing assurance evidence, and assumptions about pricing require manual review.
""".strip(),
    ),
    DemoDocument(
        document_id="vendor_northstar_security_2026",
        title="Northstar Cloud Security Overview 2026",
        source_type="internal",
        metadata={"vendor": "Northstar", "document_type": "security"},
        content="""
# Northstar Cloud Security Overview

Northstar encrypts customer content at rest using AES-256 and uses TLS 1.3 for all supported browser and API traffic. Enterprise tenants can configure SAML 2.0 single sign-on and SCIM-based user provisioning.

Northstar maintains ISO 27001 certification and a SOC 2 Type II report that can be shared under NDA. The service offers regional data residency for the European Economic Area. The administrative audit log records configuration changes, role assignments, exports, and authentication policy changes. Enterprise administrators may configure retention controls from 30 to 3650 days.

Northstar states that all standard support tickets are handled within the European support organization, but it does not state whether every diagnostic log remains exclusively in the EEA during major incident investigation.
""".strip(),
    ),
    DemoDocument(
        document_id="vendor_bluepeak_security_2026",
        title="BluePeak Platform Trust Center Extract 2026",
        source_type="internal",
        metadata={"vendor": "BluePeak", "document_type": "security"},
        content="""
# BluePeak Platform Trust Center Extract

BluePeak encrypts data at rest and in transit. The platform supports SSO through SAML 2.0. BluePeak is certified to ISO 27001 and provides a SOC 2 Type I report upon request.

The default processing location is Frankfurt, Germany. BluePeak may use globally distributed sub-processors for customer support and service diagnostics. Retention controls are available through support requests, not through the administrative console. Audit logs are available for user authentication but do not include configuration exports in the standard tier.

BluePeak describes its security program as aligned to enterprise requirements, but the document does not identify the assurance period for its SOC report.
""".strip(),
    ),
    DemoDocument(
        document_id="vendor_veridian_security_2026",
        title="Veridian Enterprise Security Brief 2026",
        source_type="internal",
        metadata={"vendor": "Veridian", "document_type": "security"},
        content="""
# Veridian Enterprise Security Brief

Veridian uses AES-256 encryption for customer data at rest and TLS 1.2 or later in transit. The platform supports OpenID Connect and SAML single sign-on. Veridian has completed SOC 2 Type II attestation and publishes an ISO 27001 certificate.

Veridian offers EEA data residency for production customer content. Administrative activity is recorded in exportable audit logs, including policy changes and privileged role assignments. Retention policies are configurable by administrators.

Veridian currently requires a separate paid add-on for audit-log exports and does not provide a committed recovery time objective in the standard contract. Its documentation describes sub-processors but does not state a maximum notification lead time for changes.
""".strip(),
    ),
    DemoDocument(
        document_id="procurement_risk_rubric_v1",
        title="Procurement Risk Rubric v1",
        source_type="internal",
        metadata={"owner": "Procurement", "document_type": "policy"},
        content="""
# Procurement Risk Rubric

A high-severity risk exists when a mandatory security control is absent, when regional data-processing commitments are unclear, or when a material commercial assumption is unsupported. A medium-severity risk exists when a control is present but requires a paid add-on or manual operating procedure. A low-severity risk exists when documentation lacks a non-material operational detail.

For vendor selection, use the following decision order: mandatory security controls, supportable data residency, verifiable total cost of ownership, operational administration, then optional capabilities. Do not treat marketing language as evidence. Escalate when evidence is incomplete rather than selecting a vendor solely on price.
""".strip(),
    ),
    DemoDocument(
        document_id="vendor_pricing_schedule_2026",
        title="Approved Vendor Pricing Schedule 2026",
        source_type="pricing",
        metadata={"owner": "Procurement", "document_type": "pricing"},
        content="""
# Approved Vendor Pricing Schedule

Northstar: 180 named users, EUR 42,000 implementation cost, EUR 710 annual licence per user, EUR 18,000 annual support, and no annual add-on cost.

BluePeak: 180 named users, EUR 30,000 implementation cost, EUR 585 annual licence per user, EUR 15,000 annual support, and EUR 12,000 annual add-on cost for audit export capability.

Veridian: 180 named users, EUR 39,000 implementation cost, EUR 640 annual licence per user, EUR 17,000 annual support, and EUR 9,000 annual audit-log export add-on.

The procurement model applies a 10 percent contingency to the first-year subtotal and excludes taxes, renewal uplifts, usage overages, and foreign-exchange effects.
""".strip(),
    ),
    DemoDocument(
        document_id="public_eu_ai_governance_note",
        title="Public Research Note: EU AI Governance Considerations",
        source_type="public_research",
        metadata={"source": "synthetic public research note", "topic": "governance"},
        content="""
# Public research note

For enterprise AI procurement, decision makers commonly require evidence of data-processing location, administrative auditability, incident processes, access control, and vendor assurance material. This research note is included only to demonstrate a controlled public-research source type. It is not legal advice and must not be treated as a regulatory determination.
""".strip(),
    ),
]
