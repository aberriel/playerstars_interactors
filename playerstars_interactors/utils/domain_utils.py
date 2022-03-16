class EntityNotFoundException(BaseException):
    pass


def find_entity_by_id(_id, adapter_instance, class_name):
    entity = adapter_instance.get_by_id(_id)
    if not entity:
        raise EntityNotFoundException(
            f'{class_name} {_id} not found')
    entity.set_adapter(adapter_instance)
    return entity
