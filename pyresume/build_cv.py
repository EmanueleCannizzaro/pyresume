import os
import sys
import argparse

import yaml
import jinja2

sys.path.append(os.path.dirname(os.path.realpath(__file__)))
import filters


class BuildCV(object):
    """
    Build markdown and tex files of CV from YAML using jinja templates
    """

    def __init__(self, yaml_config_file, filters=None, templates=None):
        self.filters = filters
        with open(yaml_config_file, 'r') as f:
            self.data = yaml.load(f)
        templates = {} if templates is None else templates
        self.loader = jinja2.loaders.DictLoader(templates)

    @property
    def jenv(self,):
        """
        Set up markdown/HTML environment
        """
        loader = jinja2.loaders.ChoiceLoader([
            self.loader,
            jinja2.FileSystemLoader(
                os.path.join(os.path.dirname(os.path.realpath(__file__)), 'templates'))
        ])
        jenv = jinja2.Environment(loader=loader)
        for f in self.filters:
            jenv.filters[f.__name__] = f
        return jenv

    @property
    def jenv_tex(self,):
        """
        Set up TeX environment
        """
        loader = jinja2.ChoiceLoader([
            self.loader,
            jinja2.FileSystemLoader(
                os.path.join(os.path.dirname(os.path.realpath(__file__)), 'templates'))
        ])
        jenv = jinja2.Environment(loader=loader)
        # define new delimiters to avoid TeX conflicts
        jenv.block_start_string = '((*'
        jenv.block_end_string = '*))'
        jenv.variable_start_string = '((('
        jenv.variable_end_string = ')))'
        jenv.comment_start_string = '((='
        jenv.comment_end_string = '=))'
        for f in self.filters:
            jenv.filters[f.__name__] = f
        return jenv

    def tex_cv(self, **kwargs):
        return self.jenv_tex.get_template("cv.tex").render(
            data=self.data, **kwargs)

    def tex_short_cv(self, **kwargs):
        return self.jenv_tex.get_template("cv-short.tex").render(
            data=self.data, **kwargs)

    def markdown_cv(self, pdf_link=None):
        return self.jenv.get_template("cv.md").render(
            data=self.data, pdf_link=pdf_link)

    def html_cv(self, pdf_link=None):
        return self.jenv.get_template("cv.html").render(
            data=self.data, pdf_link=pdf_link)


if __name__ == '__main__':
    # parse command line arguments
    parser = argparse.ArgumentParser(description='Build TeX and Markdown versions of your CV')
    cur_dir = os.path.dirname(os.path.realpath(__file__))
    parser.add_argument("--cv_data", help="YAML config file containing all CV data",
                        default=os.path.join(cur_dir, 'cv_data.yml'))
    parser.add_argument("--md_out_file", help="where to write markdown version of CV")
    parser.add_argument("--html_out_file", help="where to write HTML version of CV")
    parser.add_argument("--tex_out_file", help="where to write TeX version of CV")
    parser.add_argument("--tex_short_out_file", help="where to write short TeX version of CV")
    parser.add_argument("--pdf_link", help="where to link to PDF version of CV")
    args = parser.parse_args()
    # build cv
    filters = [filters.escape_tex,
               filters.tex_section_sorter,
               filters.tex_pub_sorter,
               filters.md_section_sorter,
               filters.html_section_sorter,
               filters.shorten_list,
               filters.select_by_attr_name,
               filters.to_cvlist,
               filters.author_filter,
               filters.doi_to_url,
               filters.date_filter,
               filters.date_range_filter]
    cv = BuildCV(args.cv_data, filters=filters)
    if args.tex_out_file is not None:
        with open(args.tex_out_file, 'w') as f:
            f.write(cv.tex_cv())
    if args.tex_short_out_file is not None:
        with open(args.tex_short_out_file, 'w') as f:
            f.write(cv.tex_short_cv())
    if args.md_out_file is not None:
        with open(args.md_out_file, 'w') as f:
            f.write(cv.markdown_cv(pdf_link=args.pdf_link))
    if args.html_out_file is not None:
        with open(args.html_out_file, 'w') as f:
            f.write(cv.html_cv(pdf_link=args.pdf_link))
