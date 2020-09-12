"""
Filters for printing TeX to jinja templates.
See http://flask.pocoo.org/snippets/55/ for more info.
"""
import re
import logging
import calendar


LATEX_SUBS = (
    (re.compile(r'\\'), r'\\textbackslash'),
    (re.compile(r'([{}_#%&$])'), r'\\\1'),
    (re.compile(r'~'), r'\~{}'),
    (re.compile(r'\^'), r'\^{}'),
    (re.compile(r'"'), r"''"),
    (re.compile(r'\.\.\.+'), r'\\ldots'),
)


def escape_tex(value):
    """
    Escape TeX special characters
    """
    newval = value
    for pattern, replacement in LATEX_SUBS:
        newval = pattern.sub(replacement, newval)
    return newval


def tex_section_sorter(section, title, index):
    """Change format based on section. Customized for my specific setup"""
    cv_listitem_format = '\cvlistitem{{{}}}'
    if title == 'Education':
        return_list =  [section['dates'], section['degree'], section['school'], section['location'], section['gpa'] if section['gpa'] else '', '']
        if section['cvlistitems']:
            return_list[-1] = '\n'.join([cv_listitem_format.format(i) for i in section['cvlistitems']])
    elif title == 'Talks' or title == 'Conference Papers and Posters':
        return_list = [section['dates'], section['institution'], section['event'], section['location'], '', f'\\textit{{{section["title"]}}}']
        if section['url']:
            return_list[-1] = f'\href{{{section["url"]}}}{{\\textit{{{section["title"]}}}}}'
    elif title == 'Research Experience':
        return_list = [section['dates'], section['title'], section['institution'], section['location'], '', section['description']]
    elif title == 'Teaching Experience':
        return_list = [section['dates'], section['title'], section['class'], '', '', section['description']]
    elif title == 'Societies and Associations' or title=='Employment Experience':
        return_list = [section['dates'], section['title'], section['org'], '', '', section['description']]
    else:
        logging.error('Unrecognized title: %s'%(title))

    return return_list[index]


def tex_pub_sorter(entry):
    """Format publication list item"""
    if entry['doi'] and entry['url']:
        return '%s, \\textit{%s}, %s, %s, \href{%s}{%s}'%(author_filter(entry['authors'], tex=True),
                                                          entry['title'], entry['journal'],
                                                          entry['year'], entry['url'], entry['doi'])
    else:
        return '%s, \\textit{%s}, %s, %s'%(author_filter(entry['authors'], tex=True), entry['title'],
                                           entry['journal'], entry['year'])


def md_section_sorter(entry, title):
    """Format markdown sections for different types"""
    if title == 'Education':
        return_str = '%s, %s / %s '%(entry['degree'], entry['dates'], entry['school'])
        if entry['cvlistitems']:
            return_str += ' / ' + ' / '.join([item for item in entry['cvlistitems']])
    elif title == 'Talks' or title == 'Conference Papers and Posters':
        if entry['url']:
            return_str = f'[*{entry["title"]}*]({entry["url"]}) / {entry["event"]} / {entry["institution"]} / {entry["location"]} / {entry["dates"]}'
        else:
            return_str = f'*{entry["title"]}* / {entry["event"]} / {entry["institution"]} / {entry["location"]} / {entry["dates"]}'
    elif title == 'Publications':
        return_str = '%s, *%s*, %s, %s'%(entry['authors'], entry['title'], entry['journal'], entry['year'])
        if entry['url'] and entry['doi']:
            return_str += ', [%s](%s)'%(entry['doi'],entry['url'])
    else:
        logging.error('Unrecognized title: %s'%(title))

    return return_str


def html_section_sorter(entry, title):
    """
    Format HTML sections for different types
    """
    if title == 'Education':
        return_str = '<strong>{}</strong> {}<span class="pull-right">{}, <em>{}</em></span>'.format(entry['school'], entry['location'], entry['degree'], entry['dates'])
    elif title == 'Talks':
        if entry['url']:
            pub_title = '<a href="{}"><em>{}</em></a>'.format(entry['url'], entry['title'])
        else:
            pub_title = '<em>{}</em>'.format(entry['title'])
        return_str = '{} <span class="pull-right">{}</span><br>{}, {}'.format(pub_title, entry['dates'], entry['event'], entry['location'])
    elif title == 'Publications':
        return_str = '<em>{}</em><br>{}, {} {}'.format(entry['title'],
                                                       author_filter(entry['authors']),
                                                       entry['journal'], entry['year'])
        if entry['url'] and entry['doi']:
            return_str += ', <a href="{}"><em>{}</em></a>'.format(entry['url'], entry['doi'])
    else:
        logging.error('Unrecognized title: {}'.format(title))

    return return_str


def author_filter(authors, tex=False):
    """
    Filter author list
    """
    my_names = ['W. T. Barnes', 'Will T. Barnes']
    bold = '\\underline{{{}}}' if tex else '<strong>{}</strong>'
    return ', '.join([bold.format(a) if a in my_names else a for a in authors])


def shorten_list(array, max_length):
    return array[:max_length]


def select_by_attr_name(array, attr, value):
    for d in array:
        if d[attr] == value:
            return d


def to_cvlist(array):
    return '\n'.join([f'\cvlistitem{{{i}}}' for i in array]) if array is not None else ''


def doi_to_url(value, doi, bibcode, link_format='html'):
    if not doi and not bibcode:
        return value
    link = f'https://doi.org/{doi}' if doi else f'http://adsabs.harvard.edu/abs/{bibcode}'
    if link_format == 'html':
        return f'< a href={link}>{value}</a>'
    elif link_format == 'markdown':
        return f'[{value}]({link})'
    elif link_format == 'tex':
        return f'\href{{{link}}}{{{value}}}'
    else:
        raise NotImplementedError(f'{link_format} links not implemented')


def date_filter(date, format='full', drop_present=False):
    if date == 'present':
        return 'present' if not drop_present else ''
    # Sometimes we just want to return a string (or int)
    if type(date) is not dict:
        return date
    day = date.get('day', None)
    month = date.get('month', None)
    year = date.get('year', None)
    # Format month and year appropriately
    if format == 'full' and month is not None:
        month = f'{calendar.month_name[month]}'
    elif format == 'abbreviated' and month is not None:
        month = f'{calendar.month_abbr[month]}'
    if format == 'numerical_short_year' and year is not None:
        year = f'{str(year)[2:]}'
    if format == 'full' or format == 'abbreviated':
        return ' '.join([f'{i}' for i in (day, month, year) if i is not None])
    elif format == 'numerical' or format == 'numerical_short_year':
        return '/'.join([f'{i}' for i in (day, month, year) if i is not None])
    else:
        raise ValueError('Invalid format')


def date_range_filter(dates, format='full', drop_present=False):
    if type(dates) is not dict or ('start' not in dates and 'end' not in dates):
        return date_filter(dates, format=format, drop_present=drop_present)
    else:
        start = dates['start']
        end = dates['end']
        # Remove redundant entries if possible
        if type(start) is dict and type(end) is dict:
            if start['year'] == end['year']:
                del start['year']
                if start['month'] == end['month']:
                    del start['month']
        start = date_filter(start, format=format, drop_present=drop_present)
        end = date_filter(end, format=format, drop_present=drop_present)
        return f'{start} -- {end}'
