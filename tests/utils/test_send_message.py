from unittest.mock import patch, MagicMock

from playerstars_interactors.utils.message import send_message


@patch('playerstars_interactors.utils.message.boto3')
def test_send_message(mock_boto3):
    result = send_message('msg', 'qname')

    mock_boto3.resource.assert_called_with('sqs')

    mock_sqs = mock_boto3.resource.return_value
    mock_sqs.get_queue_by_name.assert_called_with(QueueName='qname')

    mock_queue = mock_sqs.get_queue_by_name.return_value
    mock_queue.send_message.assert_called_with(MessageBody='msg')

    assert result == mock_queue.send_message.return_value


@patch('playerstars_interactors.utils.message.boto3',
       resource=MagicMock(
           return_value=MagicMock(
               get_queue_by_name=MagicMock(
                   side_effect=ValueError('queue not found')))))
def test_send_message_new_queue(mock_boto3):
    result = send_message('msg', 'new queue')

    mock_boto3.resource.assert_called_with('sqs')

    mock_sqs = mock_boto3.resource.return_value
    mock_sqs.get_queue_by_name.assert_called_with(QueueName='new queue')

    mock_sqs.create_queue.assert_called_with(
        QueueName='new queue',
        Attributes={'ReceiveMessageWaitTimeSeconds': '20'})

    mock_queue = mock_sqs.create_queue.return_value
    mock_queue.send_message.assert_called_with(MessageBody='msg')

    assert result == mock_queue.send_message.return_value
