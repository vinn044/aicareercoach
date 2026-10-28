"""Internal integration contract. Call from a trusted worker after parsing/ranking.
This module stores results; it does not generate AI judgments or run teammates' prototypes.
"""
from django.db import transaction
from django.core.exceptions import ValidationError
from .models import Feedback, JobMatch, Resume

class StaleAnalysis(ValueError): pass

@transaction.atomic
def store_analysis(*, owner, resume_id, expected_updated_at, structured_data, feedback, matches):
    resume = Resume.objects.select_for_update().get(pk=resume_id, owner=owner)
    # A worker must record updated_at BEFORE processing; never attach results to edited text.
    if resume.updated_at != expected_updated_at:
        raise StaleAnalysis('Resume changed while analysis was running; analyze it again.')
    if not isinstance(structured_data, dict) or not isinstance(feedback, list) or not isinstance(matches, list):
        raise ValidationError('Expected a profile object and feedback/matches lists.')
    if len(feedback) > 100 or len(matches) > 100:
        raise ValidationError('At most 100 feedback items and 100 matches per analysis.')
    # Explicit allowlists prevent a result payload from injecting ownership/status fields.
    def rows(model, items, allowed):
        output = []
        for item in items:
            if not isinstance(item, dict) or set(item) - allowed:
                raise ValidationError('Unexpected analysis fields.')
            row = model(resume=resume, **item)
            row.full_clean()
            output.append(row)
        return output
    # Delete inside the transaction before validating replacement uniqueness against the DB.
    resume.feedback.all().delete()
    resume.matches.all().delete()
    feedback_rows = rows(Feedback, feedback, {'kind', 'message', 'evidence', 'suggestion'})
    match_rows = rows(JobMatch, matches, {'external_id', 'title', 'company', 'url', 'score', 'explanation'})
    for match in match_rows:
        # URLValidator permits FTP; job links in the UI must use HTTP(S) only.
        if match.url and not match.url.startswith(('https://', 'http://')):
            raise ValidationError('Job URLs must use HTTP or HTTPS.')
        if not -1 <= match.score <= 1:
            raise ValidationError('Score must be a finite cosine similarity between -1 and 1.')
    if len({m.external_id for m in match_rows}) != len(match_rows):
        raise ValidationError('Duplicate job IDs in analysis.')
    Feedback.objects.bulk_create(feedback_rows)
    JobMatch.objects.bulk_create(match_rows)
    resume.structured_data = structured_data
    resume.full_clean()
    resume.save(update_fields=['structured_data'])
    return resume
