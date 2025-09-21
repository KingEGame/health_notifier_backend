from marshmallow import Schema, fields

class NotificationResponseSchema(Schema):
    id = fields.Int()
    patient_id = fields.Int()
    message = fields.Str()
    risk_level = fields.Str()
    notification_type = fields.Str()
    sent_at = fields.DateTime()
    read_status = fields.Bool()
    read_at = fields.DateTime()

class NotificationMarkReadSchema(Schema):
    notification_id = fields.Int(required=True)
