import logging
from smtplib import SMTPException

from django.conf import settings
from django.contrib import messages
from django.core.mail import EmailMessage
from django.shortcuts import render, redirect
from django.db.models import Count, Q
from django.core.exceptions import ImproperlyConfigured

from projects.models import Category, Project

from .forms import ContactForm

logger = logging.getLogger(__name__)

def home(request):
    featured = (
        Project.objects.published()
        .filter(featured=True)
        .select_related("category")
        .prefetch_related("tags")[:3]
    )
    categories = Category.objects.annotate(
        num_projects=Count("projects", filter=Q(projects__is_published=True))
    ).filter(num_projects__gt=0)
    
    return render(
        request,
        "pages/home.html",
        {"featured": featured, "categories": categories},
    )

def contact(request):
    if request.method == "POST":
        form = ContactForm(request.POST)
        if form.is_valid():
            if form.is_spam():
                logger.warning("Contact form honeypot triggered; message discarded")
                messages.success(request, "Thanks! Your message has been sent.")
                return redirect("pages:contact")
            try:
                send_contact_email(form.cleaned_data)
            except (SMTPException, OSError, ImproperlyConfigured):
                logger.exception("Contact form email failed")
                messages.error(
                    request,
                    "Sorry, your message couldn't be sent right now. "
                    "Please try again later, or reach me through the links above.",
                )
            else:
                messages.success(request, "Thanks! Your message has been sent.")
                return redirect("pages:contact")
    else:
        form = ContactForm()
            
    return render(request, "pages/contact.html", {"form": form})

def send_contact_email(data: dict) -> None:
    if not settings.CONTACT_EMAIL:
        raise ImproperlyConfigured("CONTACT_EMAIL is not set")
    
    name = " ".join(data["name"].split())
    EmailMessage(
        subject=f"Portfolio contact from {name}",
        body=f"From: {name} <{data['email']}>\n\n{data['message']}",
        to=[settings.CONTACT_EMAIL],
        reply_to=[data["email"]],
    ).send()
