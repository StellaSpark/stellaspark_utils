from dotenv import load_dotenv
from stellaspark_utils.text import q
from stellaspark_utils.text import sq


load_dotenv()


def test_q():
    assert q(ids="x") == '"x"'
    assert q(ids=["x", "y"]) == q(ids=("x", "y")) == ['"x"', '"y"']


def test_sq():
    assert sq(string="x") == "'x'"
    assert sq(string=["x", "y"]) == ["'x'", "'y'"]
