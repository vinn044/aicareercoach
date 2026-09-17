from dataclasses import dataclass, field


@dataclass # this is a basic way to create a object that holds information 
class CandidateProfile:
    name: str = ""
    email: str = ""
    phone: str = ""

    skills: list[str] = field(default_factory=list)
    education: list[str] = field(default_factory=list)
    experience: list[str] = field(default_factory=list)