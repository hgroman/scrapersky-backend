# Linter Rule Definition: SCRAPERSKY-E101 - Forbid Legacy PgEnum

RULE_ID = "SCRAPERSKY-E101"
RULE_MESSAGE = """
Legacy `PgEnum` from `sqlalchemy.dialects.postgresql` is forbidden due to a past production incident involving incorrect value serialization.

You MUST use the standard `sqlalchemy.Enum` (as SQLAlchemyEnum) with the mandatory `native_enum=True` and `values_callable` parameters.

See the guide for the correct implementation pattern: /Docs/01_Architectural_Guidance/developer_guides/SCRAPERSKY_DATABASE_DEVELOPER_GUIDE.md
"""

# PSEUDO-CODE FOR LINTER IMPLEMENTATION
# This would be translated into the specific plugin format for ruff or flake8.

def check_for_legacy_pgenum(node):
    """
    Checks an AST import node.
    If `from sqlalchemy.dialects.postgresql import ENUM`, then it's a violation.
    """
    if node.module == "sqlalchemy.dialects.postgresql" and "ENUM" in node.names:
        yield violation(node, RULE_ID, RULE_MESSAGE)

def check_sqlalchemy_enum_usage(node):
    """
    Checks an AST call node for `SQLAlchemyEnum`.
    If `SQLAlchemyEnum` is called without `values_callable` or `native_enum=True`, it's a violation.
    """
    if node.func.id == "SQLAlchemyEnum":
        has_values_callable = False
        has_native_enum = False
        for keyword in node.keywords:
            if keyword.arg == "values_callable":
                has_values_callable = True
            if keyword.arg == "native_enum" and keyword.value.value is True:
                has_native_enum = True
        
        if not has_values_callable or not has_native_enum:
            yield violation(node, RULE_ID, RULE_MESSAGE)
