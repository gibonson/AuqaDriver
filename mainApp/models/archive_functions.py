from mainApp.routes import db


class ArchiveFunctions(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String())
    description = db.Column(db.String())
    archiveReportIds = db.Column(db.String())
    functionStatus = db.Column(db.String())

    def __init__(self, title, description, archiveReportIds, functionStatus):
        self.title = title
        self.description = description
        self.archiveReportIds = archiveReportIds
        self.functionStatus = functionStatus