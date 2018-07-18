# doT to Jinja2 template conversion

This code converts a [https://github.com/olado/doT](doT) template into
[http://jinja.pocoo.org/](Jinja2) format.  This can be done as a once-off
conversion if you're changing templating technologies, or on the fly if
you're trying for compatibility.

# Why?

There are two main problems with doT:

1. It's mainly written in Javascript.  There is a
   [https://github.com/lucemia/doT](Python) code repository that does the same
   basic doT interpretation and should produce the same output, but it does
   not have broad cross-language support.

2. It produces not raw text, but a Javascript function that takes the data
   to interpolate as an argument.  This means you either need to exec the code
   in Javascript or run it in a browser in order to see the post-template
   output.  So you'd better hope that there's no javascript hiding in that
   input anywhere...

Jinja2 is written in Python, and it produces pure post-template output.  This
not only makes it more suitable for producing output for other non-Javascript
media such as emails or other document forms, but makes it much safer for
interpreting data which may come from untrusted sources.

# Abilities

* Conversion of doT interpolation, if/then/else conditions, simple for loops
  and Javascript for loops.
* Conversion of `Object.keys(thing).length` into `thing|length` Jinja2 syntax.

# Deficiencies

* It does not attempt to interpret the Javascript syntax of some expressions.
  In particular, Javascript allows space between an object and its property
  - e.g. `object   .property` - this is not removed in this conversion.
  Likewise, expressions that involve Javascript evaluation are not converted.

