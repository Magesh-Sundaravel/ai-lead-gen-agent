from typing import TypedDict


class RawLead(TypedDict):
    title: str
    url: str
    snippet: str


class QualifiedLead(TypedDict):
    title: str
    url: str
    snippet: str
    score: int
    reasoning: str
    priority: str
    niche: str


class Email(TypedDict):
    url: str
    subject: str
    body: str


class LeadGenState(TypedDict):
    query: str
    raw_leads: list[RawLead]
    qualified_leads: list[QualifiedLead]
    emails: list[Email]
    status: str
