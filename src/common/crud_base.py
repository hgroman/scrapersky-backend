# src/common/crud_base.py
from fastapi import Query
from typing import Optional, List, Any
from enum import Enum

class SortDirection(str, Enum):
    asc = "asc"
    desc = "desc"

async def get_sorted_filtered_query(
    query,
    model,
    sort: Optional[str] = Query(None, description="Format: column:asc or column:desc or col1:desc,col2:asc"),
    search: Optional[str] = Query(None),
    # add any common filters here
):
    if search:
        # implement your global search logic
        pass
    if sort:
        for part in sort.split(","):
            if ":" in part:
                col, direction = part.strip().split(":")
                if hasattr(model, col):
                    order_col = getattr(model, col)
                    query = query.order_by(order_col.desc() if direction == "desc" else order_col.asc())
    return query
