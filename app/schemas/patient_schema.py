from marshmallow import Schema, fields, validate

class PatientCreateSchema(Schema):
    name = fields.Str(required=True, validate=validate.Length(min=1, max=100))
    age = fields.Int(required=True, validate=validate.Range(min=17, max=45))
    pregnancy_icd10 = fields.Str(validate=validate.Length(max=20), missing=None)
    pregnancy_description = fields.Str(missing=None)
    comorbidity_icd10 = fields.Str(validate=validate.Length(max=20), missing=None)
    comorbidity_description = fields.Str(missing=None)
    weeks_pregnant = fields.Int(validate=validate.Range(min=1, max=42), missing=None)
    address = fields.Str(missing=None)
    zip_code = fields.Str(required=True, validate=validate.Length(min=1, max=20))
    phone_number = fields.Str(validate=validate.Length(max=20), missing=None)
    email = fields.Email(missing=None)
    medications = fields.Str(missing=None)
    medication_notes = fields.Str(missing=None)
    ndc_codes = fields.Str(missing=None)
    between_17_35 = fields.Bool(missing=False)
    
    # Backward compatibility fields
    conditions_icd10 = fields.List(fields.Str(), missing=[])
    trimester = fields.Int(validate=validate.OneOf([1, 2, 3]), missing=None)

class PatientUpdateSchema(Schema):
    name = fields.Str(validate=validate.Length(min=1, max=100))
    age = fields.Int(validate=validate.Range(min=17, max=45))
    pregnancy_icd10 = fields.Str(validate=validate.Length(max=20))
    pregnancy_description = fields.Str()
    comorbidity_icd10 = fields.Str(validate=validate.Length(max=20))
    comorbidity_description = fields.Str()
    weeks_pregnant = fields.Int(validate=validate.Range(min=1, max=42))
    address = fields.Str()
    zip_code = fields.Str(validate=validate.Length(min=1, max=20))
    phone_number = fields.Str(validate=validate.Length(max=20))
    email = fields.Email()
    medications = fields.Str()
    medication_notes = fields.Str()
    ndc_codes = fields.Str()
    between_17_35 = fields.Bool()
    
    # Backward compatibility fields
    conditions_icd10 = fields.List(fields.Str())
    trimester = fields.Int(validate=validate.OneOf([1, 2, 3]))

class PatientResponseSchema(Schema):
    id = fields.Int()
    name = fields.Str()
    age = fields.Int()
    pregnancy_icd10 = fields.Str()
    pregnancy_description = fields.Str()
    comorbidity_icd10 = fields.Str()
    comorbidity_description = fields.Str()
    weeks_pregnant = fields.Int()
    address = fields.Str()
    zip_code = fields.Str()
    phone_number = fields.Str()
    email = fields.Str()
    medications = fields.Str()
    medication_notes = fields.Str()
    ndc_codes = fields.Str()
    between_17_35 = fields.Bool()
    medications_list = fields.List(fields.Str())  # Parsed medications list
    ndc_codes_list = fields.List(fields.Str())  # Parsed NDC codes list
    is_high_risk_age = fields.Bool()  # Calculated from between_17_35
    conditions_icd10 = fields.List(fields.Str())  # For backward compatibility
    trimester = fields.Int()  # Calculated from weeks_pregnant
    created_at = fields.DateTime()
    updated_at = fields.DateTime()
