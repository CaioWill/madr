import factory

from madr.models import User


class UserFactory(factory.Factory):
    class Meta:
        model = User

    username = factory.Sequence(lambda n: f'test{n}')

    # ele e greado depois dos outros campos
    # o lazy puxa o objeto
    email = factory.LazyAttribute(lambda obj: f'{obj.username}@test.com')

    password = factory.LazyAttribute(lambda obj: f'@{obj.username}#')
