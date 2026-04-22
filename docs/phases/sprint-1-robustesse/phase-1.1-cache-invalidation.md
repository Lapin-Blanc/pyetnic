# Phase 1.1 — Cache invalidation on Config change (D1)

## Context

Read first:

- `CLAUDE.md`
- `docs/AUDIT.md` — section **D1**
- `docs/BACKWARDS_COMPAT.md`
- `plan.md`

This is the first phase of **Sprint 1 — Robustness**. It addresses defect **D1** from the audit: the SOAP client cache is keyed only by `service_name`, so a runtime change to `Config.ENV` or `Config.USERNAME` is silently ignored — the next call returns a stale cached client pointing at the previous environment.

This phase is independent from phase 1.2. It can be done first or in parallel.

## Objective

Make the SOAP client cache invalidate automatically when the relevant Config attributes change, so that `Config.ENV = "prod"` followed by a SOAP call always reaches the prod endpoint with prod credentials.

## Tasks

### 1. Read the current cache implementation

Open `pyetnic/soap_client.py` and locate `SoapClientManager._client_cache`. Note that:

- The cache is a class-level dict
- The cache key is just `self.service_name`
- The cache stores zeep `service` objects (not the full `Client`)
- There's no invalidation mechanism

### 2. Design the cache key

The cache must be sensitive to anything that affects which SOAP client is built. Today, the relevant inputs are:

- `service_name` (already in the key)
- `Config.ENV` — determines endpoint URL and SSL verification
- `Config.USERNAME` — embedded in the WSSE token
- `Config.PASSWORD` — embedded in the WSSE token (but using it in the cache key would be bad practice — see below)

**Decision**: use `(service_name, Config.ENV, Config.USERNAME)` as the cache key. Do NOT include the password in the key, for two reasons:

1. Passwords don't belong in cache keys (potential for accidental logging)
2. If the username is unchanged but the password is, that's a credential rotation scenario — the user will explicitly want to re-initialize anyway, and they can do so via `SoapClientManager.reset_cache()` (see task 3)

### 3. Implement the new cache

Modify `SoapClientManager._initialize_client` to compute the cache key dynamically:

```python
def _cache_key(self) -> tuple:
    """Compute the current cache key based on Config state.
    
    Sensitive to ENV and USERNAME changes so that runtime reconfiguration
    invalidates the cached client automatically.
    """
    return (self.service_name, Config.ENV, Config.USERNAME)

def _initialize_client(self):
    key = self._cache_key()
    if key in self._client_cache:
        return self._client_cache[key]
    
    # ... existing client construction logic ...
    
    self._client_cache[key] = service
    return service
```

Note that the cache is still class-level (shared across instances of `SoapClientManager`), which is fine — different instances of the same service should still share clients when their config matches.

### 4. Add an explicit reset method

```python
@classmethod
def reset_cache(cls) -> None:
    """Clear the entire SOAP client cache.
    
    Useful for tests, for credential rotations, or when integration code
    needs to force re-initialization of all clients.
    """
    cls._client_cache.clear()
```

### 5. Decide what to do with old cached entries

After the change, the cache may accumulate entries for old `(env, username)` combinations that are no longer used. For a typical script that uses one env throughout, this is fine — at most a handful of entries. For long-running processes that switch envs frequently, it could grow.

**Decision for Sprint 1**: don't worry about it. The cache will be small in practice. Document the consideration in a comment for future reference, but don't implement LRU eviction or similar.

```python
# NOTE: cache may accumulate entries if (ENV, USERNAME) changes frequently
# in long-running processes. Acceptable for typical usage. If this becomes
# a problem, consider LRU eviction or explicit reset_cache() calls.
_client_cache: dict[tuple, Any] = {}
```

### 6. Write the regression tests

Add a new file `tests/regression/test_cache_invalidation.py` (or add to an existing file if more appropriate) covering:

**Test A — minimal**: invalidation produces a new client object on env change.

```python
import pytest
from pyetnic.config import Config
from pyetnic.soap_client import SoapClientManager


@pytest.fixture
def reset_soap_cache():
    """Ensures each test starts with an empty cache."""
    SoapClientManager.reset_cache()
    yield
    SoapClientManager.reset_cache()


def test_cache_returns_same_client_when_config_unchanged(reset_soap_cache):
    """Calling _initialize_client twice with the same Config returns the same object."""
    Config.ENV = "dev"
    Config.USERNAME = "user_a"
    Config.PASSWORD = "pass_a"
    
    mgr = SoapClientManager("ORGANISATION")
    client1 = mgr._initialize_client()
    client2 = mgr._initialize_client()
    
    assert client1 is client2  # cache hit


def test_cache_invalidates_on_env_change(reset_soap_cache):
    """Changing Config.ENV produces a new client object."""
    Config.ENV = "dev"
    Config.USERNAME = "user_a"
    Config.PASSWORD = "pass_a"
    
    mgr = SoapClientManager("ORGANISATION")
    client_dev = mgr._initialize_client()
    
    Config.ENV = "prod"
    client_prod = mgr._initialize_client()
    
    assert client_dev is not client_prod  # different objects, no false cache hit


def test_cache_invalidates_on_username_change(reset_soap_cache):
    """Changing Config.USERNAME produces a new client object."""
    Config.ENV = "dev"
    Config.USERNAME = "user_a"
    Config.PASSWORD = "pass_a"
    
    mgr = SoapClientManager("ORGANISATION")
    client_a = mgr._initialize_client()
    
    Config.USERNAME = "user_b"
    client_b = mgr._initialize_client()
    
    assert client_a is not client_b
```

**Test B — endpoint inspection**: prove that the new client points at the right endpoint.

This test inspects zeep's internal binding state, which is more brittle but proves correctness. Locate the binding address via `client._binding_options['address']` or equivalent — verify with `dir()` or by reading the zeep source if needed. Acceptable equivalents:

- `service._binding_options['address']`
- `service._binding._operations[<op_name>].operation.binding.url`
- Anything else that reveals the actual endpoint URL

```python
def test_cache_invalidation_uses_correct_endpoint(reset_soap_cache):
    """After env change, the new client targets the new environment's endpoint."""
    Config.ENV = "dev"
    Config.USERNAME = "user"
    Config.PASSWORD = "pass"
    
    mgr = SoapClientManager("ORGANISATION")
    client_dev = mgr._initialize_client()
    dev_address = client_dev._binding_options['address']
    assert "tq" in dev_address or "-tq" in dev_address  # dev endpoint marker
    
    Config.ENV = "prod"
    client_prod = mgr._initialize_client()
    prod_address = client_prod._binding_options['address']
    assert "tq" not in prod_address and "-tq" not in prod_address  # prod endpoint
```

If the inspection API differs from `_binding_options['address']`, adapt the test but keep the spirit: assert that the actual URL changes.

### 7. Verify all existing regression tests still pass

```bash
pytest tests/regression/ -v
pytest tests/unit/ -v
```

The cache invalidation change is mechanically transparent to callers — old tests should not require any update. If any test breaks, investigate before proceeding (it likely means the test was relying on cached state from another test, which is itself a bug to fix).

## Constraints

- **Do not change any public API** — this is a pure internal fix.
- **Do not touch the SEPS X509 path** — the cache logic must work for both auth types unchanged.
- **No new dependencies.**
- **Backwards-compatible** in the sense that all existing callers see no change in behavior — they only get the bug fix.

## Validation

Before completing, verify:

- [ ] `pytest tests/regression/test_cache_invalidation.py -v` passes
- [ ] `pytest tests/regression/ tests/unit/ -v` — total green count increased by exactly the number of new tests added (probably 4)
- [ ] Quick manual smoke test in a Python REPL:
  ```python
  from pyetnic.config import Config
  from pyetnic.soap_client import SoapClientManager
  Config.ENV = "dev"
  Config.USERNAME = "x"
  Config.PASSWORD = "y"
  mgr = SoapClientManager("ORGANISATION")
  c1 = mgr._initialize_client()
  Config.ENV = "prod"
  c2 = mgr._initialize_client()
  print("Different:", c1 is not c2)  # should print True
  ```
- [ ] CI green on push

## Next

Update `plan.md`: mark Phase 1.1 as complete with the date. Commit message:

```
fix(sprint-1): phase 1.1 — invalidate SOAP cache on Config changes (D1)

- Cache key now includes (service_name, Config.ENV, Config.USERNAME)
- Add SoapClientManager.reset_cache() classmethod for explicit invalidation
- Add 4 regression tests covering same-config, env change, username change,
  and endpoint correctness after invalidation

Closes audit defect D1.
```

Next phase: **Phase 1.2 — Create EPROM exception hierarchy**.
