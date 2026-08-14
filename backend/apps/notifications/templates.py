from django.template import Template, Context

# Class: TemplateRenderer
class TemplateRenderer:
    @staticmethod
    # Method: render
    def render(template_string: str, variables: dict) -> str:
        """
        Renders a string template using Django's template engine.
        """
        django_template = Template(template_string)
        context = Context(variables)
        return django_template.render(context)
