from spatula import HtmlPage, HtmlListPage, CSS, XPath, SelectorError
from pydantic import BaseModel


class Employee(BaseModel):
    first: str
    last: str
    position: str
    marital_status: str
    children: int
    hired: str


class PartialEmployee(BaseModel):
    first: str
    last: str
    position: str


class EmployeeList(HtmlListPage):
    # by providing this here, it can be omitted on the command line
    # useful in cases where the scraper is only meant for one page
    source = "https://yoyodyne-propulsion.herokuapp.com/staff"

    # each row represents an employee
    selector = CSS("#employees tbody tr")

    def process_item(self, item):
        # this function is called for each <tr> we get from the selector
        # we know there are 4 <tds>
        first, last, position, details = item.getchildren()
        return EmployeeDetail(
            dict(
                first=first.text,
                last=last.text,
                position=position.text,
            ),
            source=XPath("./a/@href").match_one(details),
        )

    # pagination
    def get_next_source(self):
        try:
            return XPath("//a[contains(text(), 'Next')]/@href").match_one(self.root)
        except SelectorError:
            pass


class EmployeeDetail(HtmlPage):
    input_type = PartialEmployee

    def process_page(self):
        marital_status = CSS("#status").match_one(self.root)
        children = CSS("#children").match_one(self.root)
        hired = CSS("#hired").match_one(self.root)
        return Employee(
            first=self.input.first,
            last=self.input.last,
            position=self.input.position,
            marital_status=marital_status.text,
            children=children.text,
            hired=hired.text,
        )

    # Error Handling
    def process_error_response(self, exception):
        # every Page subclass has a built-in logger object
        self.logger.warning(exception)
