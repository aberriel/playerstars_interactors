import boto3


# noinspection PyBroadException
def send_message(msg: str, queue_name: str) -> dict:
    sqs = boto3.resource('sqs')
    try:
        q = sqs.get_queue_by_name(QueueName=queue_name)
    except BaseException:
        q = sqs.create_queue(
            QueueName=queue_name,
            Attributes={'ReceiveMessageWaitTimeSeconds': '20'})

    sent_messages = q.send_message(MessageBody=msg)

    return sent_messages
