---
title: Generic Markdown
date: 2026-03-19
tags: [example, tokens]
draft: false
---

# Heading 1

## Heading 2

### Heading 3

#### Heading 4

##### Heading 5

###### Heading 6

Body text with **bold**, _italic_, **_bold italic_**, and ~~strikethrough~~.

Inline `code span` and a [link text](https://example.com "title").

Other url <fake@example.com>

> Blockquote with **bold** inside.
>
> > Level 2 nested.
> >
> > > Level 3.
> > >
> > > > Level 4.
> > > >
> > > > > Level 5.
> > > > >
> > > > > > Level 6 maximum depth.

Example [hobbit-hole][123]

- Level 1
  - Level 2
    - Level 3
      - Level 4
        - Level 5
          - Level 6
- Bullet item 2
- Bullet item 3

1. Ordered item
   1. Nested ordered
      1. Deep ordered
         1. Deeper ordered
            1. Even deeper
               1. Maximum depth
2. Second item
   - Mixed nested
     1. Deep ordered
        - Mixed again

- [x] Done task
- [ ] Pending task

| Name | Type | Default |
| --- | :---: | ---: |
| `host` | string | `localhost` |
| port | number | "5432.123" |

```kotlin
val x = 1
```

```java
@Service
public class UserService {
    private final UserRepository repository;

    public Optional<User> findUser(Long id) {
        if (id == null) {
            throw new IllegalArgumentException("ID must not be null");
        }
        return repository.findById(id);
    }
}
```

```python
from dataclasses import dataclass

@dataclass(frozen=True)
class Config:
    host: str = "localhost"
    port: int = 5432
    debug: bool = False

def connect(config: Config) -> None:
    print(f"Connecting to {config.host}:{config.port}")
```

```typescript
interface User {
  readonly id: string;
  name: string;
}

const greet = (user: User): string => `Hello, ${user.name}!`;
```

```text
some text
some other text
```

---

Image ref: ![alt text](https://placehold.co/15x15/AE8C41/AE8C41.png)

[123]: https://en.wikipedia.org/wiki/Hobbit#Lifestyle
