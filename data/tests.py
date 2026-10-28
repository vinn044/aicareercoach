"""Integration checks for auth, ownership, CSRF, CRUD, and analysis boundaries."""
from datetime import timedelta
from unittest.mock import patch
from django.core.exceptions import ValidationError
from django.db import IntegrityError, transaction
from django.test import Client, TestCase
from django.urls import reverse
from .models import AuthQuota, Feedback, JobMatch, Resume, User
from .services import StaleAnalysis, store_analysis

class BackendTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='alice', email='alice@example.com', password='Strong-demo!374')
        self.other = User.objects.create_user(username='bob', email='bob@example.com', password='Strong-demo!375')
        self.resume = Resume.objects.create(owner=self.user, title='Engineering Resume', text='Education\nExample University', major='Engineering', minor='Math')
        self.client.force_login(self.user)
    def payload(self, **changes):
        payload = dict(owner=self.user, resume_id=self.resume.pk, expected_updated_at=self.resume.updated_at,
            structured_data={'education': [{'major': 'Engineering', 'minor': 'Math'}]},
            feedback=[{'kind': 'consistency', 'message': 'Check dates', 'evidence': '2029–2025', 'suggestion': 'Confirm dates'}],
            matches=[{'external_id': 'job-1', 'title': 'Engineer', 'company': 'Example', 'url': 'https://example.com/jobs/1', 'score': 0.7}])
        payload.update(changes)
        return payload
    def test_registration_login_logout_password_hash(self):
        c = Client()
        r = c.post(reverse('register'), {'username': 'newstudent', 'email': 'NEW@EXAMPLE.COM', 'password1': 'Distinct-pass!3749', 'password2': 'Distinct-pass!3749'})
        self.assertRedirects(r, reverse('home'))
        user = User.objects.get(username='newstudent')
        self.assertEqual(user.email, 'new@example.com')
        self.assertNotEqual(user.password, 'Distinct-pass!3749')
        self.assertTrue(user.check_password('Distinct-pass!3749'))
        self.assertEqual(c.get(reverse('logout')).status_code, 405)
        self.assertRedirects(c.post(reverse('logout')), reverse('logged_out'))
        self.assertNotIn('_auth_user_id', c.session)
        self.assertRedirects(c.post(reverse('login'), {'username': 'newstudent', 'password': 'Distinct-pass!3749'}), reverse('home'))
    def test_email_uniqueness_and_invalid_registration(self):
        c = Client()
        r = c.post(reverse('register'), {'username': 'newstudent', 'email': 'ALICE@EXAMPLE.COM', 'password1': 'Distinct-pass!3749', 'password2': 'Distinct-pass!3749'})
        self.assertContains(r, 'Unable to use this email')
        with self.assertRaises(IntegrityError), transaction.atomic():
            User.objects.create_user(username='duplicate', email='ALICE@EXAMPLE.COM')
        r = c.post(reverse('register'), {'username': 'weak', 'email': 'invalid', 'password1': '123', 'password2': '123'})
        self.assertTrue(r.context['form'].errors)
        self.assertFalse(User.objects.filter(username='weak').exists())
    def test_anonymous_protection_and_open_redirect(self):
        c = Client()
        for name in ['resume_list', 'profile', 'job_matches', 'resume_create']:
            self.assertEqual(c.get(reverse(name)).status_code, 302)
        r = c.post(reverse('login') + '?next=https://evil.example/', {'username': 'alice', 'password': 'Strong-demo!374'})
        self.assertEqual(r.url, reverse('home'))
    def test_templates_render_and_real_navigation(self):
        urls = [reverse('home'), reverse('profile'), reverse('resume_list'), reverse('resume_create'), reverse('job_matches')]
        urls += [reverse(n, args=[self.resume.pk]) for n in ['resume_detail', 'resume_edit', 'resume_delete']]
        for url in urls:
            with self.subTest(url=url):
                r = self.client.get(url)
                self.assertEqual(r.status_code, 200)
                self.assertNotContains(r, 'href="#"')
        for name in ['login', 'register', 'logged_out']: self.assertEqual(Client().get(reverse(name)).status_code, 200)
    def test_crud_and_owner_injection(self):
        r = self.client.post(reverse('resume_create'), {'title': 'New', 'text': 'Body', 'major': 'CS', 'minor': 'Art', 'owner': self.other.pk})
        created = Resume.objects.get(title='New')
        self.assertEqual(created.owner, self.user)
        self.assertRedirects(r, created.get_absolute_url())
        self.client.post(reverse('resume_edit', args=[created.pk]), {'title': 'Edited', 'text': 'Changed', 'major': 'CS', 'minor': 'Math'})
        created.refresh_from_db()
        self.assertEqual(created.minor, 'Math')
        self.client.get(reverse('resume_delete', args=[created.pk]))
        self.assertTrue(Resume.objects.filter(pk=created.pk).exists())
        self.assertRedirects(self.client.post(reverse('resume_delete', args=[created.pk])), reverse('resume_list'))
        self.assertFalse(Resume.objects.filter(pk=created.pk).exists())
    def test_other_user_cannot_read_update_delete_or_review(self):
        item = Feedback.objects.create(resume=self.resume, kind='grammar', message='Test')
        self.client.force_login(self.other)
        for name in ['resume_detail', 'resume_edit', 'resume_delete']:
            for method in ['get', 'post']:
                with self.subTest(name=name, method=method):
                    expected = 405 if name == 'resume_detail' and method == 'post' else 404
                    self.assertEqual(getattr(self.client, method)(reverse(name, args=[self.resume.pk])).status_code, expected)
        self.assertNotContains(self.client.get(reverse('resume_list')), 'Engineering Resume')
        self.assertEqual(self.client.post(reverse('feedback_status', args=[item.pk]), {'status': 'resolved'}).status_code, 404)
        self.resume.refresh_from_db()
        self.assertEqual(self.resume.title, 'Engineering Resume')
    def test_csrf_enforced(self):
        c = Client(enforce_csrf_checks=True)
        c.force_login(self.user)
        for name in ['resume_create', 'register', 'login', 'logout']:
            self.assertEqual(c.post(reverse(name)).status_code, 403)
        self.assertEqual(c.post(reverse('resume_delete', args=[self.resume.pk])).status_code, 403)
    def test_resume_text_escaped(self):
        self.resume.text = '<script>alert(1)</script>'
        self.resume.save()
        r = self.client.get(self.resume.get_absolute_url())
        self.assertContains(r, '&lt;script&gt;alert(1)&lt;/script&gt;')
        self.assertNotContains(r, '<script>alert(1)</script>')
    def test_analysis_storage_and_feedback_states(self):
        store_analysis(**self.payload())
        self.resume.refresh_from_db()
        self.assertEqual(self.resume.structured_data['education'][0]['minor'], 'Math')
        self.assertEqual(self.resume.matches.count(), 1)
        item = self.resume.feedback.get()
        self.assertEqual(self.client.get(reverse('feedback_status', args=[item.pk])).status_code, 405)
        self.assertEqual(self.client.post(reverse('feedback_status', args=[item.pk]), {'status': 'invalid'}).status_code, 400)
        self.assertRedirects(self.client.post(reverse('feedback_status', args=[item.pk]), {'status': 'dismissed'}), self.resume.get_absolute_url())
        item.refresh_from_db()
        self.assertEqual(item.status, 'dismissed')
        self.assertContains(self.client.get(reverse('job_matches')), 'Engineer')
    def test_analysis_owner_boundary_and_stale_results(self):
        with self.assertRaises(Resume.DoesNotExist): store_analysis(**self.payload(owner=self.other))
        with self.assertRaises(StaleAnalysis): store_analysis(**self.payload(expected_updated_at=self.resume.updated_at + timedelta(seconds=1)))
        self.assertEqual(self.resume.matches.count(), 0)
    def test_invalid_analysis_rolls_back(self):
        store_analysis(**self.payload())
        for changes in [{'score': 2}, {'url': 'javascript:alert(1)'}, {'score': float('nan')}, {'url': 'ftp://example.com/jobs'}]:
            with self.subTest(changes=changes), self.assertRaises(ValidationError):
                store_analysis(**self.payload(matches=[dict(self.payload()['matches'][0], **changes)]))
        with self.assertRaises(ValidationError): store_analysis(**self.payload(feedback=[{'kind': 'grammar', 'message': 'test', 'status': 'resolved'}]))
        with self.assertRaises(ValidationError): store_analysis(**self.payload(matches=[self.payload()['matches'][0]] * 2))
        self.assertEqual(self.resume.matches.get().score, 0.7)
        self.assertEqual(self.resume.feedback.count(), 1)
    def test_edit_invalidates_and_delete_cascades(self):
        store_analysis(**self.payload())
        self.client.post(reverse('resume_edit', args=[self.resume.pk]), {'title': self.resume.title, 'text': 'Different', 'major': 'Engineering', 'minor': 'Math'})
        self.resume.refresh_from_db()
        self.assertEqual(self.resume.structured_data, {})
        self.assertEqual(self.resume.matches.count(), 0)
        self.assertEqual(self.resume.feedback.count(), 0)
        store_analysis(**self.payload())
        self.client.post(reverse('resume_delete', args=[self.resume.pk]))
        self.assertFalse(Feedback.objects.exists())
        self.assertFalse(JobMatch.objects.exists())
    def test_rate_limits_and_expiry(self):
        c = Client()
        with patch('data.middleware.time.time', return_value=3600):
            for _ in range(10): self.assertEqual(c.post(reverse('login'), {}).status_code, 200)
            r = c.post(reverse('login'), {})
            self.assertEqual(r.status_code, 429)
            self.assertEqual(r['Retry-After'], '60')
            for _ in range(5): self.assertEqual(c.post(reverse('register'), {}).status_code, 200)
            self.assertEqual(c.post(reverse('register'), {}).status_code, 429)
        with patch('data.middleware.time.time', return_value=7200):
            self.assertEqual(c.post(reverse('register'), {}).status_code, 200)
            self.assertEqual(c.post(reverse('login'), {}).status_code, 200)
        self.assertTrue(AuthQuota.objects.exists())
