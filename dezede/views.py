# coding: utf-8

from __future__ import unicode_literals
import json
from django.db.models import Q
from django.http import HttpResponse
from django.utils.encoding import smart_text
from django.views.generic import ListView, TemplateView
from haystack.views import SearchView
from libretto.models import Oeuvre, Lieu, Individu
from libretto.search_indexes import autocomplete_search
from typography.utils import replace
from .models import Diapositive


class HomeView(ListView):
    model = Diapositive
    template_name = 'home.html'

    def get_queryset(self):
        qs = super(HomeView, self).get_queryset()
        return qs.published(self.request)


# TODO: Use the search engine filters to do this
def clean_query(q):
    return (q.lower().replace('(', '').replace(')', '').replace(',', '')
            .replace('-', ' '))


class CustomSearchView(SearchView):
    """
    Custom SearchView to fix spelling suggestions.
    """

    def build_form(self, form_kwargs=None):
        self.request.GET = GET = self.request.GET.copy()
        GET['q'] = replace(GET.get('q', ''))
        return super(CustomSearchView, self).build_form(form_kwargs)

    def extra_context(self):
        context = {'suggestion': None}

        if self.results.query.backend.include_spelling:
            q = self.query or ''
            suggestion = self.form.searchqueryset.spelling_suggestion(q)
            if clean_query(suggestion) != clean_query(q):
                context['suggestion'] = suggestion

        return context

    def get_results(self):
        sqs = super(CustomSearchView, self).get_results()
        user = self.request.user
        filters = Q(public=True)
        if user is not None:
            filters |= Q(owner=user)
        return sqs.filter(filters)


def autocomplete(request):
    q = request.GET.get('q', '')
    suggestions = autocomplete_search(request, q)
    suggestions = [{'value': (s.related_label() if hasattr(s, 'related_label')
                              else smart_text(s)),
                    'url': s.get_absolute_url()} for s in suggestions]
    data = json.dumps(suggestions)
    return HttpResponse(data, content_type='application/json')


class ErrorView(TemplateView):
    status = 200

    def render_to_response(self, context, **response_kwargs):
        response_kwargs['status'] = self.status
        self.template_name = '%s.html' % self.status
        return super(ErrorView, self).render_to_response(context,
                                                         **response_kwargs)


class BibliographieView(TemplateView):
    template_name = 'pages/bibliographie.html'

    def get_context_data(self, **kwargs):
        context = super(BibliographieView, self).get_context_data(**kwargs)
        context.update(
            oeuvres=Oeuvre.objects.all(),
            individus=Individu.objects.all(),
            lieux=Lieu.objects.all(),
        )
        return context
