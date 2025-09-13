# Linter Rule Definition: SCRAPERSKY-E102 - Enum Comparison and Assignment Bug Prevention
# This rule prevents the enum comparison bug that has repeatedly broken the codebase

RULE_ID = "SCRAPERSKY-E102"
RULE_MESSAGE = """
CRITICAL: SQLAlchemy enum comparison/assignment without .value

You MUST use .value when comparing or assigning enum values in SQLAlchemy operations:
- WRONG: Model.enum_field == MyEnum.Value
- RIGHT: Model.enum_field == MyEnum.Value.value
- WRONG: model.enum_field = MyEnum.Value
- RIGHT: model.enum_field = MyEnum.Value.value

This bug causes: "operator does not exist: enum_type = customenumtype" PostgreSQL errors

War Stories documenting this failure pattern:
- WAR_STORY__Enum_Implementation_Train_Wreck__2025-09-12.md
- Contact router enum filter bug (2025-09-13)

NO EXCEPTIONS. Always use .value for database operations.
"""

# ENUM TYPES TO WATCH FOR (based on src/models/enums.py)
ENUM_TYPES = {
    'ContactCurationStatus',
    'ContactProcessingStatus',
    'ContactEmailTypeEnum',
    'HubSpotSyncStatus',
    'HubSpotProcessingStatus',
    'SitemapCurationStatusEnum',
    'SitemapAnalysisStatusEnum',
    'SitemapImportCurationStatusEnum',
    'PageTypeEnum',
    'PageCurationStatusEnum',
    'LocalBusinessCurationStatusEnum'
}

def check_enum_comparison_without_value(node):
    """
    Detect SQLAlchemy enum comparisons without .value
    Pattern: Model.enum_field == EnumType.VALUE (missing .value)
    """
    if (hasattr(node, 'op') and
        hasattr(node, 'left') and hasattr(node, 'right') and
        hasattr(node.right, 'attr') and
        hasattr(node.right, 'value') and
        hasattr(node.right.value, 'id')):

        # Check if right side is EnumType.VALUE (without .value)
        if (node.right.value.id in ENUM_TYPES and
            not hasattr(node.right, 'attr') or node.right.attr != 'value'):
            yield violation(node, RULE_ID, RULE_MESSAGE)

def check_enum_assignment_without_value(node):
    """
    Detect SQLAlchemy enum assignments without .value
    Pattern: model.enum_field = EnumType.VALUE (missing .value)
    """
    if (hasattr(node, 'value') and
        hasattr(node.value, 'attr') and
        hasattr(node.value, 'value') and
        hasattr(node.value.value, 'id')):

        # Check if assignment value is EnumType.VALUE (without .value)
        if (node.value.value.id in ENUM_TYPES and
            not hasattr(node.value, 'attr') or node.value.attr != 'value'):
            yield violation(node, RULE_ID, RULE_MESSAGE)

def check_filter_append_enum_bug(node):
    """
    Detect the specific pattern: filters.append(Model.field == enum_value)
    This is the exact pattern that broke contacts filtering
    """
    if (hasattr(node, 'func') and
        hasattr(node.func, 'attr') and node.func.attr == 'append' and
        len(node.args) > 0):

        arg = node.args[0]
        if (hasattr(arg, 'right') and
            hasattr(arg.right, 'value') and
            hasattr(arg.right.value, 'id') and
            arg.right.value.id in ENUM_TYPES):
            yield violation(node, RULE_ID, RULE_MESSAGE + "\n\nFOUND: filters.append() with enum comparison bug")

# INTEGRATION NOTE FOR RUFF/FLAKE8:
# This needs to be integrated into the project's linting pipeline
# Add to pyproject.toml or setup.cfg to run with ruff check