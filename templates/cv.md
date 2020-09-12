<!-------------------------------------------------------------------------------------------->
<!--                                          Education                                     -->
<!-------------------------------------------------------------------------------------------->
{% set sect = data.sections | select_by_attr_name("title","Education") %}
## {{ sect.title }}
<div class="lead">
{% for i in sect.entries %}
* **{{ i.degree }}**, {{ i.dates | date_range_filter }} / {{i.school}} / {{i.location}}
{% endfor %}
</div>
<!-------------------------------------------------------------------------------------------->
<!--                                          Software and Computing                        -->
<!-------------------------------------------------------------------------------------------->
{% set  sect = data.sections | select_by_attr_name("title", "Software and Computing Skills") %}
## {{ sect.title }}
<div class="lead">
{% for i in sect.entries %}
* **{{ i.name }}** {{ i.value }}
{% endfor %}
</div>
<!-------------------------------------------------------------------------------------------->
<!--                                          Publications                                  -->
<!-------------------------------------------------------------------------------------------->
{% set  sect = data.sections | select_by_attr_name("title", "Papers") %}
## {{ sect.title }}
{% for i in sect.entries %}
### {{ i.title }}
<div class="lead">
{% for j in i.entries %}
* *{{ j.title }}* / {{ j.authors | author_filter }} / {{ j.journal }} / {{ j.year }}
{% endfor %}
</div>
{% endfor %}
<!-------------------------------------------------------------------------------------------->
<!--                                          Presentations                                 -->
<!-------------------------------------------------------------------------------------------->
{% set sect = data.sections | select_by_attr_name("title", "Presentations") %}
{% for i in sect.entries%}
## {{ i.title }}
<div class="lead">
{% for j in i.entries %}
* *{{ j.title }}* / {{ j.event }} / {{ j.dates | date_range_filter}} / {{ j.location }}
{% endfor %}
</div>
{% endfor %}

{% if pdf_link %}
<div class="lead text-center">
A complete version of my CV can be found [here]({{ pdf_link }})
</div>
{% endif %}
