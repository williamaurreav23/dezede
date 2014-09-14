# coding: utf-8

from __future__ import unicode_literals
from django.contrib.sites.models import Site
from django.core.cache import cache
from django.core.mail import EmailMessage
from django.http import HttpRequest
from django.template import RequestContext
from django.template.loader import render_to_string
from django.utils import translation
from django.utils.encoding import force_text
from django_rq import job
from slugify import slugify
from accounts.models import HierarchicUser
from .models import DossierDEvenements
from .utils import xelatex_to_pdf, get_user_limit_cache_key


# 18 événements : 7 secondes
# 143 événements : 9 secondes


@job
def send_pdf(dossier_pk, user_pk, site_pk, language_code):
    translation.activate(language_code)
    user = HierarchicUser.objects.get(pk=user_pk)
    dossier = DossierDEvenements.objects.get(pk=dossier_pk)
    request = HttpRequest()
    request.user = user
    context = RequestContext(
        request,
        {'object': dossier, 'user': user, 'SITE': Site.objects.get(pk=site_pk)}
    )
    tex = render_to_string('dossiers/dossierdevenements_detail.tex', context)

    body = """
    <p>Bonjour,</p>

    <p>
        Vous pouvez trouver en pièce jointe l’export du dossier Dezède « %s »
        que vous venez de demander.
    </p>

    <p>
        Bien cordialement,<br />
        L’équipe Dezède
    </p>
    """ % dossier.html()

    mail = EmailMessage('[Dezède] Export du dossier « %s »' % dossier,
                        body=body, to=(user.email,))
    mail.content_subtype = 'html'
    mail.attach('%s.pdf' % slugify(force_text(dossier)),
                xelatex_to_pdf(tex).read(), 'application/pdf')
    mail.send()

    cache.set(get_user_limit_cache_key(user), False)
