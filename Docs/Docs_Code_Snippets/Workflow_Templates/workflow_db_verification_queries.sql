-- Check the enum types and their values
SELECT
    t.typname AS enum_name,
    array_agg(e.enumlabel ORDER BY e.enumsortorder) AS enum_values
FROM
    pg_type t
JOIN
    pg_enum e ON t.oid = e.enumtypid
JOIN
    pg_catalog.pg_namespace n ON n.oid = t.typnamespace
WHERE
    n.nspname = 'public' -- Adjust if your enums are in a different schema
    AND t.typtype = 'e' -- Filter for enum types
GROUP BY
    t.typname
ORDER BY
    t.typname;

-- Check the table columns after adding them
SELECT
    column_name,
    data_type,
    is_nullable,
    column_default,
    udt_name -- This shows the specific ENUM type name
FROM
    information_schema.columns
WHERE
    table_schema = 'public'
    AND table_name = '{source_table}'
ORDER BY
    ordinal_position;
