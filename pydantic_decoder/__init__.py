import inspect
from typing import Union, Callable, AbstractSet, Mapping, Any, Dict, ClassVar, Optional
from pydantic.main import ModelMetaclass, BaseModel, BaseConfig
from pydantic.parse import load_str_bytes
from pydantic.fields import FieldInfo, ModelField, Undefined, Validator, UndefinedType
from pydantic.typing import NoArgAnyCallable, AnyType, Type

from .__meta__ import version as __version__

IntStr = Union[int, str]
AbstractSetIntStr = AbstractSet[IntStr]
MappingIntStrAny = Mapping[IntStr, Any]
DictStrAny = Dict[str, Any]


__all__ = ['__version__', 'DecoderModelMetaclass', 'DecoderModel', 'encode', 'decode',  # 'field_property',
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


# class field_property(ModelField):
#     __slots__ = (
#         'type_',
#         'outer_type_',
#         'sub_fields',
#         'key_field',
#         'validators',
#         'pre_validators',
#         'post_validators',
#         'default',
#         'default_factory',
#         'required',
#         'model_config',
#         'name',
#         'alias',
#         'has_alias',
#         'field_info',
#         'validate_always',
#         'allow_none',
#         'shape',
#         'class_validators',
#         'parse_json',
#         'fget',
#         'fset',
#         'fdel',
#         )
#
#     def __init__(self, fget=None, fset=None, fdel=None, doc=None,
#                  *,
#                  name: str=None,
#                  type_: AnyType=Any,
#                  class_validators: Optional[Dict[str, Validator]]=None,
#                  model_config: Type['BaseConfig']=None,
#                  default: Any = None,
#                  default_factory: Optional[NoArgAnyCallable] = None,
#                  required: Union[bool, UndefinedType] = Undefined,
#                  alias: str = None,
#                  field_info: Optional[FieldInfo] = None) -> None:
#
#         self.fget = fget
#         self.fset = fset
#         self.fdel = fdel
#
#         if name is None:
#             name = self.fget.__name__
#
#         return_type = inspect.signature(self.fget).return_annotation
#         if type_ == Any and return_type != inspect.Signature.empty:
#             type_ = return_type
#
#         if class_validators is None:
#             class_validators = {}
#
#         if model_config is None:
#             model_config = BaseConfig()
#         super().__init__(name=name, type_=type_, class_validators=class_validators, model_config=model_config,
#                          default=default, default_factory=default_factory, required=required, alias=alias,
#                          field_info=field_info)

# class field_property(FieldInfo):
#     __slots__ = (
#         'default',
#         'default_factory',
#         'alias',
#         'alias_priority',
#         'title',
#         'description',
#         'const',
#         'gt',
#         'ge',
#         'lt',
#         'le',
#         'multiple_of',
#         'min_items',
#         'max_items',
#         'min_length',
#         'max_length',
#         'regex',
#         'extra',
#         'attr',
#         'fget',
#         'fset',
#         'fdel',
#         )
#
#     def __init__(self, fget=None, fset=None, fdel=None,
#                  default: Any = Undefined,
#                  *,
#                  default_factory: Optional[NoArgAnyCallable] = None,
#                  alias: str = None,
#                  title: str = None,
#                  description: str = None,
#                  const: bool = None,
#                  gt: float = None,
#                  ge: float = None,
#                  lt: float = None,
#                  le: float = None,
#                  multiple_of: float = None,
#                  min_items: int = None,
#                  max_items: int = None,
#                  min_length: int = None,
#                  max_length: int = None,
#                  regex: str = None,
#                  **extra: Any) -> None:
#
#         if isinstance(fget, str):
#             self.attr = fget
#             fget = self.internal_getter
#         elif fget is None:
#             self.attr = None
#             fget = self.internal_getter
#         else:
#             self.attr = fget.__name__
#
#         self.fget = fget
#         self.fset = fset
#         self.fdel = fdel
#
#         if default is not Undefined and default_factory is not None:
#             default_factory = inspect.signature(self.fget).return_annotation
#             if default_factory == inspect.Signature.empty:
#                 default = None
#
#         super().__init__(default,
#                          default_factory=default_factory,
#                          alias=alias,
#                          title=title,
#                          description=description,
#                          const=const,
#                          gt=gt,
#                          ge=ge,
#                          lt=lt,
#                          le=le,
#                          multiple_of=multiple_of,
#                          min_items=min_items,
#                          max_items=max_items,
#                          min_length=min_length,
#                          max_length=max_length,
#                          regex=regex,
#                          **extra,)
#
#     def __get__(self, obj, objtype=None):
#         if obj is None:
#             return self
#         if self.fget is None:
#             raise AttributeError("unreadable attribute")
#         return self.fget(obj)
#
#     def __set__(self, obj, value):
#         if self.fset is None:
#             raise AttributeError("can't set attribute")
#         self.fset(obj, value)
#
#     def __delete__(self, obj):
#         if self.fdel is None:
#             raise AttributeError("can't delete attribute")
#         self.fdel(obj)
#
#     @staticmethod
#     def internal_getter(self):
#         try:
#             return getattr(self, self.internal_attr)
#         except AttributeError as err:
#             if self.default != Undefined:
#                 return self.default
#             elif self.default_factory is not None:
#                 return self.default_factory()
#             else:
#                 raise err from err
#
#     def getter(self, fget):
#         self.fget = fget
#         if self.attr is None and self.fget is not None:
#             self.attr = self.fget.__name__
#         return self
#
#     __call__ = getter
#
#     def setter(self, fset):
#         self.fset = fset
#         return self
#
#     def deleter(self, fdel):
#         self.fdel = fdel
#         return self
