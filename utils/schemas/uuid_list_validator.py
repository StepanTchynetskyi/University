from marshmallow import Schema, fields, validate


class StudentsUuidListSchema(Schema):
    student_ids = fields.List(
        fields.UUID, required=True, validate=validate.Length(min=1)
    )


class SubjectsUuidListSchemas(Schema):
    subject_ids = fields.List(
        fields.UUID, required=True, validate=validate.Length(min=1)
    )
