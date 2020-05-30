import inspect
from typing import Union, Callable, AbstractSet, Mapping, Any, Dict, ClassVar
from pydantic.main import ModelMetaclass, BaseModel
from pydantic.parse import load_str_bytes

from .__meta__ import version as __version__

IntStr = Union[int, str]
AbstractSetIntStr = AbstractSet[IntStr]
MappingIntStrAny = Mapping[IntStr, Any]
DictStrAny = Dict[str, Any]


__all__ = ['__version__', 'DecoderModelMetaclass', 'DecoderModel', 'encode', 'decode',
           'get_model_name', 'get_model', 'register_model', 'remove_model']


MODEL_TYPES = {}


def get_model_name(cls: Union[type, object] = None) -> str:
    """Return the model name for the given class."""
    if not inspect.isclass(cls):
        cls = cls.__class__
    return '{}.{}'.format(cls.__module__, cls.__name__)


def get_model(name: str) -> type:
    """Return the model type from the given model name."""
    return MODEL_TYPES[name]


def register_model(name: Union[str, type] = None, cls: type = None) -> Union[type, Callable]:
    """Register the given type for decoding."""
    # Check if class is given as first argument
    if name is not None and not isinstance(name, str):
        cls = name
        name = None

    # Check if decorator needs to be returned
    if cls is None:
        def decorator(cls: type = None):
            return register_model(name, cls)
        return decorator

    # Create a name if needed
    if name is None:
        name = get_model_name(cls)

    # Save the type and return the class (for decorator use)
    MODEL_TYPES[name] = cls
    return cls


def remove_model(cls: Union[str, type]):
    """Remove the type registered with the given name or class type."""
    try:
        # Try removing with string name
        MODEL_TYPES.pop(cls)
    except (KeyError, Exception):
        # Find the model and remove it
        try:
            for k, v in MODEL_TYPES.items():
                if v == cls:
                    MODEL_TYPES.pop(k)
                    break
        except (KeyError, Exception):
            pass


def encode(model: BaseModel) -> str:
    """Convert the given model to a string"""
    return model.json()


def decode(msg: Union[str, bytes]) -> 'BaseModel':
    """Convert the given text to the appropriate pydantic BaseModel."""
    return DecoderModel.decode(msg)


class DecoderModelMetaclass(ModelMetaclass):
    """Metaclass to automatically register every subclass."""
    def __new__(mcs, name, bases, namespace, **kwargs):
        new_cls = super().__new__(mcs, name, bases, namespace, **kwargs)
        register_model(new_cls)
        return new_cls


class DecoderModel(BaseModel, metaclass=DecoderModelMetaclass):
    """Pydantic model that registers every base class so it can be decoded later."""

    DECODER_KEY_NAME: ClassVar = 'DECODER_MODEL_TYPE'

    def dict(
        self,
        *,
        include: Union['AbstractSetIntStr', 'MappingIntStrAny'] = None,
        exclude: Union['AbstractSetIntStr', 'MappingIntStrAny'] = None,
        by_alias: bool = False,
        skip_defaults: bool = None,
        exclude_unset: bool = False,
        exclude_defaults: bool = False,
        exclude_none: bool = False,
    ) -> 'DictStrAny':
        """
        Generate a dictionary representation of the model, optionally specifying which fields to include or exclude.
        """
        d = super().dict(include=include, exclude=exclude, by_alias=by_alias, skip_defaults=skip_defaults,
                         exclude_unset=exclude_unset, exclude_defaults=exclude_defaults, exclude_none=exclude_none)
        d[self.DECODER_KEY_NAME] = get_model_name(self)
        return d

    @classmethod
    def decode(cls, msg: Union[str, bytes]) -> 'BaseModel':
        """Convert the given message into a Pydantic BaseModel"""
        if isinstance(msg, bytes):
            msg = msg.decode('utf-8')

        d = load_str_bytes(msg)  # Dictionary should be returned
        typ = get_model(d.pop(cls.DECODER_KEY_NAME))
        model = typ(**d)
        return model
