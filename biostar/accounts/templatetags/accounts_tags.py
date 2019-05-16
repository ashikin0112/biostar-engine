
import logging

import hashlib
import urllib.parse

from datetime import timedelta
from django import template
from django.utils.safestring import mark_safe

from biostar.accounts.util import now
logger = logging.getLogger("engine")
register = template.Library()


@register.inclusion_tag('widgets/form_errors.html')
def form_errors(form):
    """
    Turns form errors into a data structure
    """
    try:
        errorlist = [('', message) for message in form.non_field_errors()]

        for field in form:
            for error in field.errors:
                errorlist.append((f'{field.name}:', error))
    except Exception:
        errorlist = []

    context = dict(errorlist=errorlist)

    return context


@register.inclusion_tag('widgets/pages.html')
def pages(objs, request):

    url = request.path

    return dict(objs=objs, url=url, request=request)


@register.inclusion_tag('widgets/show_messages.html')
def show_messages(messages):
    """
    Renders the messages
    """
    return dict(messages=messages)

@register.filter
def show_score_icon(user):

    color = "modcolor" if user.profile.is_moderator else ""

    if user.profile.score > 150:
        icon = f'<i class="ui bolt icon {color}"></i>'
    else:
        icon = f'<i class="ui genderless icon {color}"></i>'

    return mark_safe(icon)


@register.filter
def show_score(score):

    score = (score * 14) + 1
    return score

@register.filter
def bignum(number):
    "Reformats numbers with qualifiers as K"
    try:
        value = float(number) / 1000.0
        if value > 10:
            return "%0.fk" % value
        elif value > 1:
            return "%0.1fk" % value
    except ValueError as exc:
        pass
    return str(number)


def pluralize(value, word):
    if value > 1:
        return "%d %ss" % (value, word)
    else:
        return "%d %s" % (value, word)


@register.simple_tag
def relative_url(value, field_name, urlencode=None):
    """
    Updates field_name parameters in url with value
    """
    # Create query string with updated field_name, value pair.
    url = '?{}={}'.format(field_name, value)
    if urlencode:
        # Split query string
        querystring = urlencode.split('&')
        # Exclude old value 'field_name' from query string
        filter_func = lambda p: p.split('=')[0] != field_name
        filtered_querystring = filter(filter_func, querystring)
        # Join the filtered string
        encoded_querystring = '&'.join(filtered_querystring)
        # Update query string
        url = '{}&{}'.format(url, encoded_querystring)

    return url


@register.filter
def show_email(user):

    try:
        head, tail = user.email.split("@")
        email = head[0] + "*" * 10 + tail
    except:
        return user.email[0] + "*" * 10

    return email


@register.filter
def time_ago(date):
    if not date:
        return ''
    delta = now() - date
    if delta < timedelta(minutes=1):
        return 'just now'
    elif delta < timedelta(hours=1):
        unit = pluralize(delta.seconds // 60, "minute")
    elif delta < timedelta(days=1):
        unit = pluralize(delta.seconds // 3600, "hour")
    elif delta < timedelta(days=30):
        unit = pluralize(delta.days, "day")
    elif delta < timedelta(days=90):
        unit = pluralize(int(delta.days / 7), "week")
    elif delta < timedelta(days=730):
        unit = pluralize(int(delta.days / 30), "month")
    else:
        diff = delta.days / 365.0
        unit = '%0.1f years' % diff
    return "%s ago" % unit


@register.simple_tag
def gravatar(user, size=80):
    #name = user.profile.name
    if user.is_anonymous or user.profile.is_suspended:
        # Removes spammy images for suspended users
        email = 'suspended@biostars.org'.encode('utf8')
    else:
        email = user.email.encode('utf8')

    hash = hashlib.md5(email).hexdigest()

    gravatar_url = "https://secure.gravatar.com/avatar/%s?" % hash
    gravatar_url += urllib.parse.urlencode({
        's': str(size),
        'd': 'retro',
    }
    )
    return mark_safe(f"""<img src={gravatar_url} height={size} width={size}/>""")
