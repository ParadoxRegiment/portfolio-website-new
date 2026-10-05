from django.core import mail
from django.test import TestCase, override_settings
from django.urls import reverse


@override_settings(CONTACT_EMAIL="me@example.com")
class ContactFormTests(TestCase):
    url = reverse("pages:contact")
    valid = {
        "name": "Ada Lovelace",
        "email": "ada@example.com",
        "message": "Loved the lightning simulation!",
        "leave_empty": "",
    }

    def test_valid_message_is_emailed_to_me(self):
        response = self.client.post(self.url, self.valid, follow=True)
        self.assertRedirects(response, self.url)
        self.assertContains(response, "Your message has been sent")
        self.assertEqual(len(mail.outbox), 1)
        sent = mail.outbox[0]
        self.assertEqual(sent.to, ["me@example.com"])
        self.assertEqual(sent.reply_to, ["ada@example.com"])
        self.assertIn("Loved the lightning simulation!", sent.body)

    def test_honeypot_sends_nothing_but_looks_successful(self):
        with self.assertLogs("pages.views", level="WARNING"):
            response = self.client.post(self.url, {**self.valid, "leave_empty": "spam.biz"}, follow=True)
        self.assertContains(response, "Your message has been sent")
        self.assertEqual(len(mail.outbox), 0)

    def test_invalid_email_shows_error_and_sends_nothing(self):
        response = self.client.post(self.url, {**self.valid, "email": "not-an-email"})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Enter a valid email address")
        self.assertEqual(len(mail.outbox), 0)

    def test_newlines_in_name_cannot_break_the_subject(self):
        self.client.post(self.url, {**self.valid, "name": "Ada\r\nBcc: x@evil.com"})
        self.assertEqual(mail.outbox[0].subject, "Portfolio contact from Ada Bcc: x@evil.com")

    @override_settings(CONTACT_EMAIL="")
    def test_missing_contact_email_shows_error_instead_of_fake_success(self):
        with self.assertLogs("pages.views", level="ERROR"):
            response = self.client.post(self.url, self.valid)
        self.assertContains(response, "couldn")  # "couldn't be sent" (apostrophe is HTML-escaped)
        self.assertEqual(len(mail.outbox), 0)