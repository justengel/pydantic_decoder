

def test_import():
    try:
        from pydantic_decoder import DecoderModelMetaclass, DecoderModel, \
            register_model, remove_model, get_model_name, get_model
        # Normal execution
    except (ImportError, Exception) as err:
        raise AssertionError('Did not import properly') from err


def test_register_model():
    from pydantic_decoder import register_model, get_model_name, get_model

    # ----- Test normal register -----
    class MyModel:
        pass

    register_model('MyModel', MyModel)
    typ = get_model('MyModel')
    assert typ == MyModel

    # ----- Test normal register automatic name -----
    register_model(MyModel)
    typ = get_model(get_model_name(MyModel))
    assert typ == MyModel

    # ----- Test decorator -----
    @register_model
    class MyModel2:
        pass

    typ = get_model(get_model_name(MyModel2))
    assert typ == MyModel2


def test_remove_model():
    from pydantic_decoder import register_model, get_model_name, get_model, remove_model

    class MyModel:
        pass

    # ----- Test Remove by name -----
    register_model('MyModel', MyModel)
    remove_model('MyModel')
    try:
        typ = get_model('MyModel')
        raise AssertionError('The class should not be registered anymore')
    except KeyError:
        pass  # Should hit here

    # ----- Test Remove by Class -----
    register_model('MyModel', MyModel)
    remove_model(MyModel)
    try:
        typ = get_model('MyModel')
        raise AssertionError('The class should not be registered anymore')
    except KeyError:
        pass  # Should hit here

    # ----- Test Remove by default name -----
    register_model(MyModel)
    remove_model(get_model_name(MyModel))
    try:
        typ = get_model(get_model_name(MyModel))
        raise AssertionError('The class should not be registered anymore')
    except KeyError:
        pass  # Should hit here

    # ----- Test Remove by Class with default name -----
    register_model(MyModel)
    remove_model(MyModel)
    try:
        typ = get_model(get_model_name(MyModel))
        raise AssertionError('The class should not be registered anymore')
    except KeyError:
        pass  # Should hit here


def test_metaclass():
    from pydantic_decoder import DecoderModelMetaclass, get_model, get_model_name

    class MyModel(metaclass=DecoderModelMetaclass):
        pass

    try:
        typ = get_model(get_model_name(MyModel))
        # Should be registered
    except (KeyError, Exception) as err:
        raise AssertionError('Metaclass did not register the class') from err


def test_decoder_model():
    from pydantic_decoder import DecoderModel, get_model, get_model_name

    class MyModel(DecoderModel):
        pass

    try:
        typ = get_model(get_model_name(MyModel))
        # Should be registered
    except (KeyError, Exception) as err:
        raise AssertionError('DecoderModel inheritance did not register the class') from err


def test_decoder_model_dict():
    from pydantic_decoder import DecoderModel, get_model, get_model_name

    class MyModel(DecoderModel):
        first_name: str
        last_name: str

    model = MyModel(first_name='John', last_name='Doe')
    d = model.dict()
    assert 'first_name' in d and 'last_name' in d and DecoderModel.DECODER_KEY_NAME in d
    assert d['first_name'] == 'John'
    assert d['last_name'] == 'Doe'
    assert d[DecoderModel.DECODER_KEY_NAME] == get_model_name(MyModel)

    assert DecoderModel.DECODER_KEY_NAME in model.json(), 'json did not use the overridden dict method!'


def test_decoder_model_decode():
    from pydantic.parse import load_str_bytes
    from pydantic_decoder import DecoderModel, get_model, get_model_name

    class MyModel(DecoderModel):
        first_name: str
        last_name: str

    class MyModel2(DecoderModel):
        first_name: str
        last_name: str

    model = MyModel(first_name='John', last_name='Doe')
    m = DecoderModel.decode(model.json())
    assert isinstance(m, MyModel)
    assert m == model

    model2 = MyModel2(first_name='John', last_name='Doe')
    m2 = DecoderModel.decode(model2.json())
    assert isinstance(m2, MyModel2)
    assert m2 == model2


# def test_field_property():
#     from pydantic import BaseModel
#     from pydantic_decoder import DecoderModel, field_property, encode, decode
#
#     class Props(DecoderModel):  # class Props(BaseModel):
#         x: int = field_property('_x', default=0)  # getter is created with '_x'
#
#         @x.setter
#         def x(self, value):
#             self._x = value  # Note: matches field_property('_x')
#
#         y: int = field_property(default=0)
#
#         @y.getter
#         def y(self) -> int:
#             return getattr(self, '_y', 0)
#
#         @y.setter
#         def y(self, value):
#             if isinstance(value, float):
#                 self._x = int(value * 10)
#             self._y = int(value)
#
#         @field_property(default=0)
#         def z(self):
#             return getattr(self, '_z', 0)
#
#         @z.setter
#         def z(self, value):
#             self._z = value
#
#
#     p = Props()
#     print(p)
#     p.x = 2
#     p.y = 1.5
#     print(p)
#
#     msg = encode(p)
#     m = decode(msg)
#     assert m.x == p.x, '{} != {}'.format(m.x, p.x)
#     assert m.y == p.y, '{} != {}'.format(m.y, p.y)
#     assert m.z == p.z, '{} != {}'.format(m.z, p.z)


if __name__ == '__main__':
    test_import()
    test_register_model()
    test_remove_model()
    test_metaclass()
    test_decoder_model()
    test_decoder_model_dict()
    test_decoder_model_decode()

    # test_field_property()

    print('All tests finished successfully!')
