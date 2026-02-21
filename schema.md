# SnipBox — Database Schema

```mermaid
erDiagram
    USER {
        int id PK
        string username
        string password
        string email
    }

    TAG {
        int id PK
        string title "unique"
    }

    SNIPPET {
        int id PK
        string title
        text note
        datetime created_at
        datetime updated_at
        int user_id FK
    }

    SNIPPET_TAGS {
        int snippet_id FK
        int tag_id FK
    }

    USER ||--o{ SNIPPET : "owns"
    SNIPPET }o--o{ TAG : "linked via SNIPPET_TAGS"
```

## Tables

| Table | Columns | Notes |
|---|---|---|
| `auth_user` | id, username, password, email, ... | Django built-in |
| `snippets_tag` | id, title | `title` is UNIQUE |
| `snippets_snippet` | id, title, note, created_at, updated_at, user_id | `user_id` FK → `auth_user` |
| `snippets_snippet_tags` | snippet_id, tag_id | M2M join table |

## Relationships

- A **User** can own many **Snippets** (one-to-many)
- A **Snippet** can have many **Tags** (many-to-many)
- A **Tag** can be shared across many **Snippets** (tag titles are unique — deduplicated at write time)
