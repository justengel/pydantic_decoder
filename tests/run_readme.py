

def run_readme1():
    from pydantic_decoder import DecoderModel, encode, decode


    class MyModel(DecoderModel):
        first_name: str
        last_name: str


    class Person(DecoderModel):
        first_name: str
        last_name: str
        dob: str = None


    model = MyModel(first_name='John', last_name='Doe')
    msg = model.json()
    m = model.decode(msg)
    assert m == model
    assert isinstance(m, MyModel)

    # Call generic encode and decode without knowledge of the class.
    john = Person(first_name='John', last_name='Doe', dob='11/11/2021')
    msg = encode(john)
    p = decode(msg)
    assert john == p
    assert isinstance(p, Person)

    msg = encode(model)
    m = decode(msg)
    assert m == model
    assert isinstance(m, MyModel)


def run_readme2():
    from pydantic_decoder import DecoderModel, register_model, encode, decode

    class MyModel(DecoderModel):
        first_name: str
        last_name: str

    class MyModel2(DecoderModel):
        first_name: str
        last_name: str


    # Subclasses of the DecoderModel are registered automatically
    # register_model(MyModel)
    # register_model('Model2', MyModel2)

    model = MyModel(first_name='John', last_name='Doe')
    msg = encode(model)
    m = decode(msg)
    assert m == model
    assert isinstance(m, MyModel)

    model2 = MyModel2(first_name='John', last_name='Doe')
    msg = encode(model2)
    m2 = decode(msg)
    assert m2 == model2
    assert isinstance(m2, MyModel2)


if __name__ == '__main__':
    run_readme1()
    run_readme2()

    print('All tests finished successfully!')
