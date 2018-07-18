from django.test import TestCase

from api.utils import patterns, dot_to_jinja

import re

test_cases = [
    # Substitution
    {
        'dot': '{{=foo}}',
        'jinja2': '{{ foo }}',
    },
    {
        'dot': '{{=pydata.foo }}',
        'jinja2': '{{ pydata.foo }}',
    },
    {
        'dot': '{{=pydata.msg[idx]}}',
        'jinja2': '{{ pydata.msg[idx] }}',
    },

    # Conditions
    {
        'dot': '{{?foo}}bar{{?}}',
        'jinja2': '{% if foo %}bar{% endif %}',
    },
    {
        'dot': '{{?foo}}{{=foo}}{{?}}',
        'jinja2': '{% if foo %}{{ foo }}{% endif %}',
    },
    {
        'dot': '{{?foo}}bar{{??}}baz{{?}}',
        'jinja2': '{% if foo %}bar{% else %}baz{% endif %}',
    },
    {
        'dot': '{{?pydata.rhel_release == "6.5"}}RHEL 6.5{{?}}',
        'jinja2': '{% if pydata.rhel_release == "6.5" %}RHEL 6.5{% endif %}',
    },
    {
        'dot': '{{? pydata.kvr.indexOf("el7") != -1 }}Not RHEL 7{{?}}',
        'jinja2': '{% if pydata.kvr.indexOf("el7") != -1 %}Not RHEL 7{% endif %}',
    },
    {
        'dot': 'Upgrade `kernel` to {{?pydata.kvr.indexOf("el7") != -1}}**3.10.0-514.el7**{{?}}{{?pydata.kvr.indexOf("el6") != -1}}**2.6.32-696.el6**{{?}} or later.',
        'jinja2': 'Upgrade `kernel` to {% if pydata.kvr.indexOf("el7") != -1 %}**3.10.0-514.el7**{% endif %}{% if pydata.kvr.indexOf("el6") != -1 %}**2.6.32-696.el6**{% endif %} or later.',
    },

    {
        'dot': '''
{{?foo}}
bar
{{?}}''',
        'jinja2': '''
{% if foo %}
bar
{% endif %}''',
    }, {
        'dot': '''
{{?foo}}
bar
{{??}}
baz
{{?}}''',
        'jinja2': '''
{% if foo %}
bar
{% else %}
baz
{% endif %}''',
    }, {
        'dot': '''
{{?foo}}
bar
{{??}}{{? fred == barney }}
baz
{{?}}
{{?}}''',
        'jinja2': '''
{% if foo %}
bar
{% else %}{% if fred == barney %}
baz
{% endif %}
{% endif %}''',
    }, {
        'dot': '''
{{?foo}}
{{? bar }}{{ bar }}{{??}}no bar{{?}}
{{??}}
baz
{{?}}''',
        'jinja2': '''
{% if foo %}
{% if bar %}{{ bar }}{% else %}no bar{% endif %}
{% else %}
baz
{% endif %}''',
    },

    # DoT-style Iteration
    {
        'dot': '{{~foos:foo}}{{=foo}}{{~}}',
        'jinja2': '{% for foo in foos %}{{ foo }}{% endfor %}',
    },
    {
        'dot': '{{~pydata.missing_kernels:kernel}}{{=kernel}}{{~}}',
        'jinja2': '{% for kernel in pydata.missing_kernels %}{{ kernel }}{% endfor %}',
    },
    {
        'dot': '{{~ pydata.files :value:index}}{{=index}} -> {{=value}}{{~}}',
        'jinja2': '{% for value in pydata.files %}{{ loop.index }} -> {{ value }}{% endfor %}',
    },

    # Javascript-style Iteration
    {
        'dot': '{{ for (var foo in foos) { }}{{=foo}}{{ } }}',
        'jinja2': '{% for foo in foos %}{{ foo }}{% endfor %}',
    },
    {
        'dot': '{{ for ( var key in pydata.files[idx]){}}{{=key}}{{}}}',
        'jinja2': '{% for key in pydata.files[idx] %}{{ key }}{% endfor %}',
    },
    {
        'dot': '{{ for (key in pydata.result.untuned) {}}{{=key}} = {{=pydata.result.untuned[key]}}{{ }}}',
        'jinja2': '{% for key in pydata.result.untuned %}{{ key }} = {{ pydata.result.untuned[key] }}{% endfor %}',
    },
    {
        'dot': '{{ for(var rpm in pydata.bad_rpms) { }}',
        'jinja2': '{% for rpm in pydata.bad_rpms %}',
    },
    {
        'dot': '{{ for( var key in pydata.current_osd_mof) {}}',
        'jinja2': '{% for key in pydata.current_osd_mof %}',
    },
    # { - we don't yet remove spaces from between an object and its property.
    #     'dot': '{{ for (var property in pydata. not_reboot_checking_error_fstab_entries_not_in_dev) { }}',
    #     'jinja2': '{% for key in pydata.not_reboot_checking_error_fstab_entries_not_in_dev %}',
    # },
]


class Dot2Jinja2Tests(TestCase):
    def test_regexes_compile(self):
        for name, patdata in patterns.items():
            try:
                re.compile(r'\{\{' + patdata['search'] + r'\}\}')
            except Exception as e:
                self.fail("{n} failed to compile {x}: {e}".format(
                    n=name, x=patdata['search'], e=e

    def test_cases(self):
        for test in test_cases:
            conv = dot_to_jinja(test['dot'])
            self.assertEqual(conv, test['jinja2'], 'conversion of ' + test['dot'] + ' failed')

    def test_jinja2_remains_unconverted(self):
        for test in test_cases:
            conv = dot_to_jinja(test['jinja2'])
            self.assertEqual(conv, test['jinja2'], test['jinja2'] + ' changed from jinja2')
