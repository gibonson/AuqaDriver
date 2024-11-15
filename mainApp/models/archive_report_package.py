from mainApp.routes import db
from mainApp import logger


class ArchiveFunctions(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String())
    description = db.Column(db.String())
    archiveReportIds = db.Column(db.String())
    eventStatus = db.Column(db.String())

    def __init__(self, title, description, archiveReportIds, eventStatus):
        self.title = title
        self.description = description
        self.archiveReportIds = archiveReportIds
        self.eventStatus = eventStatus
        

class ArchiveFunctionsLister():
    def __init__(self):
        try:
            self.archiveFunctions = ArchiveFunctions.query.all()
        except Exception as e:
            logger.error(f"An error occurred while fetching ArchiveFunctions: {e}")
            self.archiveFunctions = []
    def get_list(self):
        return self.archiveFunctions
    

class ArchiveFunctionsAdder():
    def __init__(self, formData: dict):
        self.message = 'ArchiveFunctions added'
        logger.info("Adding ArchiveFunctions to DB")
        
        try:
            title = formData["title"][0]
            description = formData["description"][0]
            archiveReportIds = formData["archiveReportIds"]
            eventStatus = formData["eventStatus"][0]
            archive_function_to_add = ArchiveFunctions(title=title, description=description, archiveReportIds=str(archiveReportIds), eventStatus=eventStatus)
            db.session.add(archive_function_to_add)
            db.session.commit()
        except Exception as e:
            logger.error(f"An error occurred: {e}")
            self.message = "Error: ArchiveFunctions could not be added"
    def __str__(self) -> str:
        return self.message