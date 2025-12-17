from utils import escape_markdown_v2, CATEGORY_TO_SPEND_TYPE_DEFAULT

class Expenditure:
    def __init__(self, product="", amount="", date="", category=""):
        """Initialize an expenditure object."""
        self.product = product
        self.amount = float(f"{amount:.2f}") if isinstance(amount, (int, float)) else float(amount)
        self.category = category
        self.date = date
        self.spend_type = ""

    def set_spend_type(self):
        if self.category:
            self.spend_type = CATEGORY_TO_SPEND_TYPE_DEFAULT.get(self.category, "")

    def __str__(self):
        return escape_markdown_v2(f"{self.date} - {self.product} ${self.amount:.2f} ({self.category})")