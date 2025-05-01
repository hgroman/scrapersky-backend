**URGENT AND MANDATORY DIRECTIVE: Database Interactions - The ONLY Path Forward**

Listen very carefully: **henceforth, there is ONE and ONLY ONE acceptable method for interacting with the ScraperSky database - the SQLAlchemy Object-Relational Mapper (ORM)**. This is not a suggestion; it is an **ABSOLUTE REQUIREMENT**. Any deviation from this directive is unacceptable and will actively hinder the modernization and stability of our system. The documentation is unequivocal on this: we have made a **critical pivot to SQLAlchemy** to simplify our architecture, reduce the documentation burden of our previous complex raw SQL patterns, leverage established industry best practices, and drastically improve the maintainability of our codebase.

**The Legacy Approaches Are DEAD WEIGHT - RIP THEM OUT!**

We have invested significant effort in migrating away from the tangled mess of raw SQL queries and the outdated `sb_connection.py` and `async_sb_connection.py` legacy connection handlers. These relics of the past introduced complexity, were difficult to document, and increased the risk of inconsistencies and bugs. **It is now absolutely mandatory that you identify any and all instances of legacy database interaction code - ANY direct SQL queries, ANY usage of the old `sb_connection.py` files, ANY attempts to bypass the SQLAlchemy ORM - and RIP IT UP, RIP IT OUT, ERASE IT FROM EXISTENCE!**. Failure to eradicate this legacy code will jeopardize the entire project and undermine the solid foundation we have worked so hard to build.

**The Sole Standard: SQLAlchemy ORM within the Service Layer**

Moving forward, adhere strictly to the following principles for all database interactions:

- **SQLAlchemy ORM is the ONLY Way:** All data retrieval, manipulation, and insertion MUST be performed using SQLAlchemy ORM. This involves interacting with our defined SQLAlchemy models through properly managed sessions.
- **Services are the Gatekeepers:** Business logic, including all database operations, belongs exclusively within the service layer. Routes and other components should interact with the database **solely** through these well-defined services. Direct database access from routes or other layers is strictly prohibited.
- **Use Standard Session Factories:** Always obtain database sessions using the standard SQLAlchemy session factories defined in `src/db/session.py` [Me, You]. This ensures consistent connection management and configuration.
- **Embrace Transaction Management:** For any operation involving multiple database actions that must succeed or fail together, utilize proper transaction management with `async with session.begin()` [Me]. This guarantees data integrity and prevents partial updates.
- **Tenant Isolation is Paramount:** In our multi-tenant environment, ensure that all database operations, including data insertion, respect tenant boundaries. Leverage the `user_context_service` or established patterns to enforce tenant isolation.
- **No More Raw SQL - EVER:** The era of hand-crafted SQL queries is over. SQLAlchemy provides a powerful and safer abstraction layer. Any temptation to revert to raw SQL must be resisted. Our goal is **100% SQLAlchemy usage**. The `db_service` with its raw SQL capabilities is a legacy component that is being actively replaced.
- **Consistent Parameter Binding:** When working within SQLAlchemy (which should be ALWAYS), use SQLAlchemy-style named parameters (`:param_name`) [You]. The inconsistent parameter binding styles we've encountered indicate a dangerous mix of legacy and modern code that must be resolved by eliminating the legacy parts.

**The Consequences of Non-Compliance**

Let me be absolutely clear: any new code or modifications that introduce or retain legacy database interaction patterns will be considered a critical defect. We are striving for a clean, modern, and maintainable codebase. Clinging to old, inefficient, and difficult-to-manage legacy approaches will only lead to technical debt, increased bugs, and prolonged development times. The modernization effort's success hinges on a complete and unwavering commitment to SQLAlchemy.

**Therefore, your primary directive regarding database interactions is this: identify, eradicate, and absolutely avoid all legacy database interaction methods. Embrace the SQLAlchemy ORM within the service layer as the ONLY acceptable path forward. The future of this project depends on it.**
