# coding: utf-8

from __future__ import unicode_literals
from django.template.defaultfilters import date
from django.utils.encoding import smart_text
from django.utils.safestring import mark_safe
from django.utils.translation import ugettext

from .text import capfirst


def date_html(d, tags=True, short=False):
    """
    Rendu HTML d’une date.

    >>> from datetime import date
    >>> print(date_html(date(1828, 1, 15)))
    mardi 15 janvier 1828
    >>> print(date_html(date(1828, 1, 1), tags=False))
    mardi 1er janvier 1828
    >>> print(date_html(date(1828, 1, 1)))
    mardi 1<sup>er</sup> janvier 1828
    >>> print(date_html(date(1828, 1, 1), tags=False, short=True))
    1er janvier 1828
    """
    pre = '' if short else date(d, 'l')
    post = date(d, 'F Y')
    j = date(d, 'j')
    if j == '1':
        k = ugettext('er')
        if tags:
            k = '<sup>%s</sup>' % k
        j += k
    return ' '.join([s for s in (pre, j, post) if s])


def html_decorator(function):
    def wrapper(txt, tags=True):
        if not txt:
            return ''
        if tags:
            return mark_safe(function(txt))
        return txt

    return wrapper


@html_decorator
def cite(txt):
    """
    >>> print(cite('Le Cid'))
    <cite>Le Cid</cite>
    >>> print(cite('The pillars of the earth', False))
    The pillars of the earth
    """
    return '<cite>' + txt + '</cite>'


def href(url, txt, tags=True, new_tab=False):
    """
    >>> print(href('truc.machin/bidule', 'Cliquez ici'))
    <a href="truc.machin/bidule">Cliquez ici</a>
    >>> print(href('/salut/toi', 'Bonjour mon gars!', new_tab=True))
    <a href="/salut/toi" target="_blank">Bonjour mon gars!</a>
    >>> print(href('a.b/c', "It's a trap!", tags=False))
    It's a trap!
    >>> href('', '')
    u''
    """
    if not txt:
        return ''
    if not tags:
        return txt
    if new_tab:
        url += '" target="_blank'
    return mark_safe(smart_text('<a href="%s">%s</a>' % (url, txt)))


@html_decorator
def sc(txt):
    """
    >>> print(sc('gentle shout'))
    <span class="sc">gentle shout</span>
    >>> print(sc('I wish I could be in small caps', tags=False))
    I wish I could be in small caps
    """
    return '<span class="sc">' + txt + '</span>'


def hlp(txt, title, tags=True):
    """
    >>> print(hlp('two years', 'period'))
    <span title="Period">two years</span>
    >>> print(hlp('G minor', 'tonality', tags=False))
    G minor
    >>> hlp('', '')
    u''
    """
    if not txt:
        return ''
    if tags:
        return mark_safe('<span title="%s">%s</span>' % (capfirst(title),
                                                         txt))
    return txt


def microdata(txt, itemprop, itemtype=None, itemscope=False, tags=True):
    if not txt:
        return ''
    if not tags:
        return txt
    additional = ''
    if itemscope:
        additional += ' itemscope'
    if itemtype:
        additional += ' itemtype="http://data-vocabulary.org/%s"' % itemtype
    return mark_safe('<span itemprop="%s"%s>%s</span>'
                     % (itemprop, additional, txt))


@html_decorator
def small(txt):
    """
    >>> print(small('I feel tiny'))
    <small>I feel tiny</small>
    >>> print(small('In a website I would be small...', tags=False))
    In a website I would be small...
    """
    return '<small>' + txt + '</small>'


@html_decorator
def strong(txt):
    """
    >>> print(strong('I are STROOoOONG!!!'))
    <strong>I are STROOoOONG!!!</strong>
    """
    return '<strong>' + txt + '</strong>'


@html_decorator
def em(txt):
    """
    >>> print('en ' + em('do') + ' mineur')
    en <em>do</em> mineur
    """
    return '<em>' + txt + '</em>'