"""Job dataset loading and validation for VetAlign-AI.

The matcher must only ever return jobs that exist in a supplied dataset. This
module is the single gate for that data: it loads the file, rejects malformed
or duplicated records, and resolves model-returned job IDs back to the original
record so that employer names, links and contacts are copied rather than
generated.

Design notes
------------
* Demo data is fictional and must stay visibly labelled. ``is_demo`` is
  inherited from the dataset header unless a record overrides it.
* Only ``http``/``https`` URLs are accepted. Anything else (``javascript:``,
  ``data:``) is dropped, because these values are later rendered as links.
* Validation raises on structural faults but records non-fatal problems in
  ``JobDataset.warnings`` so the UI can show them without crashing.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from datetime import date, datetime
from pathlib import Path
from typing import Any, Iterable

DATA_DIR = Path(__file__).parent / "data"
DEMO_DATASET = DATA_DIR / "jobs_demo.json"

#: Jobs older than this are surfaced as stale rather than presented as current.
STALE_AFTER_DAYS = 45

REQUIRED_FIELDS = (
    "job_id",
    "title",
    "employer",
    "required_skills",
    "city_or_district",
    "application_url",
    "source_url",
    "last_checked",
    "status",
)

LIST_FIELDS = ("required_skills", "preferred_skills", "qualification_requirements")
ALLOWED_STATUS = {"open", "closed", "unknown"}
ALLOWED_SCHEMES = ("http://", "https://")


class JobDataError(Exception):
    """Raised when a job dataset cannot be trusted enough to use."""


def _safe_url(value: Any) -> str:
    """Return the URL if it uses an allowed scheme, else an empty string."""
    if not isinstance(value, str):
        return ""
    candidate = value.strip()
    return candidate if candidate.lower().startswith(ALLOWED_SCHEMES) else ""


def _as_list(value: Any) -> list[str]:
    if value is None:
        return []
    if not isinstance(value, list):
        raise JobDataError(f"expected a list, got {type(value).__name__}")
    return [str(item).strip() for item in value if str(item).strip()]


def _parse_date(value: Any) -> date | None:
    try:
        return datetime.strptime(str(value), "%Y-%m-%d").date()
    except (TypeError, ValueError):
        return None


@dataclass(frozen=True)
class Job:
    """One validated job record."""

    job_id: str
    title: str
    employer: str
    required_skills: list[str]
    preferred_skills: list[str]
    qualification_requirements: list[str]
    city_or_district: str
    application_url: str
    source_url: str
    contact: str | None
    last_checked: date | None
    status: str
    is_demo: bool

    @property
    def is_open(self) -> bool:
        return self.status == "open"

    def is_stale(self, today: date | None = None) -> bool:
        if self.last_checked is None:
            return True
        today = today or date.today()
        return (today - self.last_checked).days > STALE_AFTER_DAYS

    def target_text(self) -> str:
        """Plain-text job description for the veteran's "target role" field."""
        lines = [f"{self.title} — {self.employer} ({self.city_or_district})"]
        if self.required_skills:
            lines.append("Required skills: " + ", ".join(self.required_skills))
        if self.preferred_skills:
            lines.append("Preferred skills: " + ", ".join(self.preferred_skills))
        if self.qualification_requirements:
            lines.append("Requirements: " + "; ".join(self.qualification_requirements))
        return "\n".join(lines)

    def prompt_dict(self) -> dict[str, Any]:
        """The subset sent to the model.

        Links, employer contacts and demo flags are deliberately withheld so the
        model cannot echo a mangled URL; they are re-attached from this record
        after the model returns a job_id.
        """
        return {
            "job_id": self.job_id,
            "title": self.title,
            "required_skills": self.required_skills,
            "preferred_skills": self.preferred_skills,
            "qualification_requirements": self.qualification_requirements,
            "city_or_district": self.city_or_district,
        }


@dataclass
class JobDataset:
    """A validated collection of jobs plus any non-fatal data problems."""

    jobs: list[Job] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    dataset_id: str = ""
    is_demo: bool = True
    source_path: Path | None = None

    def __len__(self) -> int:
        return len(self.jobs)

    @property
    def is_empty(self) -> bool:
        return not self.jobs

    def open_jobs(self, today: date | None = None) -> list[Job]:
        """Jobs safe to shortlist: open and not stale."""
        return [j for j in self.jobs if j.is_open and not j.is_stale(today)]

    def by_id(self, job_id: str) -> Job | None:
        wanted = str(job_id).strip()
        for job in self.jobs:
            if job.job_id == wanted:
                return job
        return None

    def resolve(self, job_ids: Iterable[Any]) -> tuple[list[Job], list[str]]:
        """Map model-returned IDs to real records.

        Returns ``(jobs, rejected_ids)``. Unknown and duplicate IDs are rejected
        rather than silently dropped, so the caller can report that the model
        invented or repeated a job.
        """
        resolved: list[Job] = []
        rejected: list[str] = []
        seen: set[str] = set()
        for raw in job_ids or []:
            key = str(raw).strip()
            job = self.by_id(key)
            if job is None or key in seen:
                rejected.append(key)
                continue
            seen.add(key)
            resolved.append(job)
        return resolved, rejected


def _build_job(raw: Any, index: int, dataset_is_demo: bool, warnings: list[str]) -> Job:
    if not isinstance(raw, dict):
        raise JobDataError(f"record {index} is not an object")

    missing = [f for f in REQUIRED_FIELDS if f not in raw or raw[f] in (None, "")]
    if missing:
        raise JobDataError(f"record {index} is missing required field(s): {', '.join(missing)}")

    job_id = str(raw["job_id"]).strip()

    try:
        lists = {name: _as_list(raw.get(name)) for name in LIST_FIELDS}
    except JobDataError as exc:
        raise JobDataError(f"{job_id}: {exc}") from exc

    if not lists["required_skills"]:
        raise JobDataError(f"{job_id}: required_skills must contain at least one skill")

    status = str(raw["status"]).strip().lower()
    if status not in ALLOWED_STATUS:
        warnings.append(f"{job_id}: unrecognised status {status!r}, treated as 'unknown'.")
        status = "unknown"

    application_url = _safe_url(raw.get("application_url"))
    if not application_url:
        warnings.append(f"{job_id}: application_url is missing or not an http(s) link; link hidden.")
    source_url = _safe_url(raw.get("source_url"))
    if not source_url:
        warnings.append(f"{job_id}: source_url is missing or not an http(s) link; provenance hidden.")

    last_checked = _parse_date(raw.get("last_checked"))
    if last_checked is None:
        warnings.append(f"{job_id}: last_checked is not a YYYY-MM-DD date; treated as stale.")

    contact = raw.get("contact")
    contact = str(contact).strip() if contact else None

    return Job(
        job_id=job_id,
        title=str(raw["title"]).strip(),
        employer=str(raw["employer"]).strip(),
        required_skills=lists["required_skills"],
        preferred_skills=lists["preferred_skills"],
        qualification_requirements=lists["qualification_requirements"],
        city_or_district=str(raw["city_or_district"]).strip(),
        application_url=application_url,
        source_url=source_url,
        contact=contact,
        last_checked=last_checked,
        status=status,
        is_demo=bool(raw.get("is_demo", dataset_is_demo)),
    )


def load_jobs(path: str | Path | None = None) -> JobDataset:
    """Load and validate a job dataset.

    Raises :class:`JobDataError` for a missing file, invalid JSON, a bad shape
    or duplicate job IDs. An intentionally empty ``jobs`` list is allowed so the
    no-match path can be tested.
    """
    source = Path(path) if path else DEMO_DATASET

    try:
        text = source.read_text(encoding="utf-8")
    except FileNotFoundError as exc:
        raise JobDataError(f"Job dataset not found: {source}") from exc
    except OSError as exc:
        raise JobDataError(f"Could not read job dataset {source}: {exc}") from exc

    try:
        payload = json.loads(text)
    except json.JSONDecodeError as exc:
        raise JobDataError(f"Job dataset {source.name} is not valid JSON: {exc}") from exc

    if not isinstance(payload, dict) or not isinstance(payload.get("jobs"), list):
        raise JobDataError(f"Job dataset {source.name} must be an object with a 'jobs' list.")

    dataset_is_demo = bool(payload.get("is_demo", True))
    warnings: list[str] = []
    jobs: list[Job] = []
    seen: set[str] = set()

    for index, raw in enumerate(payload["jobs"]):
        job = _build_job(raw, index, dataset_is_demo, warnings)
        if job.job_id in seen:
            raise JobDataError(f"Duplicate job_id {job.job_id!r} in {source.name}.")
        seen.add(job.job_id)
        jobs.append(job)

    return JobDataset(
        jobs=jobs,
        warnings=warnings,
        dataset_id=str(payload.get("dataset_id", source.stem)),
        is_demo=dataset_is_demo,
        source_path=source,
    )


# ------------------------------------------------------------ Google Sheet
#
# A volunteer maintains jobs in a Google Sheet (File > Share > Publish to web >
# CSV). Employers can submit roles through a Google Form; a volunteer copies a
# checked submission into the jobs tab and sets status to "open". The same
# validation applies as for the JSON file, but one bad row is skipped with a
# reason instead of rejecting the whole sheet.

MAX_SHEET_BYTES = 1_000_000
SHEET_TIMEOUT_S = 8

#: Friendly column names (as typed by a person or a Form) -> record fields.
COLUMN_ALIASES = {
    "job_title": "title", "role": "title", "company": "employer",
    "employer_name": "employer", "city": "city_or_district", "location": "city_or_district",
    "district": "city_or_district", "skills_required": "required_skills",
    "skills": "required_skills", "nice_to_have_skills": "preferred_skills",
    "qualifications": "qualification_requirements", "application_link": "application_url",
    "apply_link": "application_url", "link": "application_url", "demo": "is_demo",
}


def _column(name: str) -> str:
    key = "_".join(name.strip().lower().replace("/", " ").split())
    return COLUMN_ALIASES.get(key, key)


def _split_list(value: str) -> list[str]:
    """Skills are typed in one cell, separated by semicolons or new lines."""
    return [part.strip() for part in value.replace("\n", ";").split(";") if part.strip()]


def _yes(value: str, default: bool) -> bool:
    text = value.strip().lower()
    if text in ("no", "false", "0", "real", "n"):
        return False
    if text in ("yes", "true", "1", "demo", "fictional", "y"):
        return True
    return default


def parse_jobs_csv(text: str, source: str = "Google Sheet") -> JobDataset:
    """Parse sheet rows into a validated dataset; bad rows become warnings."""
    import csv
    import io

    reader = csv.DictReader(io.StringIO(text))
    if not reader.fieldnames:
        raise JobDataError(f"{source} is empty or has no header row.")
    warnings: list[str] = []
    jobs: list[Job] = []
    seen: set[str] = set()
    for index, row in enumerate(reader):
        sheet_row = index + 2  # header is row 1 in the spreadsheet
        raw: dict[str, Any] = {}
        for header, value in row.items():
            if header is None or not header.strip():
                continue
            raw[_column(header)] = (value or "").strip()
        if not any(raw.values()):
            continue  # blank line
        raw.setdefault("job_id", "")
        if not raw["job_id"]:
            raw["job_id"] = f"SHEET-{sheet_row:03d}"
        for name in LIST_FIELDS:
            raw[name] = _split_list(raw.get(name, ""))
        if not raw.get("source_url"):
            raw["source_url"] = raw.get("application_url", "")
        # Rows are fictional unless the sheet explicitly says otherwise: a real
        # vacancy wrongly marked demo is safer than the reverse.
        raw["is_demo"] = _yes(raw.get("is_demo", ""), default=True)
        raw["contact"] = raw.get("contact") or None
        try:
            job = _build_job(raw, sheet_row, True, warnings)
        except JobDataError as exc:
            warnings.append(f"Row {sheet_row} skipped: {exc}")
            continue
        if job.job_id in seen:
            warnings.append(f"Row {sheet_row} skipped: duplicate job_id {job.job_id!r}.")
            continue
        seen.add(job.job_id)
        jobs.append(job)
    return JobDataset(jobs=jobs, warnings=warnings, dataset_id=source,
                      is_demo=all(j.is_demo for j in jobs))


def fetch_jobs_csv(url: str) -> JobDataset:
    """Download a published sheet. Raises JobDataError on any failure."""
    from urllib.error import URLError
    from urllib.request import Request, urlopen

    if not str(url).lower().startswith("https://"):
        raise JobDataError("The job sheet link must start with https://")
    try:
        request = Request(url, headers={"User-Agent": "VetAlign-AI job list"})
        with urlopen(request, timeout=SHEET_TIMEOUT_S) as response:  # noqa: S310 - https only
            body = response.read(MAX_SHEET_BYTES + 1)
    except (URLError, OSError, ValueError) as exc:
        raise JobDataError(f"Could not download the job sheet ({type(exc).__name__}).") from None
    if len(body) > MAX_SHEET_BYTES:
        raise JobDataError("The job sheet is larger than 1 MB.")
    return parse_jobs_csv(body.decode("utf-8-sig", errors="replace"))


def report(path: str | Path | None = None, today: date | None = None) -> tuple[int, str]:
    """Plain-text health check for whoever maintains the job list.

    Returns ``(exit_code, text)``: 0 when the file is usable, 1 when it is not.
    """
    try:
        target = str(path or "")
        if target.lower().startswith("https://"):
            data = fetch_jobs_csv(target)
        elif target.lower().endswith(".csv"):
            data = parse_jobs_csv(Path(target).read_text(encoding="utf-8-sig"), Path(target).name)
        else:
            data = load_jobs(path)
    except (JobDataError, OSError) as exc:
        return 1, f"NOT USABLE: {exc}"
    today = today or date.today()
    current = data.open_jobs(today)
    stale = [j for j in data.jobs if j.is_open and j.is_stale(today)]
    closed = [j for j in data.jobs if not j.is_open]
    lines = [
        f"Dataset {data.dataset_id}: {len(data)} records "
        f"({'FICTIONAL demo' if data.is_demo else 'real listings'})",
        f"  shown to veterans now : {len(current)}",
        f"  stale (> {STALE_AFTER_DAYS} days, re-check or close): {len(stale)}",
        f"  closed / unknown      : {len(closed)}",
    ]
    lines += [f"    STALE  {j.job_id}  {j.title}  last checked {j.last_checked}" for j in stale]
    lines += [f"  WARNING {w}" for w in data.warnings]
    return 0, "\n".join(lines)


if __name__ == "__main__":
    import sys

    code, text = report(sys.argv[1] if len(sys.argv) > 1 else None)
    print(text)
    sys.exit(code)
