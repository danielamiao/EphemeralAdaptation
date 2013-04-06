from django import template
from django.core.serializers import serialize
from django.db.models.query import QuerySet
from django.utils import simplejson

register = template.Library()

def calculate_id(outerloop, innerloop):
    return int(outerloop)*4 + int(innerloop);

register.filter('calculate_id', calculate_id)

def jsonify(arg):
    if isinstance(arg, QuerySet):
        return serialize('json', arg)
    return simplejson.dumps(arg)

register.filter('jsonify', jsonify)