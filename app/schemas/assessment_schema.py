from marshmallow import Schema, fields

class AssessmentResponseSchema(Schema):
    id = fields.Int()
    patient_id = fields.Int()
    risk_level = fields.Str()
    heat_wave_risk = fields.Bool()
    risk_factors = fields.Dict()
    risk_score = fields.Int()
    weather_data = fields.Dict()
    assessment_date = fields.DateTime()

class AssessmentCreateSchema(Schema):
    patient_id = fields.Int(required=True)
