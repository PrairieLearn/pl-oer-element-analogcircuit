from .circuit_types import Pos, AnalogCircuit, PosTuple
from typing_extensions import NotRequired, get_annotations
from typing import Any, Literal, TypeVar, Annotated, Union, cast, get_args, get_origin, is_typeddict
from types import UnionType

def int_or_float(value: str) -> float | int:
    try:
        return int(value)
    except ValueError:
        return float(value)


def normalize_pos(pos: Pos) -> PosTuple:
    match pos:
        case dict(x=x, y=y):
            return (x, y)
        case [x, y] | (x, y):
            return (x, y)
        case str(s) if s.count(',') == 1:
            x, y = map(int_or_float, s.split(','))
            return (x, y)
        case str(s) if len(s) == 2:
            return (int(s[0]), int(s[1]))
        case str(s):
            raise ValueError(f"invalid position string: {s}")
        case _:
            raise TypeError(f"invalid position type: {type(pos)}")


def parse_circuit(raw_circuit: Any) -> AnalogCircuit:
    return validate(raw_circuit, AnalogCircuit)


T = TypeVar('T')


def validate(instance: Any, type_: type[T]) -> T:
    if not is_typeddict(type_):
        origin = get_origin(type_)
        if origin is None:
            if not isinstance(instance, type_):
                raise ValueError(f"invalid type: expected {type_}, got {type(instance)}")
        elif origin in (UnionType, Union):
            args = get_args(type_)
            for arg in args:
                try:
                    return validate(instance, arg)
                except ValueError:
                    continue
            raise ValueError(f"invalid type: expected one of {args}, got {type(instance)}")
        elif origin is Literal:
            if instance not in get_args(type_):
                raise ValueError(f"invalid value: expected one of {get_args(type_)}, got {instance}")
        elif origin is Annotated:
            return validate(instance, get_args(type_)[0])
        elif origin is dict:
            key_type, val_type = get_args(type_)
            for k, v in instance.items():
                validate(k, key_type)
                validate(v, val_type)
        elif origin is list:
            item_type = get_args(type_)[0]
            for v in instance:
                validate(v, item_type)
        # TODO: handle ellipsis
        # NOTE: this accepts lists and cast them to tuples
        elif origin is tuple:
            item_types = get_args(type_)
            if len(instance) != len(item_types):
                raise ValueError(f"invalid tuple length: expected {len(item_types)}, got {len(instance)}")
            for v, item_type in zip(instance, item_types):
                validate(v, item_type)
            return cast(T, tuple(instance))
        elif origin is set:
            item_type = get_args(type_)[0]
            ret = set()
            len_orig = len(instance)
            for v in instance:
                ret.add(validate(v, item_type))
            if len(ret) != len_orig:
                raise ValueError("invalid set: duplicate items found")
            return cast(T, ret)
        else:
            raise ValueError(f"unsupported type: {type_}")
        return cast(T, instance)

    # Typeddict validation
    annotations = get_annotations(type_)
    for key, annotation in annotations.items():
        is_optional = get_origin(annotation) is NotRequired
        if is_optional:
            annotation = get_args(annotation)[0]

        if key in instance:
            validate(instance[key], annotation)
        elif not is_optional:
            raise ValueError(f"missing required key: {key}")

    return cast(T, instance)
