import json
from dataclasses import dataclass, field, asdict


@dataclass
class Education:
    school: str = ""
    degree: str = ""
    graduation_date: str = ""


@dataclass
class Experience:
    job_title: str = ""
    company: str = ""
    start_date: str = ""
    end_date: str = ""
    description: str = ""


@dataclass
class CandidateProfile:
    name: str = ""
    email: str = ""
    phone: str = ""

    # Stores the candidate's programming languages,
    # technical skills, and other relevant abilities.
    skills: list[str] = field(default_factory=list)
    education: list[Education] = field(default_factory=list)
    experience: list[Experience] = field(default_factory=list)
    projects: list[str] = field(default_factory=list)
    certifications: list[str] = field(default_factory=list)

    def to_dict(self):
        return asdict(self)

    def to_json(self):
        return json.dumps(self.to_dict(), indent=4)