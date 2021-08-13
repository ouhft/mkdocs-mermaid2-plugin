"""
Main plugin module for mermaid2
"""

from mkdocs.plugins import BasePlugin
from mkdocs.config.config_options import Type as PluginType
from bs4 import BeautifulSoup

from . import pyjs
from .util import info

# ------------------------
# Constants and utilities
# ------------------------
# the mermaid lib currently built into the latest theme package
MERMAID_LIB_VERSION = "8.11.4"

# ------------------------
# Plugin
# ------------------------
class MarkdownMermaidPlugin(BasePlugin):
    """
    Plugin for interpreting Mermaid code.

    This is based on `pymdownx.superfences.fence_code_format` being used for the custom class for mermaid content.
    """
    # Avoid using fence_div_format as a shortcut because it strips out the line returns and generates invalid Mermaid code

    config_scheme = (
        ("version", PluginType(str, default=MERMAID_LIB_VERSION)),
        ("arguments", PluginType(dict, default={})),
        # ('custom_loader', PluginType(bool, default=False))
    )

    # ------------------------
    # Properties
    # Do not call them before on_config was run!
    # ------------------------
    @property
    def full_config(self):
        """
        The full plugin's configuration object, which also includes the contents of the yaml config file.
        """
        return self._full_config

    @property
    def mermaid_args(self):
        """
        The arguments for mermaid.
        """
        return self._mermaid_args


    # ------------------------
    # Event handlers
    # ------------------------
    def on_config(self, config):
        """
        The initial configuration: store the configuration in properties
        """
        # the full config info for the plugin is there
        # we copy it into our own variable, to keep it accessible
        self._full_config = config
        # here we use the standard self.config property:
        # (this can get confusing...)
        self._mermaid_args = self.config["arguments"]
        assert isinstance(self.mermaid_args, dict)
        info("Initialization arguments:", self.mermaid_args)

    def on_post_page(self, output_content, config, page, **kwargs):
        """
        Actions for each page: generate the HTML code for all code items marked as 'mermaid'
        """
        if "mermaid" not in output_content:
            # Skip unecessary HTML parsing
            return output_content

        soup = BeautifulSoup(output_content, "html.parser")
        page_name = page.title
        # first, determine if the page has diagrams:
        pre_code_tags = soup.select("pre.mermaid code") or soup.select("pre.language-mermaid code")
        number_found = len(pre_code_tags)

        if number_found:
            info(
                "Page '{0}': found {1} diagrams (with <pre='mermaid'><code>), converting to <div>...".format(
                    page_name, number_found
                )
            )
            for tag in pre_code_tags:
                content = tag.get_text()  # tag.text
                new_tag = soup.new_tag("div", attrs={"class": "mermaid"})
                new_tag.append(content)
                # replace the parent:
                tag.parent.replaceWith(new_tag)
        
        # Count the diagrams <div class = 'mermaid'> ... </div>
        number_of_diagrams = len(soup.select("div.mermaid"))
    
        # if yes, add the javascript snippets:
        if number_of_diagrams:
            info(
                "Page '{0}': found {1} diagrams, adding scripts".format(
                    page_name, number_of_diagrams
                )
            )
            new_tag = soup.new_tag("script")
            # initialization command
            js_args = pyjs.dumps(self.mermaid_args)
            new_tag.string = "mermaid.initialize({0});".format(js_args)
            soup.body.append(new_tag)
        return str(soup)
