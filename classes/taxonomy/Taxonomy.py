from classes.data.WpData import WpData
from classes.taxonomy.TermDisplayer import TermDisplayer
from classes.utils.Command import Command
from classes.utils.Print import Print
from classes.utils.Select import Select
from dto.TermDto import TermDto


class Taxonomy:
    terms: list[TermDto] = []

    @classmethod
    def list_all(cls):
        taxonomy = cls.choose_taxonomy()
        if not taxonomy:
            Print.error("No taxonomy selected.")
            return
        cls.init_terms(taxonomy)
        if not cls.terms:
            Print.error(f"No terms found for taxonomy '{taxonomy}'.")
            return
        TermDisplayer.display(f"Terms for '{taxonomy}'", cls.terms)

    @staticmethod
    def choose_taxonomy() -> str | None:
        taxonomies = WpData.get_wp_taxonomies()
        if not taxonomies:
            Print.error("No taxonomies found.")
            return None
        return Select.select_fzf_one(taxonomies)

    @classmethod
    def init_terms(cls, taxonomy: str):
        raw_terms = Command.run_json(
            f"wp term list {taxonomy} --fields=term_id,name,slug --format=json"
        )
        cls.terms = [TermDto(**t) for t in raw_terms]
