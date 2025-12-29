from mainApp.routes import db
from mainApp import logger

class Dashboard(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    panelType = db.Column(db.String())
    panelItemId = db.Column(db.Integer())
    panelLocation = db.Column(db.String())
    panelName = db.Column(db.String())
    panelCode = db.Column(db.String())
    panelBackground = db.Column(db.String())
    panelStatus = db.Column(db.String(), default='Active')   


    def __init__(self, panelType, panelItemId, panelLocation, panelName, panelCode, panelStatus='Active', panelBackground=''):
        self.panelType = panelType
        self.panelItemId = panelItemId      
        self.panelLocation = panelLocation
        self.panelName = panelName
        self.panelCode = panelCode
        self.panelBackground = panelBackground
        self.panelStatus = panelStatus
        
class DashboardLister():
    def __init__(self):
        self.dashboards = []
        try:
            self.dashboards = Dashboard.query.all()
        except Exception as e:
            logger.error(f"An error occurred while fetching dashboards: {e}")
    def get_list(self):
        return self.dashboards
    
    
class DashboardAdder():
    def __init__(self, formData: dict) -> None:
        self.message = 'Dashboard panel added'
        logger.info("Adding Dashboard panel to DB")

        try:
            panelType = formData["panelType"][0]
            panelItemId = formData["panelItemId"][0]
            panelLocation = formData["panelLocation"][0]
            panelName = formData["panelName"][0]
            panelCode = formData["panelCode"][0]
            panelStatus = formData["panelStatus"][0]
            panelBackground = formData["panelBackground"][0]

            new_dashboard = Dashboard(
                panelType=panelType,
                panelItemId=panelItemId,
                panelLocation=panelLocation,
                panelName=panelName,
                panelCode=panelCode,
                panelStatus=panelStatus,
                panelBackground=panelBackground
            )
            db.session.add(new_dashboard)
            db.session.commit()
            logger.info("Dashboard panel added successfully")
        except Exception as e:
            db.session.rollback()
            self.message = 'Error adding dashboard panel'
            logger.error(f"An error occurred while adding dashboard panel: {e}")   
    def __str__(self) -> str:
        return self.message
    
class DashboardManager():
    def __init__(self, id):
        self.id = id
        self.message = ""
        self.event = Dashboard.query.filter_by(id=self.id).first()
        
    def remove_dashboard(self):
        if self.event:
            db.session.delete(self.event)
            db.session.commit()
            logger.info(f'Dashboard with ID {self.id} removed')
            self.message = f'Dashboard with ID {self.id} removed'
        else:
            logger.error(f'Dashboard with ID {self.id} does not exist')
            self.message = f'Dashboard with ID {self.id} does not exist'
    
    def edit_dashboard(self, formData: dict):
        if self.event:
            try:
                self.event.panelType = formData["panelType"][0]
                self.event.panelItemId = formData["panelItemId"][0]
                self.event.panelLocation = formData["panelLocation"][0]
                self.event.panelName = formData["panelName"][0]
                self.event.panelCode = formData["panelCode"][0]
                self.event.panelStatus = formData["panelStatus"][0]
                self.event.panelBackground = formData["panelBackground"][0]
                db.session.commit()
                self.message = f"Dashboard with ID {self.id} successfully updated"
                logger.info(self.message)
            except Exception as e:
                db.session.rollback()
                self.message = f"An error occurred while updating dashboard: {e}"
                logger.error(self.message)
        else:
            self.message = f'Dashboard with ID {self.id} does not exist'
            logger.error(self.message)
            
    def change_status(self):
        if self.event:
            if self.event.panelStatus == 'Ready':
                self.event.panelStatus = 'Not ready'
                self.message = "Dashboard status changed to: Not ready"
                logger.info(f'Dashboard with ID {self.id} status changed')
            elif self.event.panelStatus == 'Not ready':
                self.event.panelStatus = 'Ready'
                logger.info(f'Dashboard with ID {self.id} status changed')
                self.message = "Dashboard status changed to: Ready"
            else:
                logger.info(f'Dashboard with ID {self.id} status error')
                self.message = "Status error!"
            db.session.commit()
        else:
            logger.error(f'Dashboard with ID {self.id} does not exist')
            self.message = f'Dashboard with ID {self.id} does not exist'
        
    def __str__(self) -> str:
        return self.message 