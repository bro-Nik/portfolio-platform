"""Architectural guardrails for the API wire contract.

Every model that FastAPI uses to parse a request body or serialize a response
must inherit ApiModel (camelCase over the wire). A BaseModel here means the
endpoint silently speaks snake_case — the exact drift this contract exists to
prevent.
"""

from typing import get_args, get_origin

from fastapi.routing import APIRoute
from pydantic import BaseModel

from app.common.schemas import ApiModel
from app.main import app


def _unwrap(annotation) -> list:
    """Return BaseModel subclasses referenced by an annotation, recursively."""
    found = []

    def visit(node):
        origin = get_origin(node)
        if origin is not None:
            for arg in get_args(node):
                visit(arg)
            return
        if isinstance(node, type) and issubclass(node, BaseModel):
            if node.__module__.startswith(('fastapi.', 'pydantic.')):
                return
            found.append(node)
            for field in node.model_fields.values():
                visit(field.annotation)

    visit(annotation)
    return found


def _iter_routes(routes):
    """Yield APIRoutes across fastapi versions.

    Older fastapi flattens include_router() into app.routes; newer ones wrap
    each included router in an internal object exposing original_router.
    """
    for route in routes:
        if isinstance(route, APIRoute):
            yield route
            continue
        original = getattr(route, 'original_router', None)
        if original is not None:
            yield from _iter_routes(original.routes)
            continue
        nested = getattr(route, 'routes', None)
        if isinstance(nested, list):
            yield from _iter_routes(nested)


def _route_models() -> set[type[BaseModel]]:
    models: set[type[BaseModel]] = set()
    for route in _iter_routes(app.routes):
        if route.response_model is not None:
            models.update(_unwrap(route.response_model))

        for param in route.dependant.body_params:
            models.update(_unwrap(param.field_info.annotation))

    return models


def test_every_wire_model_inherits_api_model():
    offenders = {
        model.__name__: f'{model.__module__}.{model.__qualname__}'
        for model in sorted(_route_models(), key=lambda m: m.__name__)
        if not issubclass(model, ApiModel)
    }
    assert not offenders, 'Wire-facing models must inherit ApiModel (camelCase contract): ' + ', '.join(
        offenders.values()
    )


def test_contract_covers_real_surface():
    routes = list(_iter_routes(app.routes))
    assert len(routes) >= 50, (
        f'Expected the real API surface (~78 endpoints), got {len(routes)} routes — '
        'the guardrail silently stopped matching routes'
    )


def test_openapi_schema_has_no_snake_case_keys():
    """The documented contract is camelCase-only, regardless of parse leniency.

    Every request body and response becomes a component schema, so scanning
    their property names covers the whole wire surface. Enum *values* (e.g.
    tag entity types like 'wallet_asset') are data, not keys, and stay snake.
    """
    import re

    snake = re.compile(r'^[a-z]+(_[a-z]+)+$')
    schemas = app.openapi()['components']['schemas']
    offenders = {
        name: sorted(prop for prop in spec.get('properties', {}) if snake.match(prop)) for name, spec in schemas.items()
    }
    offenders = {name: props for name, props in offenders.items() if props}
    assert not offenders, f'snake_case leaked into the documented contract: {offenders}'
