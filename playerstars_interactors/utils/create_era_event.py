from playerstars_domain import EventReminderAssistant, EraAction
import logging


class CreateEraException(BaseException):
    pass


def create_era(duel_id, event_time, era_finish_duel_url,
               persist_adapter, scheduler_adapter):
    logger = logging.getLogger(__name__)
    try:
        action_url = f'{era_finish_duel_url}/{duel_id}'
        era_action = EraAction(
            url=action_url,
            method='POST',
            payload={'duel_id': duel_id}
        )
        era = EventReminderAssistant(name=f'finish-duel-{duel_id}',
                                     event_time=event_time,
                                     action=era_action)
        era.set_adapter(persist_adapter)
        era.set_scheduler_adapter(scheduler_adapter)
        era.save()
        logger.info(f'Success creating era. era id: {era.entity_id}')
    except Exception as e:
        msg = f'Error creating era event. ' \
            f'Class {e.__class__.__name__} -  Value: {str(e)}'
        logger.error(msg)
        raise CreateEraException(msg)
