from functools import lru_cache, partial


class AbstractDescriptorCacheDecorator:

    def __init__(self, func):
        self.func = func
        self.names = []

    def __set_name__(self, owner, name):
        self.names.append(name)

    def store_result(self, instance, result):
        for name in self.names:
            setattr(instance, name, result)


class CachedMethod(AbstractDescriptorCacheDecorator):
    """Cache decorator like ``functools.lru_cache``,
    but applied on each bound method (i.e., in the instance)
    in order to avoid memory leak issues relating to
    caching an unbound method directly from the owner class.
    """
    def __get__(self, instance, owner):
        result = lru_cache(None)(partial(self.func, instance))
        self.store_result(instance, result)
        return result


class CachedProperty(AbstractDescriptorCacheDecorator):
    """Descriptor and also a method decorator, like ``property``,
    where the decorated function gets called only once
    and its result is stored in the instance dictionary afterwards.
    """
    def __get__(self, instance, owner):
        result = self.func(instance)
        self.store_result(instance, result)
        return result
