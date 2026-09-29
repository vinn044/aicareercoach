import json
from dataclasses import dataclass, field, asdict


@dataclass # this is a basic way to create a object that holds information 
class CandidateProfile:
    name: str = ""
    email: str = ""
    phone: str = ""

    skills: list[str] = field(default_factory=list)
    education: list[str] = field(default_factory=list)
    experience: list[str] = field(default_factory=list)
    projects: list[str] = field(default_factory=list)
    certifications: list[str] = field(default_factory=list)

    def to_dict(self):
        return asdict(self)

    def to_json(self):
        return json.dumps(self.to_dict(), indent=4)