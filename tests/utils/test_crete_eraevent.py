from playerstars_interactors.utils.create_era_event import \
    create_era, CreateEraException
from playerstars_domain.utils.datetime_helper import aware_now
from unittest.mock import MagicMock, patch
import pytest


@patch('playerstars_interactors.utils.create_era_event.'
       'EventReminderAssistant')
@patch('playerstars_interactors.utils.create_era_event.'
       'EraAction')
def test_create_era(action, era):
    time = aware_now()
    persist_adapter = MagicMock()
    scheduler_adapter = MagicMock()
    create_era('duel_id', time, 'test/create/era',
               persist_adapter, scheduler_adapter)
    action.assert_called_once_with(url=f'test/create/era/duel_id',
                                   method='POST',
                                   payload={'duel_id': 'duel_id'})
    era.assert_called_once_with(name='finish-duel-duel_id',
                                event_time=time,
                                action=action())
    era().set_adapter.assert_called_once_with(persist_adapter)
    era().set_scheduler_adapter.assert_called_once_with(scheduler_adapter)
    era().save.assert_called_once()


@patch('playerstars_interactors.utils.create_era_event.'
       'EventReminderAssistant', side_effect=Exception('oops'))
@patch('playerstars_interactors.utils.create_era_event.'
       'EraAction')
def test_create_era_raises(action, era):
    time = aware_now()
    persist_adapter = MagicMock()
    scheduler_adapter = MagicMock()
    with pytest.raises(CreateEraException) as excinfo:
        create_era('duel_id', time, 'test/create/era',
                   persist_adapter, scheduler_adapter)
    assert "Error creating era" in str(excinfo.value)
