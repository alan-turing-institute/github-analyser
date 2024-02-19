from github_analyser.utils import camel_to_snake


def test_camel_to_snake():
    camel = "camelCase"
    snake = "camel_case"
    assert camel_to_snake(camel) == snake
